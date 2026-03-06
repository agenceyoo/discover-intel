from flask import Blueprint, render_template, request
from app.services import content_service

content_bp = Blueprint('content', __name__)


@content_bp.route('/content')
def index():
    days = request.args.get('days', 7, type=int)
    insights = content_service.get_format_insights(days=days)
    return render_template('content.html',
                           insights=insights,
                           current_days=days)
