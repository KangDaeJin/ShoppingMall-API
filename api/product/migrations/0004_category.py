# Generated by Django 4.0 on 2021-12-28 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_largecategory_smallcategory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'category',
                'managed': False,
            },
        ),
    ]