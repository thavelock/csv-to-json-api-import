"""Primary logic for the CLI Tool
"""

# ===== IMPORTS =====

import csv
import json

import typer
from rich import print
from typing_extensions import Annotated

from csv_to_json_api_import import snyk

# ===== CONSTANTS =====

UNKNOWN_ORG_NAME = "Unknown Asset ID"

ORGS_JSON_OUTPUT_FILE = "new-orgs.json"

# csv file columns
COL_TECH_ORG        = 0
COL_ASSET_ID        = 1
COL_ASSET_NAME      = 2
COL_REPO_URL        = 3
COL_TARGET_NAME     = 4
COL_REPO_COUNT      = 5

# ===== GLOBALS =====

app = typer.Typer(add_completion=False)
state = {"verbose": False}

# ===== METHODS =====

@app.command('org-json')
def org_json(
    group_id:
        Annotated[
            str,
            typer.Argument(
                help='Group ID in Snyk',
                envvar='GROUP_ID')],
    source_org:
        Annotated[
            str,
            typer.Argument(
                help='Org in Snyk to copy integrations from',
                envvar='SOURCE_ORG')],
    csv_path:
        Annotated[
            str,
            typer.Option(
                help='Path to CSV file that will be used to created JSON org structure',
                envvar='CSV_PATH')]):

    new_orgs = []
    output_json = { "orgs": [] }

    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        # skip the header
        next(csv_reader, None)

        for row in csv_reader:

            if state['verbose']:
                print(row)

            new_org_name = ''

            if row[COL_ASSET_ID] == '' or row[COL_ASSET_NAME] == '':
                new_org_name = UNKNOWN_ORG_NAME
            else:
                new_org_name = row[COL_ASSET_ID] + '_' + row[COL_ASSET_NAME]

            if len(new_org_name) > 60:
                print(f"Org name too long: {new_org_name}")
                new_org_name = new_org_name[:60]
                print(f"Shortening to: {new_org_name}")

            if new_org_name not in new_orgs:
                new_orgs.append(new_org_name)

        for org in new_orgs:
            new_org_object = {
                "name": org,
                "groupId": group_id,
                "sourceOrgId": source_org
            }

            output_json["orgs"].append(new_org_object)

    if state['verbose']:
        print(output_json)

    with open(ORGS_JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(json.dumps(output_json, indent=4))
        f.close()

    return

@app.command('migrate-projects')
def migrate_projects(
    group_id:
        Annotated[
            str,
            typer.Argument(
                help='Group ID in Snyk',
                envvar='GROUP_ID')],
    snyk_token:
        Annotated[
            str,
            typer.Argument(
                help='Snyk API token',
                envvar='SNYK_TOKEN')],
    csv_path:
        Annotated[
            str,
            typer.Option(
                help='Path to CSV file that will be used to created JSON org structure',
                envvar='CSV_PATH')]):


    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file)

        for row in csv_reader:

            # get target id using asset name
            # target_id = snyk.get_target_id_from_name(snyk_token, )

            # get projects using target id as a filter

            # get org id of destination org

            # move all projects to destination org

            continue


    return

@app.callback()
def main(verbose: bool = False):
    if verbose:
        state['verbose'] = True

def run():
    """Run the defined typer CLI app
    """
    app()
