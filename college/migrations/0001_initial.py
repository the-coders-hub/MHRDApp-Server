# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-17 04:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('account', '0002_auto_20151216_2043'),
    ]

    operations = [
        migrations.CreateModel(
            name='College',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=108)),
                ('location', models.TextField()),
                ('phone', models.CharField(max_length=32)),
                ('homepage', models.URLField()),
                ('cover', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.File')),
                ('email_domains', models.ManyToManyField(to='account.EmailDomain')),
                ('logo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.File')),
                ('tags', models.ManyToManyField(to='core.Tag')),
            ],
        ),
    ]
