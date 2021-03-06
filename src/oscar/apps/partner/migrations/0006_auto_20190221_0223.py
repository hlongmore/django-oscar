# Generated by Django 2.1.2 on 2019-02-21 09:23

import dj_address.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dj_address', '0002_auto_20160213_1726'),
        ('partner', '0004_auto_20160107_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='partneraddress',
            name='address',
            field=dj_address.models.AddressField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='dj_address.Address'),
        ),
        migrations.AddField(
            model_name='partneraddress',
            name='unit_designator',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
