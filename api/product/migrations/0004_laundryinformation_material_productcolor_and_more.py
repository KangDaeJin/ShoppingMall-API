# Generated by Django 4.0 on 2022-02-17 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_alter_option_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='LaundryInformation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'db_table': 'laundry_information',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'db_table': 'material',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProductColor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('display_color_name', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'product_color',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProductColorImages',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('url', models.CharField(max_length=200)),
                ('sequence', models.IntegerField()),
            ],
            options={
                'db_table': 'product_color_images',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProductLaundryInformation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'product_laundry_information',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProductMaterial',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('material', models.CharField(max_length=20)),
                ('mixing_rate', models.IntegerField()),
            ],
            options={
                'db_table': 'product_material',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProductStyle',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'product_style',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'db_table': 'style',
                'managed': False,
            },
        ),
    ]
