# Generated by Django 3.1 on 2020-08-25 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20200824_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='which_listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='auctions.listing'),
        ),
    ]
