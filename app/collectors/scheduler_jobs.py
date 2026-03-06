import logging

logger = logging.getLogger(__name__)


def register_jobs(scheduler, app):
    config = app.config

    @scheduler.task(
        'interval',
        id='collect_news',
        minutes=config.get('NEWS_COLLECTION_INTERVAL_MINUTES', 30),
        misfire_grace_time=900,
        max_instances=1,
    )
    def collect_news():
        from app.collectors.news_collector import NewsCollector
        try:
            count = NewsCollector().run(app)
            logger.info(f"NewsCollector: {count} stories collectees")
        except Exception as e:
            logger.error(f"NewsCollector erreur: {e}")

    @scheduler.task(
        'interval',
        id='collect_trends',
        hours=config.get('TRENDS_COLLECTION_INTERVAL_HOURS', 4),
        misfire_grace_time=900,
        max_instances=1,
    )
    def collect_trends():
        from app.collectors.trends_collector import TrendsCollector
        try:
            count = TrendsCollector().run(app)
            logger.info(f"TrendsCollector: {count} tendances collectees")
        except Exception as e:
            logger.error(f"TrendsCollector erreur: {e}")

    @scheduler.task(
        'interval',
        id='scrape_articles',
        minutes=config.get('ARTICLE_SCRAPE_INTERVAL_MINUTES', 60),
        misfire_grace_time=900,
        max_instances=1,
    )
    def scrape_articles():
        from app.collectors.article_collector import ArticleCollector
        try:
            count = ArticleCollector().run(app)
            logger.info(f"ArticleCollector: {count} articles scrapes")
        except Exception as e:
            logger.error(f"ArticleCollector erreur: {e}")
