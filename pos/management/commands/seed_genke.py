from decimal import Decimal
from django.core.management.base import BaseCommand
from pos.models import BusinessSettings, Product, User


class Command(BaseCommand):
    help = "Seed initial Kenyan POS data (Admin, Cashier, Staff, Business Settings, and Products)."

    def handle(self, *args, **options):
        BusinessSettings.objects.get_or_create(
            pk=1,
            defaults={
                "business_name": "Savannah Mart & Kitchen",
                "business_type": "retail_shop",
                "kra_pin": "P051842910K",
                "mpesa_till": "5281904",
                "phone": "+254 712 345 678",
                "location": "Kimathi Street, Nairobi",
                "vat_rate": Decimal("16.00"),
                "tax_inclusive": True,
            },
        )

        users = [
            ("admin@gen.ke", "Amara Wanjiku", "admin", "GenkeAdmin2026!", "+254 711 223 344"),
            ("cashier@gen.ke", "Brian Ochieng", "cashier", "GenkeCashier2026!", "+254 722 334 455"),
            ("staff@gen.ke", "Faith Chebet", "staff", "GenkeStaff2026!", "+254 733 445 566"),
        ]
        for email, full_name, role, password, phone in users:
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    full_name=full_name,
                    role=role,
                    password=password,
                    phone=phone,
                    is_staff=(role == "admin"),
                    is_superuser=(role == "admin"),
                )

        products = [
            ("KE-COF-001", "Kenyan AA Coffee 250g", "Beverages", "all", "420.00", "650.00", 42, 10, "pack"),
            ("KE-FLR-002", "Jogoo Maize Flour 2kg", "Pantry Staples", "supermarket", "155.00", "195.00", 85, 20, "pack"),
            ("KE-OIL-003", "Golden Sunflower Oil 1L", "Cooking Essentials", "retail_shop", "260.00", "340.00", 38, 12, "bottle"),
            ("KE-MLK-004", "Brookside Fresh Milk 500ml", "Dairy", "shop", "52.00", "65.00", 64, 15, "carton"),
            ("KE-TEA-005", "Kericho Highland Tea 100g", "Beverages", "all", "140.00", "220.00", 30, 8, "tin"),
            ("KE-RES-006", "Nyama Choma & Ugali Platter", "Hot Kitchen", "restaurant", "450.00", "850.00", 25, 5, "plate"),
        ]
        for sku, name, category, mode, buy, sell, stock, reorder, unit in products:
            Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "category": category,
                    "business_mode": mode,
                    "buying_price": Decimal(buy),
                    "selling_price": Decimal(sell),
                    "stock_qty": stock,
                    "reorder_level": reorder,
                    "unit": unit,
                },
            )

        self.stdout.write(self.style.SUCCESS("Seeded Gen.ke POS database successfully."))
