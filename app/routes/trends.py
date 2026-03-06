from flask import Blueprint, render_template, request
from app.services import trending_service

trends_bp = Blueprint('trends', __name__)


@trends_bp.route('/trends')
def index():
    days = request.args.get('days', 1, type=int)
    category = request.args.get('category', None)
    page = request.args.get('page', 1, type=int)

    data = trending_service.get_trending_searches(days=days, category=category, page=page)
    categories = trending_service.get_categories_list()
    return render_template('trends.html',
                           trends_list=data['items'],
                           total=data['total'],
                           pages=data['pages'],
                           current_page=data['page'],
                           categories=categories,
                           current_days=days,
                           current_category=category)
