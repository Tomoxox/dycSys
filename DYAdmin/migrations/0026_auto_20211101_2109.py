# Generated by Django 3.2.7 on 2021-11-01 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DYAdmin', '0025_alter_comment_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peer',
            name='avatar_thumb',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='peer',
            name='signature',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='peer',
            name='unique_id',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
