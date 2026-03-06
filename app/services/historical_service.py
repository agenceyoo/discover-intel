from datetime import datetime, timedelta, date
from sqlalchemy import func
from app.extensions import db
from app.models import NewsStory, TrendingSearch


def get_volume_over_time(days=30):
    since = datetime.utcnow() - timedelta(days=days)
    results = db.session.query(
        func.date(NewsStory.collected_at).label('day'),
        func.count(NewsStory.id).label('count'),
    ).filter(
        NewsStory.collected_at >= since
    ).group_by(func.date(NewsStory.collected_at)).order_by('day').all()

    return {
        'labels': [str(r[0]) for r in results],
        'values': [r[1] for r in results],
    }


def get_category_evolution(days=30):
    from app.services.category_service import get_category_trends_over_time
    return get_category_trends_over_time(days)


def get_publisher_evolution(domains, days=30):
    since = datetime.utcnow() - timedelta(days=days)

    datasets = []
    all_labels = set()

    for domain in domains:
        results = db.session.query(
            func.date(NewsStory.collected_at).label('day'),
            func.count(NewsStory.id).label('count'),
        ).filter(
            NewsStory.publisher_domain == domain,
            NewsStory.collected_at >= since,
        ).group_by(func.date(NewsStory.collected_at)).order_by('day').all()

        day_map = {str(r[0]): r[1] for r in results}
        all_labels.update(day_map.keys())
        datasets.append({'domain': domain, 'day_map': day_map})

    labels = sorted(all_labels)
    return {
        'labels': labels,
        'datasets': [{
            'label': ds['domain'],
            'data': [ds['day_map'].get(d, 0) for d in labels],
        } for ds in datasets],
    }


def get_topic_evolution(query_text, days=30):
    since = date.today() - timedelta(days=days)
    results = TrendingSearch.query.filter(
        TrendingSearch.search_term.ilike(f'%{query_text}%'),
        TrendingSearch.trend_date >= since,
    ).order_by(TrendingSearch.trend_date.asc()).all()

    return {
        'labels': [t.trend_date.isoformat() for t in results],
        'items': [t.to_dict() for t in results],
    }
