# Generated by Django 3.2.7 on 2021-10-28 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DYAdmin', '0013_alter_video_aweme_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='set_meal',
            field=models.CharField(default='基础版', max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='customerloginlogging',
            name='browser',
            field=models.CharField(max_length=255),
        ),
    ]
