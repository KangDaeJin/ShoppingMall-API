# Generated by Django 4.0.2 on 2022-04-07 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_product_base_discounted_price_product_sale_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='stock_count',
        ),
        migrations.RemoveField(
            model_name='product',
            name='wholesaler_stock_count',
        ),
    ]
