from flask import Blueprint, request, jsonify
from app.services.campaign_service import CampaignService
from app.errors.exceptions import ValidationError

campaigns_bp = Blueprint("campaigns", __name__, url_prefix="/api/campaigns")


@campaigns_bp.route("", methods=["POST"])
def create_campaign():
    data = request.get_json()

    if not data:
        raise ValidationError("Invalid JSON body")

    campaign = CampaignService.create_campaign(data)

    return jsonify({
        "id": str(campaign.id),
        "status": campaign.status
    }), 201


@campaigns_bp.route("", methods=["GET"])
def list_campaigns():
    campaigns = CampaignService.list_campaigns()

    return jsonify([
        {
            "id": str(c.id),
            "name": c.name,
            "objective": c.objective,
            "campaign_type": c.campaign_type,
            "daily_budget": c.daily_budget,
            "status": c.status,
            "google_campaign_id": c.google_campaign_id,
            "created_at": c.created_at.isoformat()
        }
        for c in campaigns
    ]), 200


@campaigns_bp.route("/<uuid:campaign_id>/publish", methods=["POST"])
def publish_campaign(campaign_id):
    campaign = CampaignService.publish_campaign(campaign_id)

    return jsonify({
        "id": str(campaign.id),
        "status": campaign.status,
        "google_campaign_id": campaign.google_campaign_id
    }), 200


@campaigns_bp.route("/<uuid:campaign_id>/pause", methods=["POST"])
def pause_campaign(campaign_id):
    campaign = CampaignService.pause_campaign(campaign_id)

    return jsonify({
        "id": str(campaign.id),
        "status": campaign.status
    }), 200