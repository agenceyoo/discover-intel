from datetime import datetime
from flask import Blueprint, jsonify, request
from app.services import (
    dashboard_service,
    trending_service,
    publisher_service,
    category_service,
    content_service,
    historical_service,
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


def _response(data, **meta_extra):
    meta = {'generated_at': datetime.utcnow().isoformat()}
    meta.update(meta_extra)
    return jsonify({'status': 'ok', 'data': data, 'meta': meta})


# === Dashboard ===

@api_bp.route('/dashboard/metrics')
def dashboard_metrics():
    return _response(dashboard_service.get_overview_metrics())


@api_bp.route('/dashboard/category-distribution')
def dashboard_category_distribution():
    days = request.args.get('days', 1, type=int)
    return _response(dashboard_service.get_category_distribution(days=days), days=days)


@api_bp.route('/dashboard/publisher-top10')
def dashboard_publisher_top10():
    days = request.args.get('days', 1, type=int)
    return _response(dashboard_service.get_publisher_top10(days=days), days=days)


# === Tendances ===

@api_bp.route('/trends/current')
def trends_current():
    days = request.args.get('days', 1, type=int)
    category = request.args.get('category', None)
    page = request.args.get('page', 1, type=int)
    return _response(
        trending_service.get_trending_searches(days=days, category=category, page=page),
        days=days,
    )


@api_bp.route('/trends/search')
def trends_search():
    q = request.args.get('q', '')
    days = request.args.get('days', 30, type=int)
    if not q:
        return _response([])
    return _response(trending_service.search_trends(q, days=days))


@api_bp.route('/trends/<query>/related')
def trends_related(query):
    data = trending_service.get_related_queries(query)
    return _response(data)


# === Stories ===

@api_bp.route('/stories/recent')
def stories_recent():
    category = request.args.get('category', None)
    days = request.args.get('days', 7, type=int)
    page = request.args.get('page', 1, type=int)
    if category:
        data = category_service.get_category_stories(category, days=days, page=page)
    else:
        data = dashboard_service.get_recent_stories(limit=50)
    return _response(data, days=days)


# === Editeurs ===

@api_bp.route('/publishers/leaderboard')
def publishers_leaderboard():
    days = request.args.get('days', 7, type=int)
    limit = request.args.get('limit', 50, type=int)
    return _response(publisher_service.get_leaderboard(days=days, limit=limit), days=days)


@api_bp.route('/publishers/<path:domain>/trend')
def publisher_trend(domain):
    days = request.args.get('days', 30, type=int)
    return _response(publisher_service.get_publisher_trend(domain, days=days), days=days)


@api_bp.route('/publishers/<path:domain>/categories')
def publisher_categories(domain):
    data = publisher_service.get_publisher_detail(domain)
    if not data:
        return jsonify({'status': 'error', 'message': 'Publisher not found'}), 404
    return _response(data['categories'])


# === Categories ===

@api_bp.route('/categories/breakdown')
def categories_breakdown():
    days = request.args.get('days', 7, type=int)
    return _response(category_service.get_category_breakdown(days=days), days=days)


@api_bp.route('/categories/<name>/trend')
def category_trend(name):
    days = request.args.get('days', 30, type=int)
    return _response(category_service.get_category_trends_over_time(days=days), days=days)


@api_bp.route('/categories/<name>/publishers')
def category_publishers(name):
    days = request.args.get('days', 7, type=int)
    return _response(category_service.get_category_publishers(name, days=days), days=days)


# === Contenu ===

@api_bp.route('/content/formats')
def content_formats():
    days = request.args.get('days', 7, type=int)
    return _response(content_service.get_format_insights(days=days), days=days)


@api_bp.route('/content/word-count-dist')
def content_word_count_dist():
    days = request.args.get('days', 7, type=int)
    return _response(content_service.get_word_count_distribution(days=days), days=days)


@api_bp.route('/content/title-length-dist')
def content_title_length_dist():
    days = request.args.get('days', 7, type=int)
    return _response(content_service.get_title_length_distribution(days=days), days=days)


# === Historique ===

@api_bp.route('/historical/volume')
def historical_volume():
    days = request.args.get('days', 30, type=int)
    return _response(historical_service.get_volume_over_time(days=days), days=days)


@api_bp.route('/historical/categories')
def historical_categories():
    days = request.args.get('days', 30, type=int)
    return _response(historical_service.get_category_evolution(days=days), days=days)


@api_bp.route('/historical/publishers')
def historical_publishers():
    domains = request.args.get('domains', '')
    days = request.args.get('days', 30, type=int)
    domain_list = [d.strip() for d in domains.split(',') if d.strip()]
    if not domain_list:
        return _response({'labels': [], 'datasets': []})
    return _response(historical_service.get_publisher_evolution(domain_list, days=days), days=days)


@api_bp.route('/historical/topic')
def historical_topic():
    q = request.args.get('q', '')
    days = request.args.get('days', 30, type=int)
    if not q:
        return _response({'labels': [], 'items': []})
    return _response(historical_service.get_topic_evolution(q, days=days), days=days)


# === Collection ===

@api_bp.route('/collection/status')
def collection_status():
    return _response(dashboard_service.get_collection_health())
