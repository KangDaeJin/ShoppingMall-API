# Generated by Django 4.0.2 on 2022-06-08 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0009_alter_coupon_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coupon',
            options={'ordering': ['id']},
        ),
    ]
