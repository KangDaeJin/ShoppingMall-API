# Generated by Django 4.0.2 on 2022-04-06 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='discount_rate',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='membership',
            name='qualification',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]