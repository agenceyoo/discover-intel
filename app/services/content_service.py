from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models import ArticleMetadata, NewsStory


def get_format_insights(days=7):
    since = datetime.utcnow() - timedelta(days=days)

    stats = db.session.query(
        func.avg(ArticleMetadata.word_count),
        func.avg(ArticleMetadata.title_length),
        func.sum(db.cast(ArticleMetadata.has_video, db.Integer)),
        func.sum(db.cast(ArticleMetadata.has_structured_data, db.Integer)),
        func.count(ArticleMetadata.id),
    ).join(NewsStory).filter(
        NewsStory.collected_at >= since,
        ArticleMetadata.scrape_status == 'success',
    ).first()

    total = stats[4] or 1
    has_image = db.session.query(func.count(ArticleMetadata.id)).join(NewsStory).filter(
        NewsStory.collected_at >= since,
        ArticleMetadata.scrape_status == 'success',
        ArticleMetadata.og_image.isnot(None),
        ArticleMetadata.og_image != '',
    ).scalar() or 0

    return {
        'avg_word_count': round(stats[0] or 0),
        'avg_title_length': round(stats[1] or 0),
        'video_rate': round((stats[2] or 0) / total * 100, 1),
        'structured_data_rate': round((stats[3] or 0) / total * 100, 1),
        'image_rate': round(has_image / total * 100, 1),
        'total_articles': total,
    }


def get_word_count_distribution(days=7):
    since = datetime.utcnow() - timedelta(days=days)

    articles = db.session.query(ArticleMetadata.word_count).join(NewsStory).filter(
        NewsStory.collected_at >= since,
        ArticleMetadata.scrape_status == 'success',
        ArticleMetadata.word_count.isnot(None),
    ).all()

    # Créer des buckets
    buckets = {
        '0-200': 0, '200-400': 0, '400-600': 0, '600-800': 0,
        '800-1000': 0, '1000-1500': 0, '1500-2000': 0, '2000+': 0,
    }
    for (wc,) in articles:
        if wc < 200:
            buckets['0-200'] += 1
        elif wc < 400:
            buckets['200-400'] += 1
        elif wc < 600:
            buckets['400-600'] += 1
        elif wc < 800:
            buckets['600-800'] += 1
        elif wc < 1000:
            buckets['800-1000'] += 1
        elif wc < 1500:
            buckets['1000-1500'] += 1
        elif wc < 2000:
            buckets['1500-2000'] += 1
        else:
            buckets['2000+'] += 1

    return {
        'labels': list(buckets.keys()),
        'values': list(buckets.values()),
    }


def get_title_length_distribution(days=7):
    since = datetime.utcnow() - timedelta(days=days)

    articles = db.session.query(ArticleMetadata.title_length).join(NewsStory).filter(
        NewsStory.collected_at >= since,
        ArticleMetadata.scrape_status == 'success',
        ArticleMetadata.title_length.isnot(None),
    ).all()

    buckets = {
        '0-30': 0, '30-50': 0, '50-70': 0, '70-90': 0,
        '90-110': 0, '110-130': 0, '130+': 0,
    }
    for (tl,) in articles:
        if tl < 30:
            buckets['0-30'] += 1
        elif tl < 50:
            buckets['30-50'] += 1
        elif tl < 70:
            buckets['50-70'] += 1
        elif tl < 90:
            buckets['70-90'] += 1
        elif tl < 110:
            buckets['90-110'] += 1
        elif tl < 130:
            buckets['110-130'] += 1
        else:
            buckets['130+'] += 1

    return {
        'labels': list(buckets.keys()),
        'values': list(buckets.values()),
    }
