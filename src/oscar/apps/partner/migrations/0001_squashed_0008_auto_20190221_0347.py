# Generated by Django 2.1.2 on 2019-02-21 11:34

import dj_address.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import oscar.core.utils
import oscar.models.fields.autoslugfield


class Migration(migrations.Migration):

    replaces = [('partner', '0001_initial'), ('partner', '0002_auto_20141007_2032'), ('partner', '0003_auto_20150604_1450'), ('partner', '0004_auto_20160107_1755'), ('partner', '0005_auto_20181115_1953'), ('partner', '0006_auto_20190221_0223'), ('partner', '0007_auto_20190221_0313'), ('partner', '0008_auto_20190221_0347')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dj_address', '0002_auto_20160213_1726'),
        ('address', '0001_initial'),
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', oscar.models.fields.autoslugfield.AutoSlugField(blank=True, editable=False, max_length=128, populate_from='name', unique=True, verbose_name='Code')),
                ('name', models.CharField(blank=True, max_length=128, verbose_name='Name')),
                ('users', models.ManyToManyField(blank=True, null=True, related_name='partners', to=settings.AUTH_USER_MODEL, verbose_name='Users')),
            ],
            options={
                'verbose_name_plural': 'Fulfillment partners',
                'verbose_name': 'Fulfillment partner',
                'abstract': False,
                'permissions': (('dashboard_access', 'Can access dashboard'),),
            },
        ),
        migrations.CreateModel(
            name='PartnerAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, choices=[('Mr', 'Mr'), ('Miss', 'Miss'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr')], max_length=64, verbose_name='Title')),
                ('first_name', models.CharField(blank=True, max_length=255, verbose_name='First name')),
                ('last_name', models.CharField(blank=True, max_length=255, verbose_name='Last name')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='partner.Partner', verbose_name='Partner')),
                ('address', dj_address.models.AddressField(on_delete=django.db.models.deletion.PROTECT, to='dj_address.Address')),
            ],
            options={
                'verbose_name_plural': 'Partner addresses',
                'verbose_name': 'Partner address',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StockAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('threshold', models.PositiveIntegerField(verbose_name='Threshold')),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Closed', 'Closed')], default='Open', max_length=128, verbose_name='Status')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('date_closed', models.DateTimeField(blank=True, null=True, verbose_name='Date Closed')),
            ],
            options={
                'ordering': ('-date_created',),
                'verbose_name_plural': 'Stock alerts',
                'verbose_name': 'Stock alert',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StockRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner_sku', models.CharField(max_length=128, verbose_name='Partner SKU')),
                ('price_currency', models.CharField(default=oscar.core.utils.get_default_currency, max_length=12, verbose_name='Currency')),
                ('price_excl_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Price (excl. tax)')),
                ('price_retail', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Price (retail)')),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Cost Price')),
                ('num_in_stock', models.PositiveIntegerField(blank=True, null=True, verbose_name='Number in stock')),
                ('num_allocated', models.IntegerField(blank=True, null=True, verbose_name='Number allocated')),
                ('low_stock_threshold', models.PositiveIntegerField(blank=True, null=True, verbose_name='Low Stock Threshold')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Date updated')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stockrecords', to='partner.Partner', verbose_name='Partner')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stockrecords', to='catalogue.Product', verbose_name='Product')),
            ],
            options={
                'verbose_name_plural': 'Stock records',
                'verbose_name': 'Stock record',
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='stockrecord',
            unique_together={('partner', 'partner_sku')},
        ),
        migrations.AddField(
            model_name='stockalert',
            name='stockrecord',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='partner.StockRecord', verbose_name='Stock Record'),
        ),
        migrations.AlterField(
            model_name='partner',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='partners', to=settings.AUTH_USER_MODEL, verbose_name='Users'),
        ),
        migrations.AlterModelOptions(
            name='partner',
            options={'ordering': ('name', 'code'), 'permissions': (('dashboard_access', 'Can access dashboard'),), 'verbose_name': 'Fulfillment partner', 'verbose_name_plural': 'Fulfillment partners'},
        ),
    ]