# Generated by Django 3.2.7 on 2021-11-07 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DYAdmin', '0031_alter_video_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delegate',
            name='available_till',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='peer_monitor_ids',
            field=models.CharField(max_length=855, null=True),
        ),
    ]
