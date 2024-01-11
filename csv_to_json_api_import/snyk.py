"""Utility functions to simplify API calls to Snyk
"""

import json

import requests
from rich import print

from csv_to_json_api_import.constants import (SNYK_API_TIMEOUT_DEFAULT,
                                              SNYK_REST_API_BASE_URL,
                                              SNYK_REST_API_VERSION)

def get_target_id_from_name(snyk_token, org_id, target_name):

    target_id = None

    headers = {
        'Authorization': f'token {snyk_token}'
    }

    url = f"{SNYK_REST_API_BASE_URL}/orgs/{org_id}/targets?version={SNYK_REST_API_VERSION}displayName={target_name}"

    response = requests.request(
        'GET',
        url,
        headers=headers,
        timeout=SNYK_API_TIMEOUT_DEFAULT)

    response_json = json.loads(response.content)

    if response.status_code == 200:
        if (len(response_json['data'] > 0)):
            target_id = response_json['data'][0]['id']
        else:
            print(f"Did not find a target with name: {target_name}")
    else:
        print(f"Could not complete move for {target_name}, reason: {response.status_code}")

    return target_id

