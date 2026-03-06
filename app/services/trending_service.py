from datetime import date, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models import TrendingSearch


def get_trending_searches(days=1, category=None, page=1, per_page=50):
    since = date.today() - timedelta(days=days - 1)
    q = TrendingSearch.query.filter(TrendingSearch.trend_date >= since)
    if category:
        q = q.filter_by(category=category)
    q = q.order_by(TrendingSearch.trend_date.desc(), TrendingSearch.id.desc())

    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [t.to_dict() for t in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
    }


def get_related_queries(query_text):
    trend = TrendingSearch.query.filter_by(search_term=query_text).order_by(
        TrendingSearch.trend_date.desc()
    ).first()
    if trend:
        return trend.to_dict()
    return None


def search_trends(keyword, days=30):
    since = date.today() - timedelta(days=days)
    results = TrendingSearch.query.filter(
        TrendingSearch.search_term.ilike(f'%{keyword}%'),
        TrendingSearch.trend_date >= since,
    ).order_by(TrendingSearch.trend_date.desc()).limit(50).all()
    return [t.to_dict() for t in results]


def get_categories_list():
    results = db.session.query(
        TrendingSearch.category, func.count(TrendingSearch.id)
    ).group_by(TrendingSearch.category).order_by(
        func.count(TrendingSearch.id).desc()
    ).all()
    return [{'name': r[0], 'count': r[1]} for r in results]
