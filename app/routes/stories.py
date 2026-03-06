from flask import Blueprint, render_template, request
from app.services import category_service

stories_bp = Blueprint('stories', __name__)


@stories_bp.route('/stories')
def index():
    category = request.args.get('category', None)
    days = request.args.get('days', 7, type=int)
    page = request.args.get('page', 1, type=int)

    data = category_service.get_category_stories(category, days=days, page=page) if category else _get_all_stories(days, page)
    categories = category_service.get_category_breakdown(days=days)
    return render_template('stories.html',
                           stories_list=data['items'],
                           total=data['total'],
                           pages=data['pages'],
                           current_page=data['page'],
                           categories=categories,
                           current_category=category,
                           current_days=days)


def _get_all_stories(days, page):
    from datetime import datetime, timedelta
    from app.models import NewsStory
    since = datetime.utcnow() - timedelta(days=days)
    q = NewsStory.query.filter(
        NewsStory.collected_at >= since
    ).order_by(NewsStory.collected_at.desc())
    pagination = q.paginate(page=page, per_page=20, error_out=False)
    return {
        'items': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
    }
