# Generated by Django 4.0 on 2021-12-28 20:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_category'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Category',
        ),
    ]