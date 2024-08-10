from django.urls import path, re_path, include
from rest_framework_simplejwt.views import TokenVerifyView
from core.views import *

urlpatterns = [
    path('all-products/', AllProductsList.as_view()),
    path('all-products/<str:product_slug>/', ProductDetail.as_view(), name='product-detail'),
    path('search/<str:query>/', Search.as_view()),
    path('new-products/', CreatedFilter.as_view()),
    path('categories/<str:category_slug>', CategoryDetail.as_view()),
    path('products-by-category/', CategoryListView.as_view(), name='products-by-category'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('auth/verify/', VerifyView.as_view(), name='verify'),
    path('auth/google/', GoogleRegisterView.as_view(), name='google-register'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]