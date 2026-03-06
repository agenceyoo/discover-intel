from flask import Blueprint, render_template, request
from app.services import historical_service

historical_bp = Blueprint('historical', __name__)


@historical_bp.route('/historical')
def index():
    days = request.args.get('days', 30, type=int)
    return render_template('historical.html', current_days=days)
