# Generated by Django 4.0.2 on 2022-06-07 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_delete_cart'),
        ('coupon', '0007_remove_coupon_sub_categories_couponsubcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='sub_categories',
            field=models.ManyToManyField(through='coupon.CouponSubCategory', to='product.SubCategory'),
        ),
    ]
