# Generated by Django 3.2.8 on 2021-11-12 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0003_config_original_chain'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='hard_limit_groups',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='config',
            name='hard_limit_members',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='config',
            name='hard_limit_photos',
            field=models.IntegerField(default=0),
        ),
    ]