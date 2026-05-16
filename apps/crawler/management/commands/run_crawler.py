from django.core.management.base import BaseCommand
from apps.crawler.services import GitHubCrawlerService
from apps.crawler.tasks import run_github_crawler_task, run_all_categories_task


class Command(BaseCommand):
    help = 'Runs the GitHub crawler to fetch repositories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--async', action='store_true', dest='run_async',
            help='Dispatch to Celery background worker.',
        )
        parser.add_argument(
            '--per-page', type=int, default=10, dest='per_page',
            help='Repos to fetch in single-query mode (default: 10).',
        )
        parser.add_argument(
            '--all-categories', action='store_true', dest='all_categories',
            help='Crawl 500 repos across 10 categories instead of single-query mode.',
        )
        parser.add_argument(
            '--per-category', type=int, default=50, dest='per_category',
            help='Repos per category when using --all-categories (default: 50).',
        )

    def handle(self, *args, **options):
        per_page = options['per_page']
        per_category = options['per_category']
        run_async = options['run_async']
        all_categories = options['all_categories']

        if run_async:
            if all_categories:
                self.stdout.write(self.style.NOTICE(
                    f'Dispatching full category crawl ({per_category} repos × 10 categories = ~{per_category*10} repos)...'
                ))
                result = run_all_categories_task.delay(per_category=per_category)
            else:
                self.stdout.write(self.style.NOTICE(
                    f'Dispatching single-query crawl ({per_page} repos)...'
                ))
                result = run_github_crawler_task.delay(min_stars=500, per_page=per_page)

            self.stdout.write(self.style.SUCCESS(
                f'Task dispatched! Task ID: {result.id}\n'
                f'Watch Celery worker terminal for progress.'
            ))
        else:
            crawler = GitHubCrawlerService()
            if not crawler.token:
                self.stdout.write(self.style.WARNING(
                    "No GITHUB_TOKEN found. Rate limits will be restricted."
                ))
            if all_categories:
                self.stdout.write(self.style.NOTICE(
                    f'Crawling all categories ({per_category} repos each)...'
                ))
                total = crawler.fetch_all_categories(per_category=per_category)
                self.stdout.write(self.style.SUCCESS(f'Done! Processed {total} repositories.'))
            else:
                self.stdout.write(self.style.NOTICE(f'Starting single-query crawl ({per_page} repos)...'))
                repos = crawler.fetch_top_repositories(min_stars=500, per_page=per_page)
                self.stdout.write(self.style.SUCCESS(f'Done! Processed {len(repos)} repositories.'))
