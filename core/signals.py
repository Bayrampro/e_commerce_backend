from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import VerificationCode, CustomUser
from .serializers import send_verification_code


@receiver(post_save, sender=CustomUser)
def set_user_inactive(sender, instance, created, **kwargs):
    """

    При создании пользователя он по дефолту не активный,
    генерируются верификационный код и отправляется пользователю
    по указанному эмейлу

    """
    if created:
        if instance.registration_method == 'google':
            instance.is_active = True
            instance.save()
        else:
            instance.is_active = False
            instance.save()
            verification_code = VerificationCode.objects.create(user=instance)
            send_verification_code(instance.email, verification_code.code)
