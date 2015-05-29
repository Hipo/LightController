from random import randint
from django.db import models


class Device(models.Model):

    device_id = models.CharField(max_length=255, blank=False, null=False, unique=True)
    name = models.CharField('Device Name', max_length=255, blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.name:
            self.name = 'Device me baby one more time! - %s' % randint(2, 9123)

        super(Device, self).save(force_insert=False, force_update=False, using=None,
             update_fields=None)


class Switch(models.Model):

    switch_id = models.CharField(max_length=255, blank=False, null=False, unique=True)
    name = models.CharField('Switch Name', max_length=255, blank=False, null=False)
    status = models.BooleanField(default=False)
    device = models.ForeignKey(Device, related_name='switches')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.name:
            self.name = 'Switch me baby one more time! - %s' % randint(2, 9123)

        super(Switch, self).save(force_insert=False, force_update=False, using=None,
             update_fields=None)