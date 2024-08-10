from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AllProducts, Category, CustomUser
from djoser.serializers import UserCreateSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для CategoryListView
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class AllProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    """
    
    Сериализатор для AllProductsList
    
    """
    class Meta:
        model = AllProducts
        fields = (
            'id',
            'name',
            'description',
            'price',
            'main_img',
            'img_1',
            'img_2',
            'img_3',
            'img_4',
            'img_5',
            'created_at',
            'rating',
            'category',
            'slug',
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """

    Переопределение для сериализатора создание пользователя в djoser.
    Добавлено поле подтверждение пароля

    """
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        user = super().create(validated_data)
        return user


class VerifyCodeSerializer(serializers.Serializer):
    """

    Сериализатор для VerifyView

    """
    code = serializers.CharField(max_length=6)


def send_verification_code(email, code):
    from django.core.mail import send_mail
    """
    
    Функция для отправки верификационного кода через эмейл
    
    """
    subject = 'Your verification code'
    message = f'Your verification code is {code}'
    from_email = 'your-email@example.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """

    Сериализатор для CustomTokenObtainPairView

    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        try:
            user = CustomUser.objects.get(username=username, is_active=True)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('No active account found with the given credentials')

        if not user.check_password(password):
            raise serializers.ValidationError('No active account found with the given credentials')

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    """

    Сериализатор для PasswordResetRequestView

    """
    username = serializers.CharField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """

    Сериализатор для PasswordResetConfirmView

    """
    username = serializers.CharField()
    code = serializers.CharField()
    new_password = serializers.CharField()