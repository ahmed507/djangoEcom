from allauth.account.adapter import get_adapter
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer, UserModel
from django.contrib.auth import get_user_model
from rest_framework import serializers
from allauth.account.models import EmailAddress
from allauth.account import app_settings as allauth_account_settings

from django.utils.translation import gettext_lazy as _

from core.models import Product, Category, Cart, CartItem, Address, Order, User


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = get_user_model()
#         fields = '__all__'

class ListCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']  # Exclude 'description' field


class RetrieveCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']  # Include 'description' field


class ListProductSerializer(serializers.ModelSerializer):
    categories = RetrieveCategorySerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'picture', 'summary', 'price', 'categories']


class RetrieveProductSerializer(serializers.ModelSerializer):
    categories = RetrieveCategorySerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'picture', 'summary', 'description', 'price', 'categories']


class GetCartItem(serializers.ModelSerializer):
    product = ListProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'price']


class CreateCartSerializer(serializers.ModelSerializer):
    # get current user
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.HiddenField(default='active')

    class Meta:
        model = Cart
        fields = ['user', 'status']

class GetCartSerializer(serializers.ModelSerializer):
    items = GetCartItem(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'status', 'items']


class CreateOrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    quantity = serializers.IntegerField(min_value=1, default=1, read_only=True)

    class Meta:
        model = Order
        fields = ['user', 'products', 'price', 'quantity']


class RetrieveOrderSerializer(serializers.ModelSerializer):
    products = ListProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'price', 'quantity', 'created_at']


class ListOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'price', 'quantity', 'created_at']


class AddItemToCartSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    cart = serializers.HiddenField(default=GetCartSerializer)
    quantity = serializers.IntegerField(min_value=1, default=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    def create(self, validated_data):
        product = validated_data.get('product')
        validated_data['price'] = product.price * validated_data.get('quantity')
        return super().create(validated_data)

    class Meta:
        model = CartItem
        fields = ['cart', 'product', 'quantity', 'price']


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Address
        fields = ['user', 'address', 'city', 'state', 'zip_code']


class UserLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserRegistrationSerializer(RegisterSerializer):
    username = None

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_account_settings.UNIQUE_EMAIL:
            if EmailAddress.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError(_("A user is already registered with this e-mail address."))
        user = get_user_model().objects.filter(email=email)
        if user.exists():
            raise serializers.ValidationError(_("A user is already registered with this e-mail address."))
        return email


class GetUserSerializer(UserDetailsSerializer):
    class Meta:
        extra_fields = []
        # see https://github.com/iMerica/dj-rest-auth/issues/181
        # UserModel.XYZ causing attribute error while importing other
        # classes from `serializers.py`. So, we need to check whether the auth model has
        # the attribute or not
        if hasattr(UserModel, 'USERNAME_FIELD'):
            extra_fields.append(UserModel.USERNAME_FIELD)
        if hasattr(UserModel, 'EMAIL_FIELD'):
            extra_fields.append(UserModel.EMAIL_FIELD)
        if hasattr(UserModel, 'first_name'):
            extra_fields.append('first_name')
        if hasattr(UserModel, 'last_name'):
            extra_fields.append('last_name')
        if hasattr(UserModel, 'phone'):
            extra_fields.append('phone')

        model = UserModel
        fields = ('pk', *extra_fields)
        read_only_fields = ('email',)
