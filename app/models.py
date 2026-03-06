from datetime import datetime, date
from app.extensions import db


class TrendingSearch(db.Model):
    __tablename__ = 'trending_search'

    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String(500), nullable=False)
    traffic_volume = db.Column(db.String(50))
    related_queries = db.Column(db.Text)  # JSON
    related_topics = db.Column(db.Text)   # JSON
    category = db.Column(db.String(100), default='Autres')
    trend_date = db.Column(db.Date, nullable=False, index=True, default=date.today)
    collected_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    source = db.Column(db.String(50), nullable=False, default='google_trends')

    __table_args__ = (
        db.UniqueConstraint('search_term', 'trend_date', name='uq_query_date'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'query': self.search_term,
            'traffic_volume': self.traffic_volume,
            'related_queries': self.related_queries,
            'related_topics': self.related_topics,
            'category': self.category,
            'trend_date': self.trend_date.isoformat() if self.trend_date else None,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
        }


class NewsStory(db.Model):
    __tablename__ = 'news_story'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000), nullable=False)
    url = db.Column(db.String(2000), nullable=False, unique=True)
    google_news_url = db.Column(db.String(2000))
    publisher_domain = db.Column(db.String(500), nullable=False, index=True)
    publisher_name = db.Column(db.String(500))
    description = db.Column(db.Text)
    published_at = db.Column(db.DateTime, index=True)
    rss_category = db.Column(db.String(100), nullable=False, index=True)
    assigned_category = db.Column(db.String(100))
    collected_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    metadata_info = db.relationship('ArticleMetadata', backref='story', uselist=False, lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'publisher_domain': self.publisher_domain,
            'publisher_name': self.publisher_name,
            'description': self.description,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'rss_category': self.rss_category,
            'assigned_category': self.assigned_category,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
        }


class ArticleMetadata(db.Model):
    __tablename__ = 'article_metadata'

    id = db.Column(db.Integer, primary_key=True)
    news_story_id = db.Column(db.Integer, db.ForeignKey('news_story.id'), unique=True, nullable=False)
    og_title = db.Column(db.String(1000))
    og_description = db.Column(db.Text)
    og_image = db.Column(db.String(2000))
    og_type = db.Column(db.String(100))
    word_count = db.Column(db.Integer)
    title_length = db.Column(db.Integer)
    has_video = db.Column(db.Boolean, default=False)
    has_structured_data = db.Column(db.Boolean, default=False)
    author = db.Column(db.String(500))
    language = db.Column(db.String(10))
    scraped_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    scrape_status = db.Column(db.String(20), nullable=False, default='pending')

    def to_dict(self):
        return {
            'id': self.id,
            'news_story_id': self.news_story_id,
            'og_title': self.og_title,
            'og_image': self.og_image,
            'og_type': self.og_type,
            'word_count': self.word_count,
            'title_length': self.title_length,
            'has_video': self.has_video,
            'has_structured_data': self.has_structured_data,
            'author': self.author,
            'scrape_status': self.scrape_status,
        }


class Publisher(db.Model):
    __tablename__ = 'publisher'

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(500), nullable=False, unique=True)
    name = db.Column(db.String(500))
    total_appearances = db.Column(db.Integer, default=0)
    first_seen = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'domain': self.domain,
            'name': self.name,
            'total_appearances': self.total_appearances,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
        }


class CategoryMapping(db.Model):
    __tablename__ = 'category_mapping'

    id = db.Column(db.Integer, primary_key=True)
    keyword_pattern = db.Column(db.String(500))
    google_news_topic = db.Column(db.String(100))
    category_fr = db.Column(db.String(100), nullable=False)


class CollectionLog(db.Model):
    __tablename__ = 'collection_log'

    id = db.Column(db.Integer, primary_key=True)
    collector_type = db.Column(db.String(50), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False, default='running')
    items_collected = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'collector_type': self.collector_type,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'status': self.status,
            'items_collected': self.items_collected,
        }
