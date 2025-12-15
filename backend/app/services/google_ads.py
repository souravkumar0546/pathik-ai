from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from app.config import Config
from google.auth.exceptions import TransportError
import requests
import urllib3

class GoogleAdsService:
    def __init__(self):
        if not all([
            Config.GOOGLE_ADS_DEVELOPER_TOKEN,
            Config.GOOGLE_ADS_CLIENT_ID,
            Config.GOOGLE_ADS_CLIENT_SECRET,
            Config.GOOGLE_ADS_REFRESH_TOKEN,
            Config.GOOGLE_ADS_LOGIN_CUSTOMER_ID,
            Config.GOOGLE_ADS_CUSTOMER_ID,
        ]):
            raise RuntimeError("Google Ads credentials are not fully configured")

        self.customer_id = Config.GOOGLE_ADS_CUSTOMER_ID

        self.client = GoogleAdsClient.load_from_dict({
            "developer_token": Config.GOOGLE_ADS_DEVELOPER_TOKEN,
            "client_id": Config.GOOGLE_ADS_CLIENT_ID,
            "client_secret": Config.GOOGLE_ADS_CLIENT_SECRET,
            "refresh_token": Config.GOOGLE_ADS_REFRESH_TOKEN,
            "login_customer_id": Config.GOOGLE_ADS_LOGIN_CUSTOMER_ID,
            "use_proto_plus": True,
        })
    
    def raise_google_error(self, ex: GoogleAdsException):
        messages = [
            f"{error.error_code}: {error.message}"
            for error in ex.failure.errors
        ]
        raise RuntimeError(" | ".join(messages)) from ex
    
    def raise_network_error(self, ex: Exception):
        raise RuntimeError("Google Ads service unavailable") from ex

    def create_campaign_budget(self, daily_budget_micros: int, name: str):
        try:
            budget_service = self.client.get_service("CampaignBudgetService")
            operation = self.client.get_type("CampaignBudgetOperation")

            budget = operation.create
            budget.name = name
            budget.amount_micros = daily_budget_micros
            budget.delivery_method = (
                self.client.enums.BudgetDeliveryMethodEnum.STANDARD
            )

            response = budget_service.mutate_campaign_budgets(
                customer_id=self.customer_id,
                operations=[operation],
            )

            return response.results[0].resource_name

        except GoogleAdsException as ex:
            self.raise_google_error(ex)
        except (TransportError, requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as ex:
            self.raise_network_error(ex)


    def create_paused_campaign(self, name: str, budget_resource_name: str):
        try:
            campaign_service = self.client.get_service("CampaignService")
            operation = self.client.get_type("CampaignOperation")

            campaign = operation.create
            campaign.name = name
            campaign.campaign_budget = budget_resource_name
            campaign.status = self.client.enums.CampaignStatusEnum.PAUSED
            campaign.advertising_channel_type = (
                self.client.enums.AdvertisingChannelTypeEnum.SEARCH
            )

            response = campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[operation],
            )

            return response.results[0].resource_name
        except GoogleAdsException as ex:
            self.raise_google_error(ex)
        except (TransportError, requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as ex:
            self.raise_network_error(ex)
        
    def create_ad_group(self, campaign_resource_name: str, ad_group_name: str):
        try:
            ad_group_service = self.client.get_service("AdGroupService")
            operation = self.client.get_type("AdGroupOperation")

            ad_group = operation.create
            ad_group.name = ad_group_name
            ad_group.campaign = campaign_resource_name
            ad_group.status = self.client.enums.AdGroupStatusEnum.PAUSED
            ad_group.type_ = self.client.enums.AdGroupTypeEnum.SEARCH_STANDARD

            response = ad_group_service.mutate_ad_groups(
                customer_id=self.customer_id,
                operations=[operation],
            )

            return response.results[0].resource_name

        except GoogleAdsException as ex:
            self.raise_google_error(ex)
        except (TransportError, requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as ex:
            self.raise_network_error(ex)

    def create_responsive_search_ad(
        self,
        ad_group_resource_name: str,
        headline: str,
        description: str,
        final_url: str,
    ):
        try:
            ad_group_ad_service = self.client.get_service("AdGroupAdService")
            operation = self.client.get_type("AdGroupAdOperation")

            ad_group_ad = operation.create
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.status = self.client.enums.AdGroupAdStatusEnum.PAUSED

            ad = ad_group_ad.ad
            ad.final_urls.append(final_url)

            rsa = ad.responsive_search_ad

            rsa.headlines.add().text = headline
            rsa.headlines.add().text = f"{headline} – Official"
            rsa.headlines.add().text = "Get Started Today"

            rsa.descriptions.add().text = description
            rsa.descriptions.add().text = "Simple. Fast. Reliable."

            response = ad_group_ad_service.mutate_ad_group_ads(
                customer_id=self.customer_id,
                operations=[operation],
            )

            return response.results[0].resource_name

        except GoogleAdsException as ex:
            self.raise_google_error(ex)
        except (TransportError, requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as ex:
            self.raise_network_error(ex)
        
    def pause_campaign(self, campaign_resource_name: str):
        try:
            campaign_service = self.client.get_service("CampaignService")
            operation = self.client.get_type("CampaignOperation")

            campaign = operation.update
            campaign.resource_name = campaign_resource_name
            campaign.status = self.client.enums.CampaignStatusEnum.PAUSED
            operation.update_mask.paths.append("status")
            
            campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[operation],
            )

        except GoogleAdsException as ex:
            self.raise_google_error(ex)
        except (TransportError, requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as ex:
            self.raise_network_error(ex)