# Generated by Django 3.2.7 on 2021-10-29 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DYAdmin', '0015_auto_20211028_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='cid',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='peervideo',
            name='comment_num',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='sec_uid',
            field=models.CharField(max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='peer',
            name='sec_uid',
            field=models.CharField(max_length=120, null=True),
        ),
    ]
