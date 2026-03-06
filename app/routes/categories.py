from flask import Blueprint, render_template, request
from app.services import category_service

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/categories')
def index():
    days = request.args.get('days', 7, type=int)
    breakdown = category_service.get_category_breakdown(days=days)
    return render_template('categories.html',
                           breakdown=breakdown,
                           current_days=days)


@categories_bp.route('/categories/<name>')
def detail(name):
    days = request.args.get('days', 7, type=int)
    page = request.args.get('page', 1, type=int)
    data = category_service.get_category_stories(name, days=days, page=page)
    publishers = category_service.get_category_publishers(name, days=days)
    return render_template('category_detail.html',
                           category_name=name,
                           stories_list=data['items'],
                           total=data['total'],
                           pages=data['pages'],
                           current_page=data['page'],
                           publishers=publishers,
                           current_days=days)
