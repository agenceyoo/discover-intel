import re
import logging
from datetime import datetime, date

import requests
import feedparser

from app.collectors.base import BaseCollector
from app.extensions import db
from app.models import TrendingSearch, CategoryMapping

logger = logging.getLogger(__name__)

TRENDS_RSS_URL = 'https://trends.google.com/trending/rss?geo=FR'


class TrendsCollector(BaseCollector):
    COLLECTOR_TYPE = 'trends'

    def collect(self, app):
        with app.app_context():
            # Charger les patterns de categorisation
            keyword_mappings = CategoryMapping.query.filter(
                CategoryMapping.keyword_pattern.isnot(None)
            ).all()

            total = 0
            today = date.today()

            # Recuperer les tendances via RSS
            entries = self._get_trending_searches()

            for entry in entries:
                query_text = entry.get('title', '').strip()
                if not query_text:
                    continue

                # Verifier doublon
                existing = TrendingSearch.query.filter_by(
                    search_term=query_text, trend_date=today
                ).first()
                if existing:
                    continue

                # Volume de trafic
                traffic = entry.get('ht_approx_traffic', '')

                # Auto-categoriser
                category = self._categorize(query_text, keyword_mappings)

                trend = TrendingSearch(
                    search_term=query_text,
                    traffic_volume=traffic,
                    category=category,
                    trend_date=today,
                    source='google_trends_rss',
                )
                db.session.add(trend)
                total += 1

            db.session.commit()
            return total

    def _get_trending_searches(self):
        try:
            resp = requests.get(
                TRENDS_RSS_URL,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; DiscoverIntel/1.0)'},
                timeout=15,
            )
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
            return feed.entries
        except Exception as e:
            logger.error(f"Erreur recuperation tendances RSS: {e}")
            return []

    @staticmethod
    def _categorize(query_text, keyword_mappings):
        query_lower = query_text.lower()
        for mapping in keyword_mappings:
            if mapping.keyword_pattern:
                try:
                    if re.search(mapping.keyword_pattern, query_lower):
                        return mapping.category_fr
                except re.error:
                    continue
        return 'Autres'
