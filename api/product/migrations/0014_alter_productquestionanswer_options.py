# Generated by Django 4.0.2 on 2022-04-27 19:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_productquestionanswer'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productquestionanswer',
            options={'ordering': ['-created_at']},
        ),
    ]