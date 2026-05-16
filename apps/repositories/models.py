from django.db import models

class Repository(models.Model):
    github_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    repo_url = models.URLField()
    description = models.TextField(blank=True, null=True)
    readme = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    topics = models.JSONField(default=list, blank=True)
    stars = models.IntegerField(default=0)
    forks = models.IntegerField(default=0)
    open_issues = models.IntegerField(default=0)
    contributors_count = models.IntegerField(default=0)
    activity_score = models.FloatField(default=0)
    beginner_score = models.FloatField(default=0)
    doc_score = models.FloatField(default=0)
    popularity_score = models.FloatField(default=0)
    maintenance_score = models.FloatField(default=0)
    final_score = models.FloatField(default=0)
    last_commit = models.DateTimeField(null=True, blank=True)
    
    # AI Embeddings
    embedding = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.full_name

class Issue(models.Model):
    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        related_name='issues'
    )
    title = models.CharField(max_length=500)
    body = models.TextField(blank=True, null=True)
    issue_url = models.URLField()
    difficulty_score = models.FloatField(default=0)
    is_good_first_issue = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.repository.name} - {self.title}"
