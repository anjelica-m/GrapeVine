# Generated by Django 4.2.7 on 2023-11-28 07:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0012_post_private_reciever_alter_post_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='private_reciever',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reciever', to='project.author'),
        ),
    ]
