from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.pos_terminal, name="pos_terminal"),
    path("api/checkout/", views.checkout_api, name="checkout_api"),
    path("receipt/<int:sale_id>/", views.receipt_detail, name="receipt_detail"),
    path("inventory/", views.inventory_view, name="inventory"),
    path("staff/", views.staff_view, name="staff"),
    path("reports/", views.reports_view, name="reports"),
    path("reports/csv/", views.export_sales_csv, name="export_sales_csv"),
    path("settings/", views.settings_view, name="settings"),
]
