from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Q
from django.utils import timezone
import uuid

#Model used for basemodel creation
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()

class BaseModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def with_deleted(self):
        return super().get_queryset()

    def only_deleted(self):
        return super().get_queryset().filter(deleted_at__isnull=False)

#CustomUsermanger which can be used when datatable filter all is applied
class CustomUsersManager(BaseModelManager):
    def filter_search(self, qs, search):
        """
        To search from given string in the search box on the datatable.
        """
        if not search: return qs

        q = Q()
        for col in self.model.order_columns:
            if col in ['', 'status']: continue
            if col == 'first_name':
                terms = search.split()
                for term in terms:
                    q = Q(first_name__icontains = term) |  Q(middle_name__icontains = term) | Q(last_name__icontains = term)
            else:
                q |= Q(**{'{0}__istartswith'.format(col.replace('.', '__')): search})

        return qs.filter(q)

    def filter_queryset(self, qs, params):
        qs = self.filter_search(qs, params['search'])
        return qs

class Users(AbstractUser, BaseModel):
    class Meta:
        db_table = '"dashboard_user"'

    USER_TYPE_CHOICES = (
        ('SU', 'Super User'),
        ('A', 'Admin'),
        ('S', 'Supplier'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.SmallIntegerField(default=1)

    columns = ['id', 'first_name', 'username', 'email', 'status']
    order_columns = ['', 'first_name', 'username', 'email', '']

    objects = UserManager()
    filter_objects = CustomUsersManager()

    class Meta(object):
        unique_together = ('email',)
