"""Primary logic for the CLI Tool
"""

# ===== IMPORTS =====

import csv
import json
from datetime import datetime

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
    template_org:
        Annotated[
            str,
            typer.Argument(
                help='Org in Snyk to copy integrations from',
                envvar='TEMPLATE_ORG')],
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
                "sourceOrgId": template_org
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
    snyk_token:
        Annotated[
            str,
            typer.Argument(
                help='Snyk API token',
                envvar='SNYK_TOKEN')],
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
                help='Group ID in Snyk',
                envvar='SOURCE_ORG')],
    csv_path:
        Annotated[
            str,
            typer.Option(
                help='Path to CSV file that will be used to created JSON org structure',
                envvar='CSV_PATH')],
    dry_run:
        Annotated[
            bool,
            typer.Option(
                help="Print move information only")] = False):

    start_time = datetime.now()
    projects_migrated_total = 0

    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file)

        # skip the header
        next(csv_reader, None)

        for row in csv_reader:

            # get target id using asset name
            target_id = snyk.get_target_id_from_name(snyk_token, source_org, row[COL_TARGET_NAME], verbose=state['verbose'])

            if state['verbose']:
                print(f"Name: {row[COL_ASSET_NAME]}, Target ID: {target_id}")

            if target_id is not None:
                # get projects using target id as a filter

                project_ids = snyk.get_projects_from_target(snyk_token, source_org, target_id)

                if state['verbose']:
                    print(f"Project IDs for {row[COL_TARGET_NAME]}: {project_ids}")

                if len(project_ids) > 0:
                    # get org id of destination org
                    org_name = ''

                    if row[COL_ASSET_ID] == '' or row[COL_ASSET_NAME] == '':
                        org_name = UNKNOWN_ORG_NAME
                    else:
                        org_name = row[COL_ASSET_ID] + '_' + row[COL_ASSET_NAME]

                    if len(org_name) > 60:
                        org_name = org_name[:60]

                    org_id = snyk.get_organization_id_from_name(snyk_token, group_id, org_name, verbose=state['verbose'])

                    if org_id is not None:
                        print(f"Org ID: {org_id}, Org Name: '{org_name}'")

                    num_errors = 0
                    # move all projects to destination org
                    for project_id in project_ids:
                        if not snyk.move_project_to_org(snyk_token, source_org, org_id, project_id, verbose=state['verbose'], dry_run=dry_run):
                            num_errors += 1
                        else:
                            projects_migrated_total += 1

                    # clean up empty project
                    if num_errors == 0 and not dry_run:
                        snyk.delete_target(snyk_token, source_org, target_id, verbose=state['verbose'])

            else:
                print(f"Could not get Target ID for: {row[COL_TARGET_NAME]}")

            print("")

    print(f"Finished, total projects migrated: {projects_migrated_total}, took {datetime.now() - start_time}")

    return

@app.callback()
def main(verbose: bool = False):
    if verbose:
        state['verbose'] = True

def run():
    """Run the defined typer CLI app
    """
    app()
