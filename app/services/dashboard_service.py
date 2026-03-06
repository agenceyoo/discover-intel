from datetime import datetime, date, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models import NewsStory, TrendingSearch, Publisher, CollectionLog


def get_overview_metrics():
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    stories_today = NewsStory.query.filter(NewsStory.collected_at >= today_start).count()
    trends_today = TrendingSearch.query.filter_by(trend_date=today).count()
    publishers_today = db.session.query(
        func.count(func.distinct(NewsStory.publisher_domain))
    ).filter(NewsStory.collected_at >= today_start).scalar() or 0

    # Catégorie dominante aujourd'hui
    top_cat = db.session.query(
        NewsStory.assigned_category, func.count(NewsStory.id).label('cnt')
    ).filter(
        NewsStory.collected_at >= today_start
    ).group_by(NewsStory.assigned_category).order_by(func.count(NewsStory.id).desc()).first()

    return {
        'stories_today': stories_today,
        'trends_today': trends_today,
        'publishers_today': publishers_today,
        'top_category': top_cat[0] if top_cat else 'N/A',
    }


def get_trending_now(limit=10):
    today = date.today()
    trends = TrendingSearch.query.filter_by(trend_date=today).order_by(
        TrendingSearch.id.desc()
    ).limit(limit).all()
    return [t.to_dict() for t in trends]


def get_recent_stories(limit=20):
    stories = NewsStory.query.order_by(
        NewsStory.collected_at.desc()
    ).limit(limit).all()
    return [s.to_dict() for s in stories]


def get_category_distribution(days=1):
    since = datetime.utcnow() - timedelta(days=days)
    results = db.session.query(
        NewsStory.assigned_category, func.count(NewsStory.id).label('count')
    ).filter(
        NewsStory.collected_at >= since
    ).group_by(NewsStory.assigned_category).order_by(func.count(NewsStory.id).desc()).all()

    return {
        'labels': [r[0] or 'Autres' for r in results],
        'values': [r[1] for r in results],
    }


def get_publisher_top10(days=1):
    since = datetime.utcnow() - timedelta(days=days)
    results = db.session.query(
        NewsStory.publisher_domain, func.count(NewsStory.id).label('count')
    ).filter(
        NewsStory.collected_at >= since
    ).group_by(NewsStory.publisher_domain).order_by(
        func.count(NewsStory.id).desc()
    ).limit(10).all()

    return {
        'labels': [r[0] for r in results],
        'values': [r[1] for r in results],
    }


def get_collection_health():
    collectors = ['news', 'trends', 'articles']
    health = {}
    for c in collectors:
        last = CollectionLog.query.filter_by(
            collector_type=c
        ).order_by(CollectionLog.started_at.desc()).first()
        if last:
            health[c] = last.to_dict()
        else:
            health[c] = {'status': 'never_run', 'collector_type': c}
    return health
