# Generated by Django 4.0.2 on 2022-05-01 13:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_rename_reciever_mobile_number_shoppershippingaddress_receiver_mobile_number_and_more'),
        ('product', '0015_alter_productquestionanswer_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productquestionanswer',
            name='shopper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='question_answers', to='user.shopper'),
        ),
    ]
