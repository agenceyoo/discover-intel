from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models import NewsStory


def get_category_breakdown(days=7):
    since = datetime.utcnow() - timedelta(days=days)
    results = db.session.query(
        NewsStory.assigned_category, func.count(NewsStory.id).label('count')
    ).filter(
        NewsStory.collected_at >= since
    ).group_by(NewsStory.assigned_category).order_by(
        func.count(NewsStory.id).desc()
    ).all()

    total = sum(r[1] for r in results) or 1
    return [{
        'category': r[0] or 'Autres',
        'count': r[1],
        'percentage': round(r[1] / total * 100, 1),
    } for r in results]


def get_category_stories(category, days=7, page=1, per_page=20):
    since = datetime.utcnow() - timedelta(days=days)
    query = NewsStory.query.filter(
        NewsStory.assigned_category == category,
        NewsStory.collected_at >= since,
    ).order_by(NewsStory.collected_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
    }


def get_category_publishers(category, days=7, limit=10):
    since = datetime.utcnow() - timedelta(days=days)
    results = db.session.query(
        NewsStory.publisher_domain,
        func.count(NewsStory.id).label('count'),
    ).filter(
        NewsStory.assigned_category == category,
        NewsStory.collected_at >= since,
    ).group_by(NewsStory.publisher_domain).order_by(
        func.count(NewsStory.id).desc()
    ).limit(limit).all()

    return [{'domain': r[0], 'count': r[1]} for r in results]


def get_category_trends_over_time(days=30):
    since = datetime.utcnow() - timedelta(days=days)
    results = db.session.query(
        func.date(NewsStory.collected_at).label('day'),
        NewsStory.assigned_category,
        func.count(NewsStory.id).label('count'),
    ).filter(
        NewsStory.collected_at >= since
    ).group_by(
        func.date(NewsStory.collected_at), NewsStory.assigned_category
    ).order_by('day').all()

    # Transformer en format adapté pour stacked area chart
    days_data = {}
    categories = set()
    for r in results:
        day = str(r[0])
        cat = r[1] or 'Autres'
        categories.add(cat)
        if day not in days_data:
            days_data[day] = {}
        days_data[day][cat] = r[2]

    labels = sorted(days_data.keys())
    datasets = []
    for cat in sorted(categories):
        datasets.append({
            'label': cat,
            'data': [days_data.get(d, {}).get(cat, 0) for d in labels],
        })

    return {'labels': labels, 'datasets': datasets}
