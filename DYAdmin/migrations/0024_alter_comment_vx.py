# Generated by Django 3.2.7 on 2021-10-31 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DYAdmin', '0023_auto_20211030_0854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='vx',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
