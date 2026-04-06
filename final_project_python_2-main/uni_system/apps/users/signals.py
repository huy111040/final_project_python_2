from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import User


@receiver(post_save, sender=User)
def assign_role_group(sender, instance, created, **kwargs):
    if created:
        role_name = dict(User.ROLE_CHOICES).get(instance.role)
        if role_name:
            group, _ = Group.objects.get_or_create(name=role_name)
            instance.groups.add(group)
