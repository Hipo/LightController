# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='device',
            name='device_id',
        ),
        migrations.RemoveField(
            model_name='switch',
            name='switch_id',
        ),
        migrations.AddField(
            model_name='device',
            name='device_idx',
            field=models.CharField(default=datetime.datetime(2015, 5, 29, 14, 58, 26, 650888, tzinfo=utc), max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='switch',
            name='switch_idx',
            field=models.CharField(default=datetime.datetime(2015, 5, 29, 14, 58, 34, 53653, tzinfo=utc), max_length=255),
            preserve_default=False,
        ),
    ]
