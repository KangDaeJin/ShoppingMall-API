# Generated by Django 4.0.2 on 2022-08-03 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0030_alter_productadditionalinformation_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='maincategory',
            name='laundry_information_required',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='maincategory',
            name='product_additional_information_required',
            field=models.BooleanField(default=True),
        ),
    ]