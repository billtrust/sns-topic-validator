import os
import json
from botocore.vendored import requests
import logging

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def post_to_slack(webhook_url, slack_data):

    json_msg = json.dumps(slack_data)
    response = requests.post(
        webhook_url, data=json_msg,
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        msg = (
            f'Request to slack returned an error {response.status_code}, '
            f'the response is:\n{response.text}\n'
            f'Slack data message:\n{json_msg}'
            )
        logging.warn(msg)
        raise ValueError(msg)
