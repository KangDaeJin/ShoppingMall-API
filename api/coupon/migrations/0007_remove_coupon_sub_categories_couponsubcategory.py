# Generated by Django 4.0.2 on 2022-06-07 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_delete_cart'),
        ('coupon', '0006_alter_coupon_products_alter_coupon_sub_categories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='sub_categories',
        ),
        migrations.CreateModel(
            name='CouponSubCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='coupon.coupon')),
                ('sub_category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.subcategory')),
            ],
            options={
                'db_table': 'coupon_sub_category',
            },
        ),
    ]