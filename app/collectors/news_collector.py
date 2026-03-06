import time
import logging
from datetime import datetime
from urllib.parse import urlparse

import feedparser

from app.collectors.base import BaseCollector
from app.extensions import db
from app.models import NewsStory, Publisher, CategoryMapping

logger = logging.getLogger(__name__)

# Mapping Google News topics -> catégorie française par défaut
TOPIC_CATEGORY_MAP = {
    'WORLD': 'International',
    'NATION': 'Politique',
    'BUSINESS': 'Economie',
    'TECHNOLOGY': 'Technologie',
    'ENTERTAINMENT': 'Divertissement',
    'SPORTS': 'Sport',
    'SCIENCE': 'Science',
    'HEALTH': 'Sante',
    'GENERAL': 'Actualites',
}


class NewsCollector(BaseCollector):
    COLLECTOR_TYPE = 'news'

    def collect(self, app):
        with app.app_context():
            # Charger les mappings de catégories depuis la DB
            db_mappings = CategoryMapping.query.filter(
                CategoryMapping.google_news_topic.isnot(None)
            ).all()
            cat_map = {m.google_news_topic: m.category_fr for m in db_mappings}
            # Fallback sur le mapping par défaut
            for k, v in TOPIC_CATEGORY_MAP.items():
                cat_map.setdefault(k, v)

            total = 0
            base = app.config['GNEWS_BASE_URL']
            params = app.config['GNEWS_PARAMS']

            # Flux principal
            total += self._process_feed(f"{base}{params}", 'GENERAL', cat_map)
            time.sleep(1)

            # Flux par topic
            for topic in app.config['GNEWS_TOPICS']:
                url = f"{base}/headlines/section/topic/{topic}{params}"
                total += self._process_feed(url, topic, cat_map)
                time.sleep(1)

            return total

    def _process_feed(self, url, rss_category, cat_map):
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            logger.error(f"Erreur parsing feed {url}: {e}")
            return 0

        inserted = 0
        for entry in feed.entries:
            try:
                inserted += self._process_entry(entry, rss_category, cat_map)
            except Exception as e:
                logger.warning(f"Erreur traitement entrée: {e}")
                continue
        return inserted

    def _process_entry(self, entry, rss_category, cat_map):
        google_url = entry.get('link', '')
        title = entry.get('title', '').strip()
        if not title or not google_url:
            return 0

        # Utiliser l'URL Google News comme identifiant unique
        article_url = google_url

        # Vérifier doublon
        existing = NewsStory.query.filter_by(url=article_url).first()
        if existing:
            return 0

        # Extraire le domaine depuis le champ source du RSS
        source = entry.get('source')
        publisher_name = None
        domain = 'unknown'
        if source:
            publisher_name = source.get('title', None)
            source_href = source.get('href', '')
            if source_href:
                domain = self._extract_domain(source_href)
        if domain == 'unknown':
            domain = self._extract_domain(google_url)

        # Extraire la date de publication
        published_at = None
        if entry.get('published_parsed'):
            try:
                published_at = datetime(*entry.published_parsed[:6])
            except Exception:
                pass

        # Description
        description = entry.get('summary', entry.get('description', ''))

        # Catégorie française
        assigned_cat = cat_map.get(rss_category, 'Autres')

        # Créer le NewsStory
        story = NewsStory(
            title=title,
            url=article_url,
            google_news_url=google_url,
            publisher_domain=domain,
            publisher_name=publisher_name,
            description=description,
            published_at=published_at,
            rss_category=rss_category,
            assigned_category=assigned_cat,
        )
        db.session.add(story)

        # Mettre à jour ou créer le Publisher
        self._upsert_publisher(domain, publisher_name)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return 0

        return 1

    @staticmethod
    def _extract_domain(url):
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain or 'unknown'
        except Exception:
            return 'unknown'

    @staticmethod
    def _upsert_publisher(domain, name):
        publisher = Publisher.query.filter_by(domain=domain).first()
        now = datetime.utcnow()
        if publisher:
            publisher.total_appearances += 1
            publisher.last_seen = now
            if name and not publisher.name:
                publisher.name = name
        else:
            publisher = Publisher(
                domain=domain,
                name=name,
                total_appearances=1,
                first_seen=now,
                last_seen=now,
            )
            db.session.add(publisher)
