# Generated by Django 3.2.7 on 2021-10-27 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DYAdmin', '0012_auto_20211027_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='aweme_id',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
