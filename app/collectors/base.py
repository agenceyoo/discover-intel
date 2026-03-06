import time
import traceback
from datetime import datetime
from app.extensions import db
from app.models import CollectionLog


class BaseCollector:
    COLLECTOR_TYPE = 'base'

    def run(self, app):
        log = CollectionLog(
            collector_type=self.COLLECTOR_TYPE,
            started_at=datetime.utcnow(),
            status='running',
        )
        with app.app_context():
            db.session.add(log)
            db.session.commit()
            log_id = log.id

        try:
            count = self.collect(app)
            with app.app_context():
                log = db.session.get(CollectionLog, log_id)
                log.status = 'success'
                log.items_collected = count or 0
                log.finished_at = datetime.utcnow()
                db.session.commit()
            return count
        except Exception as e:
            with app.app_context():
                log = db.session.get(CollectionLog, log_id)
                log.status = 'failed'
                log.error_message = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
                log.finished_at = datetime.utcnow()
                db.session.commit()
            raise

    def collect(self, app):
        raise NotImplementedError

    @staticmethod
    def rate_limit(seconds=1):
        time.sleep(seconds)
