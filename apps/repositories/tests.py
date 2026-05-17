from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings

from apps.repositories.models import Issue, IssueNotification, Repository, RepositoryWatch
from apps.repositories.notifications import send_issue_notifications


User = get_user_model()


class AuthAndWatchApiTests(TestCase):
    def setUp(self):
        self.repo = Repository.objects.create(
            github_id=101,
            name='demo',
            owner='octocat',
            full_name='octocat/demo',
            repo_url='https://github.com/octocat/demo',
        )

    def test_register_login_and_star_repository(self):
        register = self.client.post(
            '/api/auth/register/',
            data='{"email":"user@example.com","password":"secret123"}',
            content_type='application/json',
        )
        self.assertEqual(register.status_code, 201)
        self.assertTrue(register.json()['authenticated'])

        star = self.client.post(f'/api/repos/{self.repo.id}/star/')
        self.assertEqual(star.status_code, 200)
        self.assertTrue(RepositoryWatch.objects.filter(repository=self.repo).exists())

        logout = self.client.post('/api/auth/logout/')
        self.assertEqual(logout.status_code, 200)

        login = self.client.post(
            '/api/auth/login/',
            data='{"email":"user@example.com","password":"secret123"}',
            content_type='application/json',
        )
        self.assertEqual(login.status_code, 200)
        self.assertTrue(login.json()['authenticated'])

    def test_repo_serializer_marks_starred_for_authenticated_user(self):
        user = User.objects.create_user(username='user@example.com', email='user@example.com', password='secret123')
        RepositoryWatch.objects.create(user=user, repository=self.repo)
        self.client.force_login(user)

        response = self.client.get(f'/api/repos/{self.repo.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_starred'])

    def test_duplicate_email_registration_is_rejected_case_insensitively(self):
        first = self.client.post(
            '/api/auth/register/',
            data='{"email":"user@example.com","password":"secret123"}',
            content_type='application/json',
        )
        self.assertEqual(first.status_code, 201)

        second = self.client.post(
            '/api/auth/register/',
            data='{"email":"USER@example.com","password":"secret123"}',
            content_type='application/json',
        )
        self.assertEqual(second.status_code, 400)
        self.assertIn('already exists', second.json()['detail'])
        self.assertEqual(User.objects.filter(email__iexact='user@example.com').count(), 1)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='noreply@test.local',
)
class NotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='watcher@example.com',
            email='watcher@example.com',
            password='secret123',
        )
        self.repo = Repository.objects.create(
            github_id=202,
            name='demo',
            owner='octocat',
            full_name='octocat/demo',
            repo_url='https://github.com/octocat/demo',
        )
        RepositoryWatch.objects.create(user=self.user, repository=self.repo)
        self.issue = Issue.objects.create(
            repository=self.repo,
            github_issue_number=99,
            title='Bug in setup',
            body='Complete issue body text',
            issue_url='https://github.com/octocat/demo/issues/99',
            ai_summary='Short issue summary',
        )

    def test_send_issue_notifications_sends_once_per_user_issue(self):
        sent_count = send_issue_notifications(self.issue)
        self.assertEqual(sent_count, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Short issue summary', mail.outbox[0].body)
        self.assertIn('Complete issue body text', mail.outbox[0].body)

        sent_count_again = send_issue_notifications(self.issue)
        self.assertEqual(sent_count_again, 0)
        self.assertEqual(IssueNotification.objects.count(), 1)
