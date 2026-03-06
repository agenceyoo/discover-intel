import os
from flask import Flask
from app.extensions import db, scheduler
from app.models import CategoryMapping


DEFAULT_CATEGORIES = [
    {'google_news_topic': 'WORLD', 'category_fr': 'International'},
    {'google_news_topic': 'NATION', 'category_fr': 'Politique'},
    {'google_news_topic': 'BUSINESS', 'category_fr': 'Economie'},
    {'google_news_topic': 'TECHNOLOGY', 'category_fr': 'Technologie'},
    {'google_news_topic': 'ENTERTAINMENT', 'category_fr': 'Divertissement'},
    {'google_news_topic': 'SPORTS', 'category_fr': 'Sport'},
    {'google_news_topic': 'SCIENCE', 'category_fr': 'Science'},
    {'google_news_topic': 'HEALTH', 'category_fr': 'Sante'},
    {'google_news_topic': 'GENERAL', 'category_fr': 'Actualites'},
    # Keyword patterns pour les tendances Google Trends
    {'keyword_pattern': r'football|rugby|tennis|ligue 1|psg|om|ol|euro 2026|coupe|nba|f1|sport',
     'category_fr': 'Sport'},
    {'keyword_pattern': r'iphone|samsung|google|apple|ia|intelligence artificielle|tech|app|robot',
     'category_fr': 'Technologie'},
    {'keyword_pattern': r'macron|assemblee|senat|election|politique|gouvernement|ministre|loi|reforme',
     'category_fr': 'Politique'},
    {'keyword_pattern': r'film|serie|musique|concert|cinema|netflix|disney|spectacle|artiste',
     'category_fr': 'Divertissement'},
    {'keyword_pattern': r'bourse|cac 40|economie|inflation|emploi|salaire|entreprise|startup',
     'category_fr': 'Economie'},
    {'keyword_pattern': r'sante|covid|medicament|hopital|medecin|vaccin|maladie|cancer',
     'category_fr': 'Sante'},
    {'keyword_pattern': r'climat|environnement|rechauffement|ecologie|pollution|biodiversite',
     'category_fr': 'Environnement'},
    {'keyword_pattern': r'espace|nasa|planete|decouverte|recherche|science|etude|scientifique',
     'category_fr': 'Science'},
]


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=True)

    config_map = {
        'development': 'app.config.DevelopmentConfig',
        'production': 'app.config.ProductionConfig',
        'testing': 'app.config.TestingConfig',
    }
    app.config.from_object(config_map.get(config_name, config_map['development']))

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        _seed_categories()
        # Activer WAL mode pour SQLite
        with db.engine.connect() as conn:
            conn.execute(db.text("PRAGMA journal_mode=WAL"))
            conn.commit()

    # Enregistrer les blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # Démarrer le scheduler
    if app.config.get('SCHEDULER_ENABLED'):
        run_main = os.environ.get('WERKZEUG_RUN_MAIN')
        if not app.debug or run_main == 'true':
            scheduler.init_app(app)
            from app.collectors.scheduler_jobs import register_jobs
            register_jobs(scheduler, app)
            scheduler.start()

    return app


def _seed_categories():
    if CategoryMapping.query.first() is not None:
        return
    for cat in DEFAULT_CATEGORIES:
        mapping = CategoryMapping(
            keyword_pattern=cat.get('keyword_pattern'),
            google_news_topic=cat.get('google_news_topic'),
            category_fr=cat['category_fr'],
        )
        db.session.add(mapping)
    db.session.commit()
