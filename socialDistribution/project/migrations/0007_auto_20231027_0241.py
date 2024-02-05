# Generated by Django 3.1.6 on 2023-10-27 02:41

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_auto_20231024_2143'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('summary', models.CharField(max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='friendfollowrequest',
            name='actor_authorAAsksB',
        ),
        migrations.RemoveField(
            model_name='friendfollowrequest',
            name='object_authorB',
        ),
        migrations.RemoveField(
            model_name='author',
            name='followers_open_friend_requests',
        ),
        migrations.RemoveField(
            model_name='author',
            name='friends',
        ),
        migrations.AlterField(
            model_name='author',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='followers', to='project.Author'),
        ),
        migrations.DeleteModel(
            name='Follower',
        ),
        migrations.DeleteModel(
            name='FriendFollowRequest',
        ),
        migrations.AddField(
            model_name='followrequest',
            name='follower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_follow_requests', to='project.author'),
        ),
        migrations.AddField(
            model_name='followrequest',
            name='following',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_follow_requests', to='project.author'),
        ),
    ]
