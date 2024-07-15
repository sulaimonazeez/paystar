import requests
from django.conf import settings
import logging
from .models import Profile

logger = logging.getLogger(__name__)

class PaystackService:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = "https://api.paystack.co"

    def generate_virtual_account(self, user):
        url = f"{self.base_url}/dedicated_account"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

        # Fetch user profile for phone number
        data = {
            "customer": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": "08080891605"
                 # Assuming phone number is stored in user.profile.phone_number
            },
            "preferred_bank": "wema-bank",
            "type":"nuban" # Preferred bank, you can change as needed
            # "split_code": "SPL_98WF13EB7A2A61",  # Optional split code if you have revenue sharing setup
        }

        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()

        logger.debug(f"Paystack response: {response_data}")

        if response.status_code == 200 and response_data['status']:
            return response_data['data']
        else:
            error_message = response_data.get('message', 'Unknown error')
            logger.error(f"Paystack error: {error_message}")
            raise Exception(f"Failed to create virtual account: {error_message}")
