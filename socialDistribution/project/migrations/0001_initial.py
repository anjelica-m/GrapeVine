# Generated by Django 3.1.6 on 2023-10-14 17:02

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('url', models.URLField()),
                ('host', models.GenericIPAddressField(default='127.0.0.1:8000')),
                ('displayName', models.CharField(max_length=50)),
                ('github', models.URLField()),
                ('profileImage', models.URLField()),
                ('followers_open_friend_requests', models.ManyToManyField(blank=True, related_name='open_requests', to='project.Author')),
                ('following', models.ManyToManyField(blank=True, related_name='i_am_following', to='project.Author')),
                ('friends', models.ManyToManyField(blank=True, related_name='my_friends', to='project.Author')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nodeName', models.CharField(max_length=50)),
                ('apiURL', models.URLField()),
                ('host', models.GenericIPAddressField(default='127.0.0.1:8000')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('title', models.CharField(default='Untitled', max_length=50)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('source', models.URLField()),
                ('origin', models.URLField()),
                ('description', models.CharField(default='', max_length=50)),
                ('contentType', models.CharField(max_length=200)),
                ('content', models.TextField(max_length=600)),
                ('categories', models.CharField(default='', max_length=200)),
                ('count', models.IntegerField(default=0)),
                ('published', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('visibility', models.CharField(choices=[('PUBLIC', 'PUBLIC'), ('PRIVATE', 'PRIVATE'), ('FRIENDS_ONLY', 'FRIENDS_ONLY')], default='PUBLIC', max_length=50)),
                ('unlisted', models.BooleanField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.author')),
            ],
        ),
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('context', models.URLField()),
                ('summary', models.CharField(max_length=50)),
                ('object_post_or_comment', models.URLField()),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.author')),
            ],
        ),
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('items', models.CharField(default='', max_length=200)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.author')),
            ],
        ),
        migrations.CreateModel(
            name='FriendFollowRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('summary', models.CharField(max_length=50)),
                ('actor_authorAAsksB', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='a_asks_b', to='project.author')),
                ('object_authorB', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='b_is_asked', to='project.author')),
            ],
        ),
        migrations.CreateModel(
            name='Followers',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('authorAFollowsB', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='a_follows_b', to='project.author')),
                ('authorB', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='b_is_followed', to='project.author')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment', models.TextField(max_length=600)),
                ('contentType', models.CharField(max_length=200)),
                ('published', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.author')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.post')),
            ],
        ),
    ]
