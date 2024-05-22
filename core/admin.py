from django.contrib import admin

from core.models import Product, Category, Order, Cart, CartItem, User, Address
from custom_user.admin import EmailUserAdmin

from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(EmailUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "phone")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


admin.site.site_header = "Django Ecommerce"
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Address)
