from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter

from dj_rest_auth.views import (UserDetailsView,LoginView, LogoutView, PasswordChangeView, PasswordResetView,
                                PasswordResetConfirmView)

from core import views

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny,],
)

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'users/me', views.AddressViewSet, basename='address')


urlpatterns = [
    # path('', views.home, name='home'),
    # path('users/', views.GetAllUsersView.as_view(), name='users'),
    # path('api-auth/', include('rest_framework.urls')),
    # path('register', include('dj_rest_auth.registration.urls', namespace='dj_rest_auth.registration')),
    path('auth/login/', LoginView.as_view(), name="user-login"),
    path('auth/logout/', LogoutView.as_view(), name='user-logout'),
    path('auth/password/reset', PasswordResetView.as_view(), name='rest_password_reset'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    # path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    path('users/me/', UserDetailsView.as_view(), name='user-details'),
    path('users/me/change-password/', PasswordChangeView.as_view(), name='rest_password_change'),

    # path('products/',views.GetAllProducts.as_view(),name='products'),
    # path('categories/', views.GetAllCategories.as_view(), name='categories'),
    # path('cart/', views.CreateCartView.as_view(), name='cart'),
    path('', include(router.urls)),

    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]