from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import VirtualAccounting, UserProfiles
from .services import PaystackService
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_virtual_account(sender, instance, created, **kwargs):
    if created:
        try:
            paystack_service = PaystackService()
            virtual_account_data = paystack_service.generate_virtual_account(instance)
            VirtualAccounting.objects.create(
                user=instance,
                account_number=virtual_account_data['account_number'],
                bank_name=virtual_account_data['bank']['name'],
                order_ref=virtual_account_data['reference']
            )
        except Exception as e:
            logger.error(f"Failed to create virtual account: {e}")
            
            
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfiles.objects.create(user=instance)
    instance.userprofiles.save()
