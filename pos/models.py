from decimal import Decimal
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, role="staff", **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email=email, full_name=full_name, password=password, role="admin", **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("cashier", "Cashier"),
        ("staff", "Staff"),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=32, blank=True, default="")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"


class BusinessSettings(models.Model):
    BUSINESS_TYPES = [
        ("shop", "Shop / Duka"),
        ("retail_shop", "Retail Shop"),
        ("restaurant", "Restaurant & Kitchen"),
        ("supermarket", "Supermarket"),
    ]

    business_name = models.CharField(max_length=150, default="Savannah Mart & Kitchen")
    business_type = models.CharField(max_length=30, choices=BUSINESS_TYPES, default="retail_shop")
    kra_pin = models.CharField(max_length=30, blank=True, default="P051842910K")
    mpesa_till = models.CharField(max_length=30, blank=True, default="5281904")
    phone = models.CharField(max_length=32, blank=True, default="+254 712 345 678")
    location = models.CharField(max_length=150, blank=True, default="Kimathi Street, Nairobi")
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("16.00"))
    tax_inclusive = models.BooleanField(default=True)
    receipt_footer = models.CharField(
        max_length=255,
        default="Asante kwa kufanya biashara nasi! Goods once sold are not returnable.",
    )
    currency_code = models.CharField(max_length=10, default="KES")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name} ({self.get_business_type_display()})"


class Product(models.Model):
    MODE_CHOICES = [
        ("all", "All Business Modes"),
        ("shop", "Shop / Duka"),
        ("retail_shop", "Retail Shop"),
        ("restaurant", "Restaurant"),
        ("supermarket", "Supermarket"),
    ]

    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=80)
    business_mode = models.CharField(max_length=30, choices=MODE_CHOICES, default="all")
    buying_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_qty = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    unit = models.CharField(max_length=24, default="pcs")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (KES {self.selling_price})"


class Sale(models.Model):
    PAYMENT_METHODS = [
        ("mpesa", "M-Pesa"),
        ("cash", "Cash"),
        ("card", "Card"),
        ("split", "Split"),
    ]

    receipt_number = models.CharField(max_length=40, unique=True)
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cashier_name = models.CharField(max_length=120)
    customer_name = models.CharField(max_length=120, blank=True, default="Walk-in Customer")
    customer_phone = models.CharField(max_length=32, blank=True, default="")
    business_type = models.CharField(max_length=30, default="retail_shop")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="mpesa")
    mpesa_ref = models.CharField(max_length=40, blank=True, default="")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_tendered = models.DecimalField(max_digits=12, decimal_places=2)
    change_given = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.receipt_number} - KES {self.total_amount}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=160)
    sku = models.CharField(max_length=50)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    buying_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
