# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0003_auto_20150529_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='device_id',
            field=models.CharField(unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='switch',
            name='switch_id',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
