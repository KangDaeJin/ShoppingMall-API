# Generated by Django 4.0.2 on 2022-05-12 13:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0020_alter_productcolor_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productmaterial',
            unique_together=set(),
        ),
    ]