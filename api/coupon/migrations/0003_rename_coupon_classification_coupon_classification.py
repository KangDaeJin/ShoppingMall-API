# Generated by Django 4.0.2 on 2022-06-06 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0002_rename_maximum_order_price_coupon_maximum_discount_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coupon',
            old_name='coupon_classification',
            new_name='classification',
        ),
    ]