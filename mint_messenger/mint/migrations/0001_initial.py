# Generated by Django 4.2.7 on 2023-11-13 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('send_time', models.DateTimeField(auto_now_add=True)),
                ('edit_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('send_time', 'message'),
            },
        ),
    ]
