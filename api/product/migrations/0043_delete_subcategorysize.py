# Generated by Django 4.0.2 on 2022-08-16 15:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0042_remove_subcategory_require_laundry_information_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SubCategorySize',
        ),
    ]
