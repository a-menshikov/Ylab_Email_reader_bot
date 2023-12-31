# Generated by Django 4.1 on 2023-09-13 13:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, unique=True, verbose_name='Название')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug сервиса')),
                ('address', models.CharField(max_length=256, verbose_name='Адрес сервера')),
                ('port', models.PositiveIntegerField(verbose_name='Порт сервера')),
            ],
            options={
                'verbose_name': 'Почтовый сервис',
                'verbose_name_plural': 'Почтовые сервисы',
            },
        ),
        migrations.CreateModel(
            name='EmailBox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_username', models.CharField(max_length=64, verbose_name='Имя пользователя')),
                ('email_password', models.CharField(max_length=256, verbose_name='Пароль')),
                ('email_service', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='boxes', to='email_service.emailservice', verbose_name='Почтовый сервис')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='boxes', to='user.botuser', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Почтовый ящик',
                'verbose_name_plural': 'Почтовые ящики',
            },
        ),
        migrations.CreateModel(
            name='BoxFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filter_value', models.CharField(max_length=256, verbose_name='Значение фильтра')),
                ('filter_name', models.CharField(blank=True, max_length=128, null=True, verbose_name='Имя фильтра')),
                ('box_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filters', to='email_service.emailbox', verbose_name='Почтовый ящик')),
            ],
            options={
                'verbose_name': 'Фильтр',
                'verbose_name_plural': 'Фильтры',
            },
        ),
    ]
