# Generated by Django 4.0 on 2022-02-21 20:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_alter_color_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='age',
            options={'managed': False, 'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='color',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='flexibility',
            options={'managed': False, 'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='productmaterial',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='seethrough',
            options={'managed': False, 'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='thickness',
            options={'managed': False, 'ordering': ['id']},
        ),
    ]
