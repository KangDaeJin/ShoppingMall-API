# Generated by Django 4.0.2 on 2022-07-31 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0029_productadditionalinformation_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='productadditionalinformation',
            table='product_additional_information',
        ),
    ]
