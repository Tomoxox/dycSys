# Generated by Django 3.2.7 on 2021-10-21 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DYAdmin', '0004_auto_20211014_2235'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyHotWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=0, verbose_name='是否删除')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('words', models.CharField(max_length=50, null=True)),
                ('index', models.CharField(max_length=80)),
                ('Customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DYAdmin.customer')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
    ]
