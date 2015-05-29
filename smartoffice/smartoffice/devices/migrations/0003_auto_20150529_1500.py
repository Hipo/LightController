# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_auto_20150529_1458'),
    ]

    operations = [
        migrations.RenameField(
            model_name='device',
            old_name='device_idx',
            new_name='device_id',
        ),
        migrations.RenameField(
            model_name='switch',
            old_name='switch_idx',
            new_name='switch_id',
        ),
    ]
