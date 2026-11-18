import csv
import json
from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import BusinessSettingsForm, LoginForm, ProductForm, StaffCreateForm
from .models import BusinessSettings, Product, Sale, SaleItem, User


def get_business_settings():
    settings_obj, _ = BusinessSettings.objects.get_or_create(pk=1)
    return settings_obj


def login_view(request):
    if request.user.is_authenticated:
        return redirect("pos_terminal")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user is not None and user.is_active:
            login(request, user)
            return redirect("pos_terminal")
        messages.error(request, "Invalid email or password.")
    return render(request, "login.html", {"form": form, "business": get_business_settings()})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def pos_terminal(request):
    business = get_business_settings()
    products = Product.objects.filter(is_active=True)
    categories = sorted(set(products.values_list("category", flat=True)))
    return render(
        request,
        "pos.html",
        {
            "business": business,
            "products": products,
            "categories": categories,
        },
    )


@login_required
@require_POST
def checkout_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    items = payload.get("items", [])
    if not items:
        return JsonResponse({"error": "Cart cannot be empty."}, status=400)

    business = get_business_settings()
    payment_method = payload.get("payment_method", "mpesa")
    mpesa_ref = (payload.get("mpesa_ref") or "").strip().upper()
    customer_name = (payload.get("customer_name") or "Walk-in Customer").strip()
    customer_phone = (payload.get("customer_phone") or "").strip()
    discount = Decimal(str(payload.get("discount_amount") or "0"))
    tendered = Decimal(str(payload.get("amount_tendered") or "0"))

    with transaction.atomic():
        subtotal = Decimal("0.00")
        resolved_items = []

        for entry in items:
            product = get_object_or_404(Product.objects.select_for_update(), pk=entry["product_id"])
            qty = int(entry["quantity"])
            if qty <= 0:
                return JsonResponse({"error": f"Invalid quantity for {product.name}."}, status=400)
            if product.stock_qty < qty:
                return JsonResponse(
                    {"error": f"Insufficient stock for {product.name}. Available: {product.stock_qty}."},
                    status=400,
                )
            unit_price = Decimal(str(entry.get("unit_price") or product.selling_price))
            line_total = (unit_price * qty).quantize(Decimal("0.01"))
            subtotal += line_total
            resolved_items.append((product, qty, unit_price, line_total))

        net_after_discount = max(Decimal("0.00"), subtotal - discount)
        vat_rate = business.vat_rate / Decimal("100")
        if business.tax_inclusive:
            vat_amount = (net_after_discount - (net_after_discount / (Decimal("1") + vat_rate))).quantize(Decimal("0.01"))
            total_amount = net_after_discount.quantize(Decimal("0.01"))
        else:
            vat_amount = (net_after_discount * vat_rate).quantize(Decimal("0.01"))
            total_amount = (net_after_discount + vat_amount).quantize(Decimal("0.01"))

        if tendered < total_amount:
            tendered = total_amount
        change_given = max(Decimal("0.00"), tendered - total_amount)

        today_prefix = timezone.localtime().strftime("GEN-%Y%m%d")
        count_today = Sale.objects.filter(receipt_number__startswith=today_prefix).count() + 1
        receipt_number = f"{today_prefix}-{count_today:04d}"

        sale = Sale.objects.create(
            receipt_number=receipt_number,
            cashier=request.user,
            cashier_name=request.user.full_name,
            customer_name=customer_name,
            customer_phone=customer_phone,
            business_type=business.business_type,
            payment_method=payment_method,
            mpesa_ref=mpesa_ref,
            subtotal=subtotal,
            vat_amount=vat_amount,
            discount_amount=discount,
            total_amount=total_amount,
            amount_tendered=tendered,
            change_given=change_given,
            notes=payload.get("notes", ""),
        )

        for product, qty, unit_price, line_total in resolved_items:
            SaleItem.objects.create(
                sale=sale,
                product=product,
                product_name=product.name,
                sku=product.sku,
                quantity=qty,
                unit_price=unit_price,
                buying_price=product.buying_price,
                line_total=line_total,
            )
            product.stock_qty = F("stock_qty") - qty
            product.save(update_fields=["stock_qty", "updated_at"])

    return JsonResponse({"sale_id": sale.id, "receipt_number": sale.receipt_number})


@login_required
def receipt_detail(request, sale_id):
    sale = get_object_or_404(Sale.objects.prefetch_related("items"), pk=sale_id)
    return render(request, "receipt.html", {"sale": sale, "business": get_business_settings()})


@login_required
def inventory_view(request):
    business = get_business_settings()
    if request.method == "POST":
        if request.user.role not in ("admin", "staff"):
            messages.error(request, "Only Admin or Staff members can add products.")
            return redirect("inventory")
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, f"Saved {product.name} to inventory.")
            return redirect("inventory")
    else:
        form = ProductForm()

    products = Product.objects.all()
    return render(
        request,
        "inventory.html",
        {"business": business, "products": products, "form": form},
    )


@login_required
def staff_view(request):
    if request.user.role != "admin":
        messages.error(request, "Admin access required to manage staff.")
        return redirect("pos_terminal")

    if request.method == "POST":
        form = StaffCreateForm(request.POST)
        if form.is_valid():
            staff_user = form.save()
            messages.success(request, f"Added staff member {staff_user.full_name}.")
            return redirect("staff")
    else:
        form = StaffCreateForm()

    staff_members = User.objects.all().order_by("-created_at")
    return render(
        request,
        "staff.html",
        {"business": get_business_settings(), "staff_members": staff_members, "form": form},
    )


@login_required
def reports_view(request):
    if request.user.role != "admin":
        messages.error(request, "Admin access required to view sales reports.")
        return redirect("pos_terminal")

    days = int(request.GET.get("days", 30))
    since = timezone.now() - timedelta(days=days)
    sales = Sale.objects.filter(created_at__gte=since)
    totals = sales.aggregate(revenue=Sum("total_amount"), vat=Sum("vat_amount"))
    total_revenue = totals["revenue"] or Decimal("0.00")
    total_vat = totals["vat"] or Decimal("0.00")

    return render(
        request,
        "reports.html",
        {
            "business": get_business_settings(),
            "sales": sales[:50],
            "total_revenue": total_revenue,
            "total_vat": total_vat,
            "transaction_count": sales.count(),
            "days": days,
        },
    )


@login_required
def export_sales_csv(request):
    if request.user.role != "admin":
        return HttpResponse("Forbidden", status=403)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="genke_sales_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Receipt", "Date", "Cashier", "Customer", "Payment", "M-Pesa Ref", "VAT (KES)", "Total (KES)"])
    for sale in Sale.objects.all():
        writer.writerow([
            sale.receipt_number,
            sale.created_at.strftime("%Y-%m-%d %H:%M"),
            sale.cashier_name,
            sale.customer_name,
            sale.payment_method,
            sale.mpesa_ref,
            sale.vat_amount,
            sale.total_amount,
        ])
    return response


@login_required
def settings_view(request):
    if request.user.role != "admin":
        messages.error(request, "Admin access required to customize business settings.")
        return redirect("pos_terminal")
    business = get_business_settings()
    if request.method == "POST":
        form = BusinessSettingsForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            messages.success(request, "Business settings updated.")
            return redirect("settings")
    else:
        form = BusinessSettingsForm(instance=business)
    return render(request, "settings.html", {"business": business, "form": form})
