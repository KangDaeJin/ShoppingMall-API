# Generated by Django 4.0.2 on 2022-04-09 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_alter_statustransition_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='shipping_message',
            field=models.CharField(default='aaa', max_length=50),
            preserve_default=False,
        ),
    ]