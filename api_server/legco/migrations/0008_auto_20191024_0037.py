# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-10-24 00:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legco', '0007_auto_20190901_2351'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='name_short_ch',
            field=models.CharField(default='', max_length=512),
        ),
        migrations.AddField(
            model_name='party',
            name='name_short_en',
            field=models.CharField(default='', max_length=512),
        ),
    ]
