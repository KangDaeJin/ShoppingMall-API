# Generated by Django 4.0.2 on 2022-06-06 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0002_rename_maximum_order_price_coupon_maximum_discount_price_and_more'),
        ('user', '0019_alter_shoppercoupon_is_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopper',
            name='coupons',
            field=models.ManyToManyField(through='user.ShopperCoupon', to='coupon.Coupon'),
        ),
        migrations.AlterField(
            model_name='shoppercoupon',
            name='coupon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='coupon.coupon'),
        ),
        migrations.AlterField(
            model_name='shoppercoupon',
            name='shopper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='user.shopper'),
        ),
    ]