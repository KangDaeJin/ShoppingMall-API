# Generated by Django 4.0.2 on 2022-04-12 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_alter_cancellationinformation_refund'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refund',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
