# Generated by Django 4.2.7 on 2023-11-27 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0013_alter_node_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='github',
            field=models.URLField(blank=True, null=True),
        ),
    ]