"""Utility functions to simplify API calls to Snyk
"""

import json
import time

import requests
from rich import print

from csv_to_json_api_import.constants import *

def get_target_id_from_name(snyk_token, org_id, target_name, verbose=False):
    retry = 0

    target_id = None

    headers = {
        'Authorization': f'token {snyk_token}'
    }

    url = f"{SNYK_REST_API_BASE_URL}/orgs/{org_id}/targets?version={SNYK_REST_API_VERSION}&displayName={requests.utils.quote(target_name, safe='')}"

    while True:
        response = requests.request(
            'GET',
            url,
            headers=headers,
            timeout=SNYK_API_TIMEOUT_DEFAULT)

        if response.status_code == 200:
            response_json = json.loads(response.content)
            if (len(response_json['data']) > 0):
                target_id = response_json['data'][0]['id']
            else:
                print(f"Did not find a target with name: {target_name}")
            break
        elif response.status_code == 429:
            print(f"To many API calls, backing off for {SNYK_API_RATE_LIMIT_BACKOFF_SECONDS} seconds")
            time.sleep(SNYK_API_RATE_LIMIT_BACKOFF_SECONDS)
            retry += 1
            if retry > MAX_RETRIES:
                break
        else:
            print(f"Could not complete request {target_name}, reason: {response.status_code}")
            break

    return target_id

def get_projects_from_target(snyk_token, org_id, target_id, verbose=False):
    project_ids = []
    retry = 0

    headers = {
        'Authorization': f'token {snyk_token}'
    }

    url = f"{SNYK_REST_API_BASE_URL}/orgs/{org_id}/projects?version={SNYK_REST_API_VERSION}&target_id={target_id}&limit=100"

    while True:
        response = requests.request(
            'GET',
            url,
            headers=headers,
            timeout=SNYK_API_TIMEOUT_DEFAULT)

        if response.status_code == 200:
            response_json = json.loads(response.content)
            for project in response_json['data']:
                project_ids.append(project['id'])

            if 'next' not in response_json['links'] or response_json['links']['next'] == '':
                break

            url = f"{SNYK_API_BASE_URL}{response_json['links']['next']}"
            retry = 0

        elif response.status_code == 429:
            print(f"To many API calls, backing off for {SNYK_API_RATE_LIMIT_BACKOFF_SECONDS} seconds")
            time.sleep(SNYK_API_RATE_LIMIT_BACKOFF_SECONDS)
            retry += 1
            if retry > MAX_RETRIES:
                break
        else:
            print(f"Could not complete request, reason: {response.status_code}")
            break

    return project_ids

def get_organization_id_from_name(snyk_token, group_id, org_name, verbose=False):
    retry = 0
    org_id = None

    headers = {
        'Authorization': f'token {snyk_token}'
    }

    url = f"{SNYK_REST_API_BASE_URL}/groups/{group_id}/orgs?version={SNYK_REST_API_VERSION}&name={requests.utils.quote(org_name, safe='')}"

    while True:
        response = requests.request(
            'GET',
            url,
            headers=headers,
            timeout=SNYK_API_TIMEOUT_DEFAULT)

        if response.status_code == 200:
            response_json = json.loads(response.content)
            if (len(response_json['data']) > 0):
                org_id = response_json['data'][0]['id']
            else:
                print(f"Did not find an org with name: {org_name}")
            break
        elif response.status_code == 429:
            print(f"To many API calls, backing off for {SNYK_API_RATE_LIMIT_BACKOFF_SECONDS} seconds")
            time.sleep(SNYK_API_RATE_LIMIT_BACKOFF_SECONDS)
            retry += 1
            if retry > MAX_RETRIES:
                break
        else:
            print(f"Could not complete request, reason: {response.status_code}")
            break

    return org_id

def move_project_to_org(snyk_token, source_org, target_org, project_id, verbose=False, dry_run=False):
    retry = 0

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'token {snyk_token}'
    }

    url = f"{SNYK_V1_API_BASE_URL}/org/{source_org}/project/{project_id}/move"

    payload = json.dumps({
        "targetOrgId": f"{target_org}"
    })

    print(f"Moving project: {project_id} from org: {source_org} to org: {target_org}")

    if not dry_run:
        while True:

            try:
                response = requests.request(
                    'PUT',
                    url,
                    headers=headers,
                    data=payload,
                    timeout=SNYK_API_TIMEOUT_DEFAULT)

                if response.status_code == 200:
                    response_json = json.loads(response.content)
                    print(f"Successfully migrated project: {project_id}")
                    return True
                elif response.status_code == 429:
                    print(f"To many API calls, backing off for {SNYK_API_RATE_LIMIT_BACKOFF_SECONDS} seconds")
                    time.sleep(SNYK_API_RATE_LIMIT_BACKOFF_SECONDS)
                    retry += 1
                    if retry > MAX_RETRIES:
                        break
                else:
                    print(f"Could not complete request, reason: {response.status_code}")
                    break

            except requests.ConnectTimeout:
                print(f"ERROR: ConnectionTimeout, moving on to next project")
                return False
            except requests.ReadTimeout:
                print(f"ERROR ReadTimeout, moving on to next project")
                return False
            except requests.Timeout:
                print(f"ERROR: Timeout, moving on to next project")
                return False

    return False

def delete_target(snyk_token, org_id, target_id, verbose=False):
    retry = 0

    headers = {
        'Authorization': f'token {snyk_token}'
    }

    url = f"{SNYK_REST_API_BASE_URL}/orgs/{org_id}/targets/{target_id}?version={SNYK_REST_API_VERSION}"

    while True:
        response = requests.request(
            'DELETE',
            url,
            headers=headers,
            timeout=SNYK_API_TIMEOUT_DEFAULT)

        if response.status_code == 204:
            print(f"Successfully removed target {target_id} from org {org_id}")
            return True
        elif response.status_code == 429:
            print(f"To many API calls, backing off for {SNYK_API_RATE_LIMIT_BACKOFF_SECONDS} seconds")
            time.sleep(SNYK_API_RATE_LIMIT_BACKOFF_SECONDS)
            retry += 1
            if retry > MAX_RETRIES:
                break
        else:
            print(f"Could not remove target {target_id}, reason: {response.status_code}")
            break
