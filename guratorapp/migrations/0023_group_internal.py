# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-02 12:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guratorapp', '0022_auto_20180429_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='internal',
            field=models.BooleanField(default=True, verbose_name='Internal group'),
        ),
    ]