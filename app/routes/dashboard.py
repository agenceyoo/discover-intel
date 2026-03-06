from flask import Blueprint, render_template
from app.services import dashboard_service

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    metrics = dashboard_service.get_overview_metrics()
    trending = dashboard_service.get_trending_now(limit=10)
    stories = dashboard_service.get_recent_stories(limit=15)
    health = dashboard_service.get_collection_health()
    return render_template('dashboard.html',
                           metrics=metrics,
                           trending=trending,
                           stories=stories,
                           health=health)
