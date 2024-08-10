import requests
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.serializers import AllProductSerializer, CategorySerializer, VerifyCodeSerializer, \
    CustomTokenObtainPairSerializer, PasswordResetRequestSerializer, send_verification_code, \
    PasswordResetConfirmSerializer
from e_commerce import settings
from .models import AllProducts, Category, VerificationCode, CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.exceptions import TokenError


class AllProductsList(generics.ListAPIView):
    """

    Список первых шести продуктов по рейтингу

    """
    queryset = AllProducts.objects.order_by('-rating')[0:6]
    serializer_class = AllProductSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )


class ProductDetail(generics.RetrieveAPIView):
    """

    Конкретный продукт по слагу

    """
    serializer_class = AllProductSerializer

    def get_object(self):
        queryset = AllProducts.objects.all()
        filter_kwargs = {'slug': self.kwargs['product_slug']}
        obj = get_object_or_404(queryset, **filter_kwargs)
        return obj


class Search(generics.ListAPIView):
    """

    Поиск продуктов по имени. Регистронезависимый.

    """
    def get_queryset(self):
        query = self.kwargs.get('query')
        query_upper = query[0].upper() + query[1:]
        query_lower = query[0].lower() + query[1:]
        queryset = AllProducts.objects.filter(Q(name__icontains=query_upper) | Q(name__icontains=query_lower))
        return queryset

    serializer_class = AllProductSerializer


class CreatedFilter(generics.ListAPIView):
    """

    Список новинок. Филтруются по created_at

    """
    queryset = AllProducts.objects.order_by('-created_at')[0:8]
    serializer_class = AllProductSerializer


class CategoryDetail(generics.ListAPIView):
    """

    Конкретная категория по слагу.

    """
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        queryset = AllProducts.objects.filter(category__slug=category_slug)
        return queryset

    serializer_class = AllProductSerializer


class CategoryListView(generics.ListAPIView):
    """

    Список категории.

    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CustomTokenRefreshView(TokenRefreshView):
    """

    Кастомное представление которое обновляет не только access токен но и refresh
    это сделано для того чтобы при истечении срока действии refresh токена пользователю
    не надо было занова логинится

    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')

        try:
            token = RefreshToken(refresh_token)
            user_id = token['user_id']  # Получаем user_id из payload

            # Получаем пользователя по user_id
            user = CustomUser.objects.get(id=user_id)

            # Создаем новый refresh-токен для пользователя
            new_refresh = RefreshToken.for_user(user)

            # Генерируем новые токены
            new_access_token = str(new_refresh.access_token)
            new_refresh_token = str(new_refresh)

            return Response({
                'access': new_access_token,
                'refresh': new_refresh_token,
            }, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class VerifyView(generics.GenericAPIView):
    """

    Проверяет отправленный на почту верификационный код.
    Если он правильный и не истек его срок,
    то пользователь становится активным

    """
    serializer_class = VerifyCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']

        try:
            verification_code = VerificationCode.objects.get(code=code)
            user = verification_code.user
            user.is_active = True
            user.save()
            verification_code.delete()
            return Response({'detail': 'User verified successfully'}, status=status.HTTP_200_OK)
        except VerificationCode.DoesNotExist:
            return Response({'detail': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """

    Переопределяем сериализатор для аутентификации с помощью jwt токенов.
    Теперь он дает токены только активным пользователям

    """
    serializer_class = CustomTokenObtainPairSerializer


class PasswordResetRequestView(APIView):
    """

    Представление для запроса на смену пароля пользователя

    """
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            try:
                user = CustomUser.objects.get(username=username, is_active=True)
            except User.DoesNotExist:
                return Response({"error": "User not found or inactive"}, status=status.HTTP_404_NOT_FOUND)

            VerificationCode.objects.filter(user=user).delete()
            reset_code = VerificationCode.objects.create(user=user)
            send_verification_code(user.email, reset_code.code)
            return Response({"message": "Password reset code sent"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """

    Представление для подтверждение на смену пароля пользователя

    """
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']

            try:
                user = CustomUser.objects.get(username=username, is_active=True)
            except User.DoesNotExist:
                return Response({"error": "User not found or inactive"}, status=status.HTTP_404_NOT_FOUND)

            try:
                reset_code = VerificationCode.objects.get(user=user, code=code)
            except VerificationCode.DoesNotExist:
                return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleRegisterView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({"detail": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        user_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(user_info_url, headers=headers)

        if response.status_code != 200:
            return Response({"detail": "Failed to fetch user info from Google"}, status=status.HTTP_400_BAD_REQUEST)

        user_info = response.json()
        email = user_info.get('email')
        name = user_info.get('name')
        if not email:
            return Response({"detail": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        user, created = User.objects.get_or_create(email=email, defaults={'username': name, 'registration_method': 'google'})

        if created:
            user.set_unusable_password()
            user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "detail": "User logged in or registered successfully",
            "access": access_token,
            "refresh": refresh_token
        }, status=status.HTTP_200_OK)