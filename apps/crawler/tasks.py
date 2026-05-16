from celery import shared_task
from apps.crawler.services import GitHubCrawlerService


@shared_task(bind=True, name='crawler.run_github_crawler')
def run_github_crawler_task(self, min_stars=500, per_page=10):
    """Fetch top repos by stars (single-query, used for quick runs)."""
    try:
        crawler = GitHubCrawlerService()
        repos = crawler.fetch_top_repositories(min_stars=min_stars, per_page=per_page)
        return {'status': 'success', 'repositories_processed': len(repos)}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True, name='crawler.run_all_categories')
def run_all_categories_task(self, per_category=50):
    """Crawl 500 repos across 10 categories."""
    try:
        crawler = GitHubCrawlerService()
        total = crawler.fetch_all_categories(per_category=per_category)
        return {'status': 'success', 'repositories_processed': total}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60, max_retries=3)
