# Generated by Django 4.0.2 on 2022-04-18 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0010_alter_refund_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='refund',
            name='created_at',
        ),
        migrations.AddField(
            model_name='exchangeinformation',
            name='completed_at',
            field=models.DateTimeField(null=True),
        ),
    ]