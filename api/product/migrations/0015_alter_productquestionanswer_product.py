# Generated by Django 4.0.2 on 2022-05-01 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_alter_productquestionanswer_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productquestionanswer',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='question_answers', to='product.product'),
        ),
    ]
