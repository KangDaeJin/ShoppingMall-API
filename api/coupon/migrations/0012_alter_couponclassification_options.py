# Generated by Django 4.0.2 on 2022-06-09 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0011_alter_coupon_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='couponclassification',
            options={'ordering': ['id']},
        ),
    ]