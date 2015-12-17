# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-17 10:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('college', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalCollege',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=108)),
                ('location', models.TextField()),
                ('phone', models.CharField(max_length=32)),
                ('homepage', models.URLField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical college',
            },
        ),
        migrations.RemoveField(
            model_name='college',
            name='cover',
        ),
        migrations.RemoveField(
            model_name='college',
            name='logo',
        ),
    ]
