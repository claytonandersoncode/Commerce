# Generated by Django 3.1 on 2020-08-25 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20200825_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='startbid',
            field=models.FloatField(null=True),
        ),
    ]
