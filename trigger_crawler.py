import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.crawler.services import GitHubCrawlerService

if __name__ == '__main__':
    print("🚀 Starting manual repository crawl...")
    crawler = GitHubCrawlerService()
    # We use per_category=10 for a quicker run, but you can increase it
    total = crawler.fetch_all_categories(per_category=10)
    print(f"✅ Finished! Processed {total} repositories.")
