from django.contrib.auth import get_user_model
from drf_yasg.openapi import Schema, TYPE_OBJECT
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import generics, status, viewsets, views, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet

from core.models import Product, Cart, Category, Order, CartItem, Address
from core.serializers import GetCartSerializer, AddItemToCartSerializer, ListProductSerializer, \
    CreateCartSerializer, ListCategorySerializer, RetrieveCategorySerializer, RetrieveProductSerializer, \
    CreateOrderSerializer, ListOrderSerializer, RetrieveOrderSerializer, AddressSerializer


# class GetAllUsersView(generics.ListAPIView):
#     queryset = get_user_model().objects.all()
#     serializer_class = UserSerializer


# class GetAllProducts(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Product.objects.all()
#     serializer_class = GetProductSerializer


# class GetAllCategories(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Category.objects.all()
#     serializer_class = GetCategorySerializer


class CartViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CreateCartSerializer

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    @swagger_auto_schema(
        methods=['get'],
        operation_id='Get active cart',
        operation_description='Get the active cart of the current user',
        responses={HTTP_200_OK: Schema(type=TYPE_OBJECT, properties={
            'id': Schema(type='integer'),
            'status': Schema(type='string'),
            'items': Schema(type='array', items=Schema(type=TYPE_OBJECT, properties={
                'id': Schema(type='integer'),
                'product': Schema(type='string'),
                'quantity': Schema(type='integer'),
                'price': Schema(type='number'),
            }))
        })}

    )
    @action(detail=False, methods=['get'], url_path='active-cart')
    def get_active_cart(self, request):
        active_cart = Cart.objects.filter(user=request.user, status='active').first()
        if active_cart:
            serializer = GetCartSerializer(active_cart)
            return Response(serializer.data)
        else:
            # create a new cart
            new_cart = Cart.objects.create(user=request.user, status='active')
            return Response(GetCartSerializer(new_cart).data)

    @swagger_auto_schema(
        methods=['post'],
        operation_id='Add item to active cart',
        operation_description='Add an item to the active cart of the current user',
        request_body=AddItemToCartSerializer,
    )
    @action(detail=False, methods=['post'], url_path='add-item')
    def add_item(self, request):
        # add the current user active cart id to the request data and calculate the price
        cart = Cart.objects.filter(user=request.user, status='active').first()
        if cart:
            request.data['cart'] = cart.id
        else:
            cart = Cart.objects.create(user=request.user, status='active')
            request.data['cart'] = cart.id
        request.data['price'] = Product.objects.get(id=request.data['product']).price * request.data['quantity']
        serializer = AddItemToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # check if the item is already in the cart
        if cart.items.filter(product=request.data['product']).exists():
            # update the quantity
            item = cart.items.get(product=request.data['product'])
            item.quantity += request.data['quantity']
            item.price += request.data['price']
            item.save()
            serializer.data['quantity'] = item.quantity
            serializer.data['price'] = item.price
            return Response(serializer.data)

        serializer.save(cart=cart)
        return Response(serializer.data)

    @swagger_auto_schema(
        methods=['post'],
        operation_id='Checkout active cart',
        operation_description='Checkout the active cart of the current user',
        request_body=no_body,
        responses={HTTP_200_OK: Schema(type=TYPE_OBJECT, properties={
            'quantity': Schema(type='integer'),
            'price': Schema(type='number'),
        })}
    )
    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        active_cart = Cart.objects.filter(user=request.user, status='active').first()
        if active_cart:
            active_cart.status = 'ordered'
            active_cart.save()
            # create order
            print(request.user.id)
            serializer = CreateOrderSerializer(data={
                'user': request.user.id,
                'products': [item.product.id for item in active_cart.items.all()],
                'price': sum([item.price for item in active_cart.items.all()]),
                'quantity': sum([item.quantity for item in active_cart.items.all()]),
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'quantity': serializer.instance.quantity, 'price': serializer.instance.price})
        else:
            return Response({'message': 'No active cart'}, status=HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        methods=['delete'],
        operation_id='Delete active cart',
        operation_description='Delete the active cart of the current user',
        request_body=no_body,
    )
    @action(detail=False, methods=['delete'], url_path='delete-cart')
    def abandon(self, request):
        active_cart = Cart.objects.filter(user=request.user, status='active').first()
        if active_cart:
            active_cart.status = 'abandoned'
            active_cart.save()
            return Response({'message': 'Cart deleted'}, status=HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'No active cart'}, status=HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        methods=['delete'],
        operation_id='Delete item from active cart',
        operation_description='Delete an item from the active cart of the current user',
        request_body=Schema(type=TYPE_OBJECT, properties={
            'product': Schema(type='integer'),
        })
    )
    @action(detail=False, methods=['delete'], url_path='delete-item')
    def delete_item(self, request):
        active_cart = Cart.objects.filter(user=request.user, status='active').first()
        if active_cart:
            try:
                item = active_cart.items.get(product=request.data['product'])
                if item:
                    item.delete()
                    return Response({'message': 'Item deleted'}, status=HTTP_204_NO_CONTENT)
                else:
                    return Response({'message': 'Item not found'}, status=HTTP_404_NOT_FOUND)
            except CartItem.DoesNotExist:
                return Response({'message': 'Item not found'}, status=HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'No active cart'}, status=HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        methods=['put'],
        operation_id='Update item in active cart',
        operation_description='Update an item in the active cart of the current user',
        request_body=AddItemToCartSerializer,
    )
    @action(detail=False, methods=['put'], url_path='update-item')
    def update_item(self, request):
        active_cart = Cart.objects.filter(user=request.user, status='active').first()
        if active_cart:
            item = active_cart.items.get(product=request.data['product'])
            item.quantity = request.data['quantity']
            item.price = item.product.price * item.quantity
            item.save()
            return Response({'message': 'Item updated'}, status=HTTP_200_OK)
        else:
            return Response({'message': 'No active cart'}, status=HTTP_404_NOT_FOUND)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ListProductSerializer
        if self.action == 'retrieve':
            return RetrieveProductSerializer
        return super().get_serializer_class()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ListCategorySerializer
        if self.action == 'retrieve':
            return RetrieveCategorySerializer
        return super().get_serializer_class()


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ListOrderSerializer
        if self.action == 'retrieve':
            return RetrieveOrderSerializer
        return super().get_serializer_class()


class AddressViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    @swagger_auto_schema(
        methods=['get'],
        operation_id='Get address',
        operation_description='Get the address of the current user',
        responses={HTTP_200_OK: Schema(type=TYPE_OBJECT, properties={
            'id': Schema(type='integer'),
            'address': Schema(type='string'),
            'city': Schema(type='string'),
            'state': Schema(type='string'),
            'zip_code': Schema(type='string'),
        })}
    )
    @action(detail=False, methods=['get'], url_path='get-address')
    def get_address(self, request):
        address = Address.objects.filter(user=request.user).first()
        if address:
            serializer = AddressSerializer(address)
            return Response(serializer.data)
        else:
            return Response({'message': 'No address found'}, status=HTTP_404_NOT_FOUND)


    @swagger_auto_schema(
        methods=['patch'],
        operation_id='Update address',
        operation_description='Update the address of the current user',
        request_body=AddressSerializer,
        responses={HTTP_200_OK: Schema(type=TYPE_OBJECT, properties={
            'id': Schema(type='integer'),
            'address': Schema(type='string'),
            'city': Schema(type='string'),
            'state': Schema(type='string'),
            'zip_code': Schema(type='string'),
        })}
    )
    @action(detail=False, methods=['patch'], url_path='update-address')
    def update_address(self, request):
        address = Address.objects.filter(user=request.user).first()
        if address:
            serializer = AddressSerializer(address, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'message': 'No address found'}, status=HTTP_404_NOT_FOUND)


    @swagger_auto_schema(
        methods=['delete'],
        operation_id='Delete address',
        operation_description='Delete the address of the current user',
        request_body=no_body,
    )
    @action(detail=False, methods=['delete'], url_path='delete-address')
    def delete_address(self, request):
        address = Address.objects.filter(user=request.user).first()
        if address:
            address.delete()
            return Response({'message': 'Address deleted'}, status=HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'No address found'}, status=HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        methods=['post'],
        operation_id='Create address',
        operation_description='Create an address for the current user',
        request_body=AddressSerializer,
        responses={HTTP_201_CREATED: Schema(type=TYPE_OBJECT, properties={
            'id': Schema(type='integer'),
            'address': Schema(type='string'),
            'city': Schema(type='string'),
            'state': Schema(type='string'),
            'zip_code': Schema(type='string'),
        })}
    )
    @action(detail=False, methods=['post'], url_path='create-address')
    def create_address(self, request):
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)
