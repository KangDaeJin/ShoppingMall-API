# Generated by Django 4.0.2 on 2022-05-31 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0025_alter_order_options_alter_status_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='status',
            options={},
        ),
        migrations.AlterField(
            model_name='status',
            name='name',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
