# Generated by Django 5.1 on 2024-09-01 11:14

import db.validators
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('author', models.CharField(blank=True, max_length=100, null=True)),
                ('link', models.URLField(blank=True, max_length=500, null=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to=db.validators.get_file_path, validators=[db.validators.attatchment_validate])),
                ('image', models.ImageField(blank=True, null=True, upload_to=db.validators.get_image_path, validators=[db.validators.image_validate, django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'webp'])])),
                ('flag', models.CharField(max_length=255)),
                ('disable_solve_notif', models.BooleanField(default=False)),
                ('is_over', models.BooleanField(default=False)),
                ('message_id', models.CharField(blank=True, editable=False, max_length=50, null=True)),
                ('add_time', models.DateTimeField(auto_now_add=True)),
                ('solve_count', models.IntegerField(default=0, editable=False)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='db.category')),
            ],
        ),
        migrations.CreateModel(
            name='Solve',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solved_time', models.DateTimeField(auto_now_add=True)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='db.challenge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
