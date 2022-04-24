# Generated by Django 4.0.2 on 2022-04-22 16:42

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0014_remove_cancellationinformation_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusHistory',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='status_history', to='order.orderitem')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='order.status')),
            ],
            options={
                'db_table': 'status_history',
            },
        ),
        migrations.DeleteModel(
            name='StatusLog',
        ),
    ]
