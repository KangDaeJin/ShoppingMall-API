# Generated by Django 4.0.2 on 2022-07-29 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0026_product2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='theme',
        ),
    ]