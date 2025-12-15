import uuid
from datetime import datetime
from ..extensions import db


class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = db.Column(db.String(255), nullable=False)
    objective = db.Column(db.String(50), nullable=False)
    campaign_type = db.Column(db.String(50), nullable=False)

    daily_budget = db.Column(db.Integer, nullable=False)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)

    status = db.Column(db.String(20), nullable=False, default="DRAFT")

    google_campaign_id = db.Column(db.String(100), nullable=True)

    ad_group_name = db.Column(db.String(255), nullable=False)
    ad_headline = db.Column(db.String(255), nullable=False)
    ad_description = db.Column(db.Text, nullable=False)
    asset_url = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)