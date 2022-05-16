import uuid
from typing import Optional, Iterable
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords
from django.utils.translation import ugettext_lazy as _  # NOQA
from account.constants import EMAIL_TYPE_CHOICES



class BaseModel(models.Model):
    """More lean base model."""

    datetime_updated = models.DateTimeField(_('Last update at'), auto_now=True)
    datetime_created = models.DateTimeField(_('Created at'), auto_now_add=True)

    objects = models.Manager()

    class Meta:
        """Class meta."""

        abstract = True

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Override save for triggering datetime_updated on update_fields case.

        When using update_fields, the datetime_updated is not updated automatically. This makes sure that it happens.
        """
        listed_for_update_fields = None
        if update_fields:
            listed_for_update_fields = list(update_fields)
            listed_for_update_fields.append('datetime_updated')

        return super().save(force_insert, force_update, using, listed_for_update_fields or None)



class CustomUser(AbstractUser):
    # gender choices
    GENDER_NA = 0
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER = ((GENDER_NA, 'Not Available'), (GENDER_MALE, 'Male'), (GENDER_FEMALE, 'Female'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False) # NOQA (ignore all errors on this line)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=255, default=uuid.uuid4, unique=False)
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    gender = models.IntegerField(choices=GENDER, default=GENDER_NA)
    history = HistoricalRecords()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # type: ignore

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'


class UserEmail(BaseModel):
    # keep track of emails, sent to a user
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT, related_name='user_email')

    email_type = models.IntegerField(choices=EMAIL_TYPE_CHOICES)

    history = HistoricalRecords()

    def __str__(self) -> str:
        """Representation as string."""
        return f'{self.user} - {self.get_email_type_display()}'
