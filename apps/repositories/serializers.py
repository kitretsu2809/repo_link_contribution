from rest_framework import serializers
from .models import Repository, Issue


class IssueSerializer(serializers.ModelSerializer):
    days_ago = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'id', 'github_issue_number', 'title', 'issue_url',
            'state', 'labels', 'created_at', 'days_ago',
            'is_good_first_issue', 'ai_summary',
        ]

    def get_days_ago(self, obj):
        if not obj.created_at:
            return None
        from datetime import datetime, timezone
        delta = datetime.now(timezone.utc) - obj.created_at
        return delta.days


class RepositorySerializer(serializers.ModelSerializer):
    recent_issues = serializers.SerializerMethodField()
    recent_issues_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Repository
        fields = '__all__'

    def get_recent_issues(self, obj):
        """Return issues created in the last 5 days."""
        from datetime import datetime, timezone, timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=5)
        issues = obj.issues.filter(created_at__gte=cutoff).order_by('-created_at')[:10]
        return IssueSerializer(issues, many=True).data

    def get_recent_issues_count(self, obj):
        from datetime import datetime, timezone, timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=5)
        return obj.issues.filter(created_at__gte=cutoff).count()

    def get_is_starred(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.watches.filter(user=request.user).exists()
