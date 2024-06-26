# Generated by Django 4.0.2 on 2022-04-26 16:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_rename_reciever_mobile_number_shoppershippingaddress_receiver_mobile_number_and_more'),
        ('product', '0012_productquestionanswerclassification'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductQuestionAnswer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.CharField(max_length=1000)),
                ('answer', models.CharField(max_length=1000, null=True)),
                ('answer_completed', models.BooleanField(default=False)),
                ('is_secret', models.BooleanField(default=False)),
                ('classification', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.productquestionanswerclassification')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.product')),
                ('shopper', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='user.shopper')),
            ],
            options={
                'db_table': 'product_question_answer',
            },
        ),
    ]
