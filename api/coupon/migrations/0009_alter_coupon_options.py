# Generated by Django 4.0.2 on 2022-06-08 13:57

import builtins
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0008_coupon_sub_categories'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coupon',
            options={'ordering': [builtins.id]},
        ),
    ]
