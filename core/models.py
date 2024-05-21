# from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.utils.translation import gettext_lazy as _
from custom_user.models import AbstractEmailUser


class User(AbstractEmailUser):
    first_name = models.CharField(max_length=255, blank=True, null=True, default='', verbose_name='First Name')
    last_name = models.CharField(max_length=255, blank=True, null=True, default='', verbose_name='Last Name')
    phone = models.CharField(max_length=255, blank=True, null=True, default='', verbose_name='Phone')

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True, default='', verbose_name='Address', help_text='Address')
    city = models.CharField(max_length=255, null=True, blank=True, default='', verbose_name='City', help_text='City')
    state = models.CharField(max_length=255, null=True, blank=True, default='', verbose_name='State', help_text='State')
    zip_code = models.CharField(max_length=255, null=True, blank=True, default='', verbose_name='Zip Code', help_text='Zip Code')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    def __str__(self):
        return self.address


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Name', help_text='Name')
    description = models.TextField(null=True, blank=True, default='', verbose_name='Description', help_text='Description')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At', help_text='Updated At')

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Title', help_text='Title')
    picture = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name='Picture', help_text='Picture')
    summary = models.TextField(null=True, blank=True, verbose_name='Summary', help_text='Summary')
    description = models.TextField(null=True, blank=True, verbose_name='Description', help_text='Description')
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0, verbose_name='Price', help_text='Price')
    categories = models.ManyToManyField(Category, related_name='products', verbose_name='Categories', help_text='Categories')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At', help_text='Updated At')

    def __str__(self):
        return self.title


CART_STATUS = [
    ('active', 'active'),
    ('ordered', 'ordered'),
    ('abandoned', 'abandoned'),
]


class Cart(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name', help_text='Name')
    status = models.CharField(choices=CART_STATUS, max_length=255, default='active', verbose_name='Status', help_text='Status')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', null=True, blank=True, verbose_name='User', help_text='User')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At', help_text='Updated At')

    def __str__(self):
        return self.name


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Cart', help_text='Cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items', verbose_name='Product', help_text='Product')
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0, verbose_name='Price', help_text='Price')
    quantity = models.IntegerField(default=1, verbose_name='Quantity', help_text='Quantity')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At', help_text='Updated At')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At', help_text='Updated At')


class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_lines')
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0, verbose_name='Price', help_text='Price')
    quantity = models.IntegerField(default=1, verbose_name='Quantity', help_text='Quantity')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At', help_text='Updated At')


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Product', help_text='Product')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name='User', help_text='User')
    rating = models.DecimalField(decimal_places=1, max_digits=2, default=0, verbose_name='Rating', help_text='Rating')
    review = models.TextField(null=True, blank=True, verbose_name='Review', help_text='Review')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At', help_text='Updated At')

