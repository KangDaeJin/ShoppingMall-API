# Generated by Django 4.0.2 on 2022-05-17 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0023_alter_delivery_options_alter_delivery_table'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='delivery',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelTable(
            name='delivery',
            table='delivery',
        ),
    ]
