from datetime import datetime
from app.extensions import db
from app.models.campaign import Campaign
from app.services.google_ads import GoogleAdsService
from app.errors.exceptions import ValidationError, NotFoundError


class CampaignService:
    @staticmethod
    def create_campaign(data: dict) -> Campaign:
        required_fields = [
            "name",
            "objective",
            "campaign_type",
            "daily_budget",
            "start_date",
            "ad_group_name",
            "ad_headline",
            "ad_description",
        ]

        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing field: {field}")

        try:
            campaign = Campaign(
                name=data["name"],
                objective=data["objective"],
                campaign_type=data["campaign_type"],
                daily_budget=data["daily_budget"],
                start_date=datetime.fromisoformat(data["start_date"]).date(),
                end_date=datetime.fromisoformat(data["end_date"]).date()
                if data.get("end_date") else None,
                ad_group_name=data["ad_group_name"],
                ad_headline=data["ad_headline"],
                ad_description=data["ad_description"],
                asset_url=data.get("asset_url"),
                status="DRAFT"
            )
            db.session.add(campaign)
            db.session.commit()
            return campaign

        except Exception:
            db.session.rollback()
            raise
    
    @staticmethod
    def list_campaigns():
        return Campaign.query.order_by(Campaign.created_at.desc()).all()

    @staticmethod
    def publish_campaign(campaign_id):
        campaign = Campaign.query.get(campaign_id)

        if not campaign:
            raise NotFoundError("Campaign not found")

        if campaign.status != "DRAFT":
            raise ValidationError("Only DRAFT campaigns can be published")

        try:
            google_ads = GoogleAdsService()

            budget_resource = google_ads.create_campaign_budget(
                daily_budget_micros=campaign.daily_budget * 1_000_000,
                name=f"{campaign.name} Budget",
            )
            google_campaign_resource = google_ads.create_paused_campaign(
                name=campaign.name,
                budget_resource_name=budget_resource,
            )
            ad_group_resource = google_ads.create_ad_group(
                campaign_resource_name=google_campaign_resource,
                ad_group_name=campaign.ad_group_name,
            )
            google_ads.create_responsive_search_ad(
                ad_group_resource_name=ad_group_resource,
                headline=campaign.ad_headline,
                description=campaign.ad_description,
                final_url=campaign.asset_url or "https://example.com",
            )

            campaign.google_campaign_id = google_campaign_resource
            campaign.status = "PUBLISHED"

            db.session.commit()

            return campaign

        except Exception:
            db.session.rollback()
            raise
    
    @staticmethod
    def pause_campaign(campaign_id):
        campaign = Campaign.query.get(campaign_id)

        if not campaign:
            raise NotFoundError("Campaign not found")

        if not campaign.google_campaign_id:
            raise ValidationError("Campaign not published to Google Ads")

        try:
            google_ads = GoogleAdsService()
            google_ads.pause_campaign(campaign.google_campaign_id)

            campaign.status = "PAUSED"
            db.session.commit()

            return campaign

        except Exception:
            db.session.rollback()
            raise