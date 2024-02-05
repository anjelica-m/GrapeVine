# Generated by Django 3.1.6 on 2023-10-24 21:43

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_auto_20231023_0406'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('context', models.URLField()),
                ('summary', models.CharField(max_length=50)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.author')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.comment')),
            ],
        ),
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('context', models.URLField()),
                ('summary', models.CharField(max_length=50)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.author')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.post')),
            ],
        ),
        migrations.DeleteModel(
            name='Like',
        ),
    ]
