# Generated by Django 4.0.2 on 2022-07-27 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SettingGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('app', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=20)),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
            options={
                'db_table': 'setting_group',
                'unique_together': {('app', 'name')},
            },
        ),
        migrations.CreateModel(
            name='SettingItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='items', to='common.settinggroup')),
            ],
            options={
                'db_table': 'setting_item',
                'unique_together': {('group', 'name')},
            },
        ),
    ]
