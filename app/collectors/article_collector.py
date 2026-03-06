import logging
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.collectors.base import BaseCollector
from app.extensions import db
from app.models import NewsStory, ArticleMetadata

logger = logging.getLogger(__name__)


class ArticleCollector(BaseCollector):
    COLLECTOR_TYPE = 'articles'

    def collect(self, app):
        with app.app_context():
            batch_size = app.config.get('ARTICLE_SCRAPE_BATCH_SIZE', 20)
            headers = app.config.get('REQUEST_HEADERS', {})
            timeout = app.config.get('REQUEST_TIMEOUT', 15)

            # Trouver les stories sans métadonnées
            scraped_ids = db.session.query(ArticleMetadata.news_story_id).subquery()
            pending = NewsStory.query.filter(
                ~NewsStory.id.in_(db.session.query(scraped_ids))
            ).order_by(NewsStory.collected_at.desc()).limit(batch_size).all()

            total = 0
            for story in pending:
                try:
                    self._scrape_article(story, headers, timeout)
                    total += 1
                except Exception as e:
                    logger.warning(f"Erreur scraping {story.url[:80]}: {e}")
                    meta = ArticleMetadata(
                        news_story_id=story.id,
                        scrape_status='failed',
                        scraped_at=datetime.utcnow(),
                    )
                    db.session.add(meta)
                time.sleep(3)  # Rate limit

            db.session.commit()
            return total

    def _scrape_article(self, story, headers, timeout):
        response = requests.get(story.url, headers=headers, timeout=timeout, allow_redirects=True)

        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            meta = ArticleMetadata(
                news_story_id=story.id,
                scrape_status='skipped',
                scraped_at=datetime.utcnow(),
            )
            db.session.add(meta)
            return

        soup = BeautifulSoup(response.text, 'lxml')

        # Open Graph
        og_title = self._get_meta(soup, 'og:title')
        og_description = self._get_meta(soup, 'og:description')
        og_image = self._get_meta(soup, 'og:image')
        og_type = self._get_meta(soup, 'og:type')

        # Word count approximatif
        article_text = self._extract_text(soup)
        word_count = len(article_text.split()) if article_text else None

        # Longueur du titre
        title = og_title or story.title
        title_length = len(title) if title else None

        # Vidéo
        has_video = bool(
            soup.find('video')
            or soup.find('iframe', src=lambda s: s and ('youtube' in s or 'dailymotion' in s or 'vimeo' in s))
        )

        # Données structurées
        has_structured_data = bool(soup.find('script', type='application/ld+json'))

        # Auteur
        author = (
            self._get_meta(soup, 'author')
            or self._get_meta(soup, 'article:author')
        )
        if not author:
            author_tag = soup.find('meta', attrs={'name': 'author'})
            if author_tag:
                author = author_tag.get('content')

        # Langue
        language = None
        html_tag = soup.find('html')
        if html_tag:
            language = html_tag.get('lang', '')[:10]

        meta = ArticleMetadata(
            news_story_id=story.id,
            og_title=og_title,
            og_description=og_description,
            og_image=og_image,
            og_type=og_type,
            word_count=word_count,
            title_length=title_length,
            has_video=has_video,
            has_structured_data=has_structured_data,
            author=author,
            language=language,
            scrape_status='success',
            scraped_at=datetime.utcnow(),
        )
        db.session.add(meta)

    @staticmethod
    def _get_meta(soup, property_name):
        tag = soup.find('meta', property=property_name)
        if tag:
            return tag.get('content', '').strip()
        tag = soup.find('meta', attrs={'name': property_name})
        if tag:
            return tag.get('content', '').strip()
        return None

    @staticmethod
    def _extract_text(soup):
        # Retirer scripts et styles
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()

        # Chercher le contenu principal
        article = soup.find('article') or soup.find('main') or soup.find('div', class_='article-body')
        if article:
            return article.get_text(separator=' ', strip=True)

        # Fallback: paragraphes
        paragraphs = soup.find_all('p')
        return ' '.join(p.get_text(strip=True) for p in paragraphs)
