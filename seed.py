"""Script de collecte initiale - lance manuellement les collecteurs."""
import logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    from app import create_app
    app = create_app()

    logger.info("=== Collecte initiale Google Discover France ===")

    # 1. Collecter les news Google News RSS
    logger.info("Collecte Google News RSS France...")
    from app.collectors.news_collector import NewsCollector
    try:
        count = NewsCollector().run(app)
        logger.info(f"  -> {count} stories collectees")
    except Exception as e:
        logger.error(f"  -> Erreur NewsCollector: {e}")

    # 2. Collecter les tendances Google Trends
    logger.info("Collecte Google Trends France...")
    from app.collectors.trends_collector import TrendsCollector
    try:
        count = TrendsCollector().run(app)
        logger.info(f"  -> {count} tendances collectees")
    except Exception as e:
        logger.error(f"  -> Erreur TrendsCollector: {e}")

    # 3. Scraper les métadonnées des articles
    logger.info("Scraping metadonnees articles...")
    from app.collectors.article_collector import ArticleCollector
    try:
        count = ArticleCollector().run(app)
        logger.info(f"  -> {count} articles scrapes")
    except Exception as e:
        logger.error(f"  -> Erreur ArticleCollector: {e}")

    logger.info("=== Collecte initiale terminee ===")

    # Résumé
    with app.app_context():
        from app.models import NewsStory, TrendingSearch, ArticleMetadata, Publisher
        from app.extensions import db
        logger.info(f"  Stories en base: {NewsStory.query.count()}")
        logger.info(f"  Tendances en base: {TrendingSearch.query.count()}")
        logger.info(f"  Metadonnees articles: {ArticleMetadata.query.count()}")
        logger.info(f"  Editeurs uniques: {Publisher.query.count()}")


if __name__ == '__main__':
    main()
