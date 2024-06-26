# Generated by Django 4.0.2 on 2022-06-06 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0001_initial'),
        ('user', '0016_merge_20220606_1313'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopperCoupon',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('end_date', models.DateField()),
                ('is_available', models.IntegerField()),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='coupon.coupon')),
                ('shopper', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='user.shopper')),
            ],
            options={
                'db_table': 'shopper_coupon',
            },
        ),
    ]
