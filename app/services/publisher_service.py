from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models import NewsStory, Publisher, ArticleMetadata


def get_leaderboard(days=7, limit=50):
    since = datetime.utcnow() - timedelta(days=days)
    results = db.session.query(
        NewsStory.publisher_domain,
        NewsStory.publisher_name,
        func.count(NewsStory.id).label('count'),
    ).filter(
        NewsStory.collected_at >= since
    ).group_by(
        NewsStory.publisher_domain, NewsStory.publisher_name
    ).order_by(func.count(NewsStory.id).desc()).limit(limit).all()

    return [{
        'domain': r[0],
        'name': r[1],
        'count': r[2],
        'rank': i + 1,
    } for i, r in enumerate(results)]


def get_publisher_detail(domain):
    publisher = Publisher.query.filter_by(domain=domain).first()
    if not publisher:
        return None

    # Répartition par catégorie
    cats = db.session.query(
        NewsStory.assigned_category, func.count(NewsStory.id)
    ).filter_by(publisher_domain=domain).group_by(
        NewsStory.assigned_category
    ).all()

    # Stats articles
    stories_with_meta = db.session.query(
        func.avg(ArticleMetadata.word_count),
        func.avg(ArticleMetadata.title_length),
        func.sum(db.cast(ArticleMetadata.has_video, db.Integer)),
        func.count(ArticleMetadata.id),
    ).join(NewsStory).filter(
        NewsStory.publisher_domain == domain,
        ArticleMetadata.scrape_status == 'success',
    ).first()

    total_meta = stories_with_meta[3] or 0

    return {
        'publisher': publisher.to_dict(),
        'categories': {
            'labels': [c[0] or 'Autres' for c in cats],
            'values': [c[1] for c in cats],
        },
        'content_stats': {
            'avg_word_count': round(stories_with_meta[0] or 0),
            'avg_title_length': round(stories_with_meta[1] or 0),
            'video_rate': round((stories_with_meta[2] or 0) / total_meta * 100, 1) if total_meta > 0 else 0,
        }
    }


def get_publisher_trend(domain, days=30):
    since = datetime.utcnow() - timedelta(days=days)
    results = db.session.query(
        func.date(NewsStory.collected_at).label('day'),
        func.count(NewsStory.id).label('count'),
    ).filter(
        NewsStory.publisher_domain == domain,
        NewsStory.collected_at >= since,
    ).group_by(func.date(NewsStory.collected_at)).order_by('day').all()

    return {
        'labels': [str(r[0]) for r in results],
        'values': [r[1] for r in results],
    }
