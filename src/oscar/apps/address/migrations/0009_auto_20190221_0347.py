# Generated by Django 2.1.2 on 2019-02-21 10:47

import dj_address.models
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0008_auto_20190221_0313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='address',
            field=dj_address.models.AddressField(default=1, on_delete=django.db.models.deletion.PROTECT, to='dj_address.Address'),
            preserve_default=False,
        ),
    ]
