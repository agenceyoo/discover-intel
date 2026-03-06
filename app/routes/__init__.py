def register_blueprints(app):
    from app.routes.dashboard import dashboard_bp
    from app.routes.trends import trends_bp
    from app.routes.stories import stories_bp
    from app.routes.publishers import publishers_bp
    from app.routes.categories import categories_bp
    from app.routes.content import content_bp
    from app.routes.historical import historical_bp
    from app.routes.api import api_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(trends_bp)
    app.register_blueprint(stories_bp)
    app.register_blueprint(publishers_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(historical_bp)
    app.register_blueprint(api_bp)
