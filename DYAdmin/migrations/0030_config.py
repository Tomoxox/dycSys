# Generated by Django 3.2.7 on 2021-11-04 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DYAdmin', '0029_auto_20211101_2250'),
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=0, verbose_name='是否删除')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('video_num', models.IntegerField(default=30)),
                ('task_num', models.IntegerField(default=3)),
                ('peer_num', models.IntegerField(default=5)),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
    ]
