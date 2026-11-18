from django.contrib import admin
from .models import BusinessSettings, Product, Sale, SaleItem, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("email", "full_name")


@admin.register(BusinessSettings)
class BusinessSettingsAdmin(admin.ModelAdmin):
    list_display = ("business_name", "business_type", "kra_pin", "mpesa_till", "vat_rate")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "business_mode", "selling_price", "stock_qty", "is_active")
    list_filter = ("category", "business_mode", "is_active")
    search_fields = ("sku", "name")


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "cashier_name", "payment_method", "total_amount", "created_at")
    list_filter = ("payment_method", "business_type")
    inlines = [SaleItemInline]
