# Generated by Django 4.0.2 on 2022-02-28 16:46

import common.storage
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Age',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'age',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
                ('image_url', models.ImageField(max_length=200, storage=common.storage.ClientSVGStorage, upload_to='')),
            ],
            options={
                'db_table': 'color',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Flexibility',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'flexibility',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'db_table': 'keyword',
            },
        ),
        migrations.CreateModel(
            name='LaundryInformation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'db_table': 'laundry_information',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='MainCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
                ('image_url', models.ImageField(max_length=200, storage=common.storage.ClientSVGStorage, upload_to='')),
            ],
            options={
                'db_table': 'main_category',
                'ordering': ['id'],
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
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=60)),
                ('code', models.CharField(default='AA', max_length=12)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('price', models.IntegerField()),
                ('on_sale', models.BooleanField(default=True)),
                ('age', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.age')),
            ],
            options={
                'db_table': 'product',
            },
        ),
        migrations.CreateModel(
            name='ProductColor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('display_color_name', models.CharField(max_length=20)),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.color')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='colors', to='product.product')),
            ],
            options={
                'db_table': 'product_color',
                'unique_together': {('product', 'display_color_name')},
            },
        ),
        migrations.CreateModel(
            name='SeeThrough',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'see_through',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10, unique=True)),
            ],
            options={
                'db_table': 'size',
                'ordering': ['id'],
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
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('require_product_additional_information', models.BooleanField()),
                ('require_laundry_information', models.BooleanField()),
                ('main_category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sub_categories', to='product.maincategory')),
            ],
            options={
                'db_table': 'sub_category',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'db_table': 'tag',
            },
        ),
        migrations.CreateModel(
            name='Thickness',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'thickness',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='SubCategorySize',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('size', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.size')),
                ('sub_category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.subcategory')),
            ],
            options={
                'db_table': 'sub_category_size',
                'unique_together': {('sub_category', 'size')},
            },
        ),
        migrations.AddField(
            model_name='subcategory',
            name='sizes',
            field=models.ManyToManyField(through='product.SubCategorySize', to='product.Size'),
        ),
        migrations.CreateModel(
            name='ProductLaundryInformation',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('laundry_information', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.laundryinformation')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.product')),
            ],
            options={
                'db_table': 'product_laundry_information',
                'unique_together': {('product', 'laundry_information')},
            },
        ),
        migrations.AddField(
            model_name='product',
            name='laundry_informations',
            field=models.ManyToManyField(through='product.ProductLaundryInformation', to='product.LaundryInformation'),
        ),
        migrations.AddField(
            model_name='product',
            name='style',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.style'),
        ),
        migrations.AddField(
            model_name='product',
            name='sub_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.subcategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(db_table='product_tag', to='product.Tag'),
        ),
        migrations.AddField(
            model_name='product',
            name='wholesaler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='user.wholesaler'),
        ),
        migrations.CreateModel(
            name='ProductMaterial',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('material', models.CharField(max_length=20)),
                ('mixing_rate', models.IntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='materials', to='product.product')),
            ],
            options={
                'db_table': 'product_material',
                'unique_together': {('product', 'material')},
            },
        ),
        migrations.CreateModel(
            name='ProductImages',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('image_url', models.CharField(max_length=200)),
                ('sequence', models.IntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='images', to='product.product')),
            ],
            options={
                'db_table': 'product_images',
                'ordering': ['sequence'],
                'unique_together': {('product', 'sequence')},
            },
        ),
        migrations.CreateModel(
            name='ProductColorImages',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('image_url', models.CharField(max_length=200)),
                ('sequence', models.IntegerField()),
                ('product_color', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='images', to='product.productcolor')),
            ],
            options={
                'db_table': 'product_color_images',
                'unique_together': {('product_color', 'sequence'), ('product_color', 'image_url')},
            },
        ),
        migrations.CreateModel(
            name='ProductAdditionalInformation',
            fields=[
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, related_name='product_additional_information', serialize=False, to='product.product')),
                ('lining', models.BooleanField()),
                ('flexibility', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.flexibility')),
                ('see_through', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.seethrough')),
                ('thickness', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.thickness')),
            ],
            options={
                'db_table': 'product_additional_information',
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('display_size_name', models.CharField(max_length=20)),
                ('price_difference', models.IntegerField(default=0)),
                ('product_color', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='options', to='product.productcolor')),
                ('size', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.size')),
            ],
            options={
                'db_table': 'option',
                'unique_together': {('product_color', 'size')},
            },
        ),
    ]
