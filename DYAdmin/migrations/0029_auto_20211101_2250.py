# Generated by Django 3.2.7 on 2021-11-01 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DYAdmin', '0028_alter_consumer_remark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='address',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='consumer',
            name='phone',
            field=models.CharField(max_length=20, null=True),
        ),
    ]