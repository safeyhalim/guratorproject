# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-03 14:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import guratorapp.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, verbose_name='Username')),
                ('real_name', models.CharField(max_length=50, verbose_name='Real name')),
                ('email', models.CharField(default='', max_length=500, verbose_name='E-Mail address')),
                ('email2', models.CharField(default='', max_length=500, verbose_name='E-Mail address (confirmation)')),
                ('accepted_terms_conditions', models.BooleanField(default=False, verbose_name='I accept the terms and conditions as stated above')),
                ('ip', models.CharField(blank=True, max_length=100)),
                ('gender', models.CharField(choices=[('f', 'female'), ('m', 'male')], max_length=2, verbose_name='Gender')),
                ('picture', models.ImageField(blank=True, upload_to=guratorapp.models.content_file_name, verbose_name='Profile picture')),
                ('birthdate', models.DateField(verbose_name='Date of Birth')),
                ('matriculation_number', models.CharField(default='0', max_length=10)),
                ('gps_long', models.CharField(max_length=15)),
                ('gps_lat', models.CharField(max_length=15)),
                ('grade', models.CharField(max_length=5)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
