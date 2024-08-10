from django_cron import CronJobBase, Schedule
from django.utils import timezone
from core.models import VerificationCode
import logging

logger = logging.getLogger(__name__)


class DeleteExpiredVerificationCodesCronJob(CronJobBase):
    """

    Задача для удаление просроченных верификационных кодов,
    который выполняет линуксовый кронтаб в фоновлм режиме

    """
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'core.delete_expired_verification_codes_cron_job'

    def do(self):
        expired_codes = VerificationCode.objects.filter(expires_at__lt=timezone.now())
        count = expired_codes.count()
        expired_codes.delete()
        logger.info(f'Deleted {count} expired verification codes.')
