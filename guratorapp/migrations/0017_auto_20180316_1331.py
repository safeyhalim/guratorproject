# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-16 12:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guratorapp', '0016_personalityquestion_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='personality',
        ),
        migrations.AddField(
            model_name='participant',
            name='personality_accommodating',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='personality_avoiding',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='personality_competing',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='personality_compromising',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='personality_cooperating',
            field=models.IntegerField(default=0),
        ),
    ]