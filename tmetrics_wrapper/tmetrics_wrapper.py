import json
import logging
import os
import sys

import click
from api import TMetricsAPI
from input_parser import TasksParser
from time_blocks_planner import TimeBlocksPlanner
from utils import add_click_options, config_logger, query_yes_no

LOG = logging.getLogger(__name__)

TASK_DEFINITION_SEPARATOR = "---"

_shared_options = [
    click.option(
        "--account-id",
        default=os.environ.get("TMETRICS_ACCOUNT_ID"),
        required=True,
        help="Account id, can be found in tmetrics url. Can be defined through env variable: TMETRICS_ACCOUNT_ID",
    ),
    click.option(
        "--user-token",
        default=os.environ.get("TMETRICS_TOKEN"),
        show_default=False,
        required=True,
        help='User API token, you can generate it in TMetrics "My profile" section. '
        "Can be defined through env variable: TMETRICS_TOKEN",
    ),
    click.option("--host", default="https://app.tmetric.com", help="TMetrics host.", show_default=True),
    click.option("--dry-run", is_flag=True, default=False, help="Do not make any API calls."),
    click.option("-v", "--verbose", is_flag=True, default=False, help="Enable debug logs."),
    click.option("-y", "--assume-yes", is_flag=True, default=False, help="Do not ask for confirmation."),
]


@click.group()
def cli():
    """Main cli group"""
    pass


@cli.command()
@add_click_options(_shared_options)
@click.option("--out-file", type=click.Path(exists=False), required=True)
def init_config(verbose, account_id, user_token, host, out_file, dry_run, assume_yes):  # noqa: PLR0913
    config_logger(verbose)
    LOG.debug(f"Listing projects for account id: {account_id}")
    api = TMetricsAPI(account_id=account_id, token=user_token, host=host)
    if dry_run:
        LOG.error("Cannot generate config with dry run option.")
        sys.exit(1)
    project_list = api.get_projects()
    config_projects = {}
    for project in project_list:
        client_name = project.get("client", {"name": None}).get("name")
        project_name = project.get("name")
        project_id = project.get("id")
        key = f"{project_name}/{client_name}" if client_name else project_name
        config_projects[key] = {"id": project_id, "alias": ""}
    config = {"projects": config_projects}
    LOG.info(f"Generated config:\n{config}")
    if assume_yes or query_yes_no(f"Write to file? ({out_file})"):
        with open(out_file, "w", encoding="utf-8") as file:
            LOG.info(f"Writing config to file: {out_file}")
            json.dump(config, file, indent=4, sort_keys=True)


@cli.command()
@add_click_options(_shared_options)
@click.option("--tasks-file", help="Path to your task definitons file", type=click.Path(exists=True), required=True)
@click.option(
    "--config-file",
    help="Path to your configuration",
    show_default=True,
    default="config.json",
    type=click.Path(exists=True),
    required=True,
)
def run(verbose, account_id, user_token, host, tasks_file, config_file, dry_run, assume_yes):  # noqa: PLR0913
    config_logger(verbose=verbose)
    LOG.debug(f"Running for account id: {account_id} on host: {host}")
    api = TMetricsAPI(account_id=account_id, token=user_token, host=host)
    with open(file=config_file) as config_file_:
        config = json.load(config_file_)
    with open(file=tasks_file) as tasks_file_:
        tasks_definition_list = tasks_file_.read().split(TASK_DEFINITION_SEPARATOR)
    parser = TasksParser(config)
    LOG.debug(f"Task definitions{tasks_definition_list}")
    for task_definition in tasks_definition_list:
        if not task_definition:
            LOG.warning("Empty task definition, skipping.")
        start_date, end_date, task_list = parser.parse(task_definition)
        planner = TimeBlocksPlanner(start_date, end_date, task_list)
        planner.plan()
        planner.display_current_plan()
        if not dry_run and (assume_yes or query_yes_no(question="Are you sure?")):
            planner.apply_plan(api)


if __name__ == "__main__":
    cli()
