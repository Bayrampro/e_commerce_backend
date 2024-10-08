# Generated by Django 5.0.7 on 2024-07-17 10:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='AllProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('main_img', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('img_1', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('img_2', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('img_3', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('img_4', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('img_5', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rating', models.FloatField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='category', to='core.category')),
            ],
            options={
                'verbose_name': 'AllProduct',
                'verbose_name_plural': 'AllProduct',
            },
        ),
    ]
