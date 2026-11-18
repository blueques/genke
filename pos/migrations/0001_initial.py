from decimal import Decimal
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("full_name", models.CharField(max_length=120)),
                ("phone", models.CharField(blank=True, default="", max_length=32)),
                ("role", models.CharField(choices=[("admin", "Admin"), ("cashier", "Cashier"), ("staff", "Staff")], default="staff", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("groups", models.ManyToManyField(blank=True, related_name="user_set", related_query_name="user", to="auth.group")),
                ("user_permissions", models.ManyToManyField(blank=True, related_name="user_set", related_query_name="user", to="auth.permission")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="BusinessSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("business_name", models.CharField(default="Savannah Mart & Kitchen", max_length=150)),
                ("business_type", models.CharField(choices=[("shop", "Shop / Duka"), ("retail_shop", "Retail Shop"), ("restaurant", "Restaurant & Kitchen"), ("supermarket", "Supermarket")], default="retail_shop", max_length=30)),
                ("kra_pin", models.CharField(blank=True, default="P051842910K", max_length=30)),
                ("mpesa_till", models.CharField(blank=True, default="5281904", max_length=30)),
                ("phone", models.CharField(blank=True, default="+254 712 345 678", max_length=32)),
                ("location", models.CharField(blank=True, default="Kimathi Street, Nairobi", max_length=150)),
                ("vat_rate", models.DecimalField(decimal_places=2, default=Decimal("16.00"), max_digits=5)),
                ("tax_inclusive", models.BooleanField(default=True)),
                ("receipt_footer", models.CharField(default="Asante kwa kufanya biashara nasi! Goods once sold are not returnable.", max_length=255)),
                ("currency_code", models.CharField(default="KES", max_length=10)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sku", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=160)),
                ("category", models.CharField(max_length=80)),
                ("business_mode", models.CharField(default="all", max_length=30)),
                ("buying_price", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("selling_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("stock_qty", models.IntegerField(default=0)),
                ("reorder_level", models.IntegerField(default=10)),
                ("unit", models.CharField(default="pcs", max_length=24)),
                ("image", models.ImageField(blank=True, null=True, upload_to="products/")),
                ("is_active", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Sale",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("receipt_number", models.CharField(max_length=40, unique=True)),
                ("cashier_name", models.CharField(max_length=120)),
                ("customer_name", models.CharField(blank=True, default="Walk-in Customer", max_length=120)),
                ("customer_phone", models.CharField(blank=True, default="", max_length=32)),
                ("business_type", models.CharField(default="retail_shop", max_length=30)),
                ("payment_method", models.CharField(choices=[("mpesa", "M-Pesa"), ("cash", "Cash"), ("card", "Card"), ("split", "Split")], default="mpesa", max_length=20)),
                ("mpesa_ref", models.CharField(blank=True, default="", max_length=40)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=12)),
                ("vat_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("discount_amount", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("amount_tendered", models.DecimalField(decimal_places=2, max_digits=12)),
                ("change_given", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("cashier", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="SaleItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_name", models.CharField(max_length=160)),
                ("sku", models.CharField(max_length=50)),
                ("quantity", models.IntegerField()),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("buying_price", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("line_total", models.DecimalField(decimal_places=2, max_digits=12)),
                ("product", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="pos.product")),
                ("sale", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="pos.sale")),
            ],
        ),
    ]
