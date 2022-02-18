# Generated by Django 4.0 on 2022-02-17 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_laundryinformation_material_productcolor_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubCategorySize',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'sub_category_size',
                'managed': False,
            },
        ),
        migrations.AddField(
            model_name='subcategory',
            name='sizes',
            field=models.ManyToManyField(through='product.SubCategorySize', to='product.Size'),
        ),
    ]