# Generated by Django 4.0.2 on 2022-04-25 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_delete_productimageforvalidation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
