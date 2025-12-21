from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from app.config import Config
from google.auth.exceptions import TransportError
import requests
import urllib3

from app.errors.exceptions import ExternalServiceError


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
            raise ExternalServiceError(
                "Google Ads credentials are not fully configured"
            )

        self.customer_id = Config.GOOGLE_ADS_CUSTOMER_ID

        self.client = GoogleAdsClient.load_from_dict({
            "developer_token": Config.GOOGLE_ADS_DEVELOPER_TOKEN,
            "client_id": Config.GOOGLE_ADS_CLIENT_ID,
            "client_secret": Config.GOOGLE_ADS_CLIENT_SECRET,
            "refresh_token": Config.GOOGLE_ADS_REFRESH_TOKEN,
            "login_customer_id": Config.GOOGLE_ADS_LOGIN_CUSTOMER_ID,
            "use_proto_plus": True,
        })

    def handle_google_exception(self, ex: GoogleAdsException):
        messages = [
            f"{error.error_code}: {error.message}"
            for error in ex.failure.errors
        ]
        raise ExternalServiceError(" | ".join(messages)) from ex

    def handle_network_exception(self, ex: Exception):
        raise ExternalServiceError("Google Ads service unavailable") from ex

    def raise_google_error(self, ex: GoogleAdsException):
        return self.handle_google_exception(ex)

    def raise_network_error(self, ex: Exception):
        return self.handle_network_exception(ex)

    def publish_search_campaign_atomic(
            self,
            *,
            campaign_name: str,
            daily_budget_micros: int,
            ad_group_name: str,
            headline: str,
            description: str,
            final_url: str,
        ):
        try:
            google_ads_service = self.client.get_service("GoogleAdsService")

            operations = []
            customer = f"customers/{self.customer_id}"

            budget_temp = f"{customer}/campaignBudgets/-1"
            campaign_temp = f"{customer}/campaigns/-2"
            ad_group_temp = f"{customer}/adGroups/-3"

            budget = self.client.get_type("CampaignBudget")
            budget.resource_name = budget_temp
            budget.name = f"{campaign_name} Budget"
            budget.amount_micros = daily_budget_micros
            budget.delivery_method = (
                self.client.enums.BudgetDeliveryMethodEnum.STANDARD
            )

            budget_op = self.client.get_type("MutateOperation")
            budget_op.campaign_budget_operation.create = budget
            operations.append(budget_op)

            campaign = self.client.get_type("Campaign")
            campaign.resource_name = campaign_temp
            campaign.name = campaign_name
            campaign.campaign_budget = budget_temp
            campaign.status = self.client.enums.CampaignStatusEnum.PAUSED
            campaign.advertising_channel_type = (
                self.client.enums.AdvertisingChannelTypeEnum.SEARCH
            )

            campaign_op = self.client.get_type("MutateOperation")
            campaign_op.campaign_operation.create = campaign
            operations.append(campaign_op)

            ad_group = self.client.get_type("AdGroup")
            ad_group.resource_name = ad_group_temp
            ad_group.name = ad_group_name
            ad_group.campaign = campaign_temp
            ad_group.status = self.client.enums.AdGroupStatusEnum.PAUSED
            ad_group.type_ = self.client.enums.AdGroupTypeEnum.SEARCH_STANDARD

            ad_group_op = self.client.get_type("MutateOperation")
            ad_group_op.ad_group_operation.create = ad_group
            operations.append(ad_group_op)

            ad_group_ad = self.client.get_type("AdGroupAd")
            ad_group_ad.ad_group = ad_group_temp
            ad_group_ad.status = self.client.enums.AdGroupAdStatusEnum.PAUSED

            ad = ad_group_ad.ad
            ad.final_urls.append(final_url)

            rsa = ad.responsive_search_ad

            h1 = self.client.get_type("AdTextAsset")
            h1.text = headline

            h2 = self.client.get_type("AdTextAsset")
            h2.text = f"{headline} Official"

            h3 = self.client.get_type("AdTextAsset")
            h3.text = "Get Started Today"

            rsa.headlines.append(h1)
            rsa.headlines.append(h2)
            rsa.headlines.append(h3)

            d1 = self.client.get_type("AdTextAsset")
            d1.text = description

            d2 = self.client.get_type("AdTextAsset")
            d2.text = "Simple. Fast. Reliable."

            rsa.descriptions.append(d1)
            rsa.descriptions.append(d2)

            ad_op = self.client.get_type("MutateOperation")
            ad_op.ad_group_ad_operation.create = ad_group_ad
            operations.append(ad_op)

            response = google_ads_service.mutate(
                customer_id=self.customer_id,
                mutate_operations=operations,
            )

            for res in response.mutate_operation_responses:
                if res.campaign_result.resource_name:
                    return res.campaign_result.resource_name

            raise ExternalServiceError("Campaign created but resource not returned")

        except GoogleAdsException as ex:
            self.handle_google_exception(ex)
        except (TransportError, requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as ex:
            self.handle_network_exception(ex)

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
            self.handle_google_exception(ex)
        except (TransportError, requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as ex:
            self.handle_network_exception(ex)


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
            self.handle_google_exception(ex)
        except (TransportError, requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as ex:
            self.handle_network_exception(ex)
        
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
            self.handle_google_exception(ex)
        except (TransportError, requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as ex:
            self.handle_network_exception(ex)

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

            h1 = self.client.get_type("AdTextAsset")
            h1.text = headline

            h2 = self.client.get_type("AdTextAsset")
            h2.text = f"{headline} – Official"

            h3 = self.client.get_type("AdTextAsset")
            h3.text = "Get Started Today"

            rsa.headlines.append(h1)
            rsa.headlines.append(h2)
            rsa.headlines.append(h3)

            d1 = self.client.get_type("AdTextAsset")
            d1.text = description

            d2 = self.client.get_type("AdTextAsset")
            d2.text = "Simple. Fast. Reliable."

            rsa.descriptions.append(d1)
            rsa.descriptions.append(d2)

            response = ad_group_ad_service.mutate_ad_group_ads(
                customer_id=self.customer_id,
                operations=[operation],
            )

            return response.results[0].resource_name

        except GoogleAdsException as ex:
            self.handle_google_exception(ex)
        except (TransportError, requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as ex:
            self.handle_network_exception(ex)
        
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