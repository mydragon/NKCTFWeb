# Generated by Django 2.1.1 on 2018-09-30 14:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Auth_Token', models.CharField(max_length=32, null=True)),
                ('Auth_Type', models.CharField(choices=[(1, 'GitHub'), (2, 'QQ')], max_length=16, null=True)),
                ('Score', models.IntegerField(default=0)),
                ('QQ', models.CharField(max_length=16, null=True)),
                ('Github', models.CharField(max_length=32, null=True)),
                ('Description', models.CharField(default='Welcome to NanKai CTF', max_length=128)),
                ('Email', models.CharField(max_length=32, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=32, unique=True)),
                ('Description', models.CharField(default='Join our team!!', max_length=128)),
                ('Leader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Member')),
            ],
        ),
    ]
