import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'discover.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = False
    SCHEDULER_ENABLED = True

    # Intervalles de collecte
    TRENDS_COLLECTION_INTERVAL_HOURS = 4
    NEWS_COLLECTION_INTERVAL_MINUTES = 30
    ARTICLE_SCRAPE_INTERVAL_MINUTES = 60
    ARTICLE_SCRAPE_BATCH_SIZE = 20

    # Google News France RSS
    GNEWS_BASE_URL = 'https://news.google.com/rss'
    GNEWS_PARAMS = '?hl=fr&gl=FR&ceid=FR:fr'
    GNEWS_TOPICS = [
        'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY',
        'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH'
    ]

    # Principaux éditeurs français
    TRACKED_PUBLISHERS = [
        'lemonde.fr', 'lefigaro.fr', 'liberation.fr', 'leparisien.fr',
        '20minutes.fr', 'lesechos.fr', 'lequipe.fr', 'mediapart.fr',
        'francetvinfo.fr', 'ouest-france.fr', 'sudouest.fr', 'bfmtv.com',
        'tf1info.fr', 'huffingtonpost.fr', 'nouvelobs.com', 'lexpress.fr',
        'cnews.fr', 'europe1.fr', 'rfi.fr', 'france24.com'
    ]

    # Requêtes HTTP
    REQUEST_TIMEOUT = 15
    REQUEST_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (compatible; DiscoverIntel/1.0; Research Tool)'
    }


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Obligatoire en production


class TestingConfig(Config):
    TESTING = True
    SCHEDULER_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
