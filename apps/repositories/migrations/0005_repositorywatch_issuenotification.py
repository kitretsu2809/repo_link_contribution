from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repositories', '0004_issue_ai_summary_issue_created_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RepositoryWatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watches', to='repositories.repository')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repository_watches', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'repository')},
            },
        ),
        migrations.CreateModel(
            name='IssueNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='repositories.issue')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issue_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'issue')},
            },
        ),
    ]
