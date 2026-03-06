from flask import Blueprint, render_template, request
from app.services import publisher_service

publishers_bp = Blueprint('publishers', __name__)


@publishers_bp.route('/publishers')
def index():
    days = request.args.get('days', 7, type=int)
    limit = request.args.get('limit', 50, type=int)
    leaderboard = publisher_service.get_leaderboard(days=days, limit=limit)
    return render_template('publishers.html',
                           leaderboard=leaderboard,
                           current_days=days)


@publishers_bp.route('/publishers/<path:domain>')
def detail(domain):
    data = publisher_service.get_publisher_detail(domain)
    if not data:
        return render_template('publishers.html', leaderboard=[], current_days=7, error=f"Editeur '{domain}' non trouve")
    return render_template('publisher_detail.html', data=data, domain=domain)
