# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-28 22:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_subscription_end'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='strip_id',
            new_name='stripe_id',
        ),
    ]
