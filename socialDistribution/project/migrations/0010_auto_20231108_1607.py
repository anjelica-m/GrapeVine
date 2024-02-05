# Generated by Django 3.1.6 on 2023-11-08 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0009_author_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='type',
            field=models.CharField(default='post', max_length=20),
        ),
        migrations.AlterField(
            model_name='author',
            name='host',
            field=models.CharField(default='127.0.0.1', max_length=200),
        ),
        migrations.AlterField(
            model_name='node',
            name='host',
            field=models.CharField(default='127.0.0.1:8000', max_length=200),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(default='', max_length=600),
        ),
        migrations.AlterField(
            model_name='post',
            name='contentType',
            field=models.CharField(default='text/plain', max_length=200),
        ),
        migrations.AlterField(
            model_name='post',
            name='origin',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='source',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='unlisted',
            field=models.BooleanField(default=False),
        ),
    ]