# Generated by Django 4.0.2 on 2022-04-08 13:57

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_alter_product_theme'),
        ('user', '0003_shopper_point'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductLike',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.product')),
                ('shopper', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='user.shopper')),
            ],
            options={
                'db_table': 'product_like',
                'unique_together': {('shopper', 'product')},
            },
        ),
    ]
