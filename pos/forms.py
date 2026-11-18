from django import forms
from .models import BusinessSettings, Product, User


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "name@business.co.ke"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "sku",
            "name",
            "category",
            "business_mode",
            "buying_price",
            "selling_price",
            "stock_qty",
            "reorder_level",
            "unit",
            "image",
            "is_active",
        ]


class StaffCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), min_length=6)

    class Meta:
        model = User
        fields = ["full_name", "email", "phone", "role", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class BusinessSettingsForm(forms.ModelForm):
    class Meta:
        model = BusinessSettings
        fields = [
            "business_name",
            "business_type",
            "kra_pin",
            "mpesa_till",
            "phone",
            "location",
            "vat_rate",
            "tax_inclusive",
            "receipt_footer",
        ]
