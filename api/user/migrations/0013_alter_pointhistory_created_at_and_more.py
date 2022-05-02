# Generated by Django 4.0.2 on 2022-05-02 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_alter_pointhistory_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pointhistory',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='pointhistory',
            name='shopper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='point_histories', to='user.shopper'),
        ),
    ]
