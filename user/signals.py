from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from authentication.models import Connection
from django.core.cache import cache
from django.db.models import Q

@receiver(post_save,sender=Connection)
def listen_for_save(created,instance,*args, **kwargs):
    if created:
        update_cache(instance)

@receiver(post_delete,sender=Connection)
def listen_for_delete(sender,instance,*args, **kwargs):
    update_cache(instance)

def update_cache(instance):
        connections = Connection.objects.filter(
            Q(sender=instance.sender) | Q(receiver=instance.sender)
        ).values_list(
            'sender_id', 'receiver_id'
        )

        
        connected_user_ids = {
            uid for pair in connections for uid in pair
        }
        # print(connected_user_ids)
        print(instance.sender.id)
        connected_user_ids.discard(instance.sender.id)
        print(f"user_connections_{instance.sender.username}")
        cache.set(f"user_connections_{instance.sender.username}", connected_user_ids)
        