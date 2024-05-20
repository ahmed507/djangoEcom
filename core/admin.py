from django.contrib import admin

from core.models import Product, Category, Order, Cart,CartItem

admin.site.site_header = "Django Ecommerce"
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(CartItem)