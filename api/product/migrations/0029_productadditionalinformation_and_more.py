# Generated by Django 4.0.2 on 2022-07-31 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0009_rename_key_settinggroup_main_key_and_more'),
        ('product', '0028_remove_product2_flexibility_remove_product2_lining_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductAdditionalInformation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('flexibility', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_additional_information_flexibility', to='common.settingitem')),
                ('lining', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_additional_information_lining', to='common.settingitem')),
                ('see_through', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_additional_information_see_through', to='common.settingitem')),
                ('thickness', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_additional_information_thickness', to='common.settingitem')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='additional_information',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='product.productadditionalinformation'),
        ),
    ]
