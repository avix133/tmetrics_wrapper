import datetime
import json
import logging
import os

import click

from src.api import TMetricsAPI
from src.input_parser import TasksParser
from src.time_entry_planner import TimeEntryPlanner
from src.utils import config_logger

LOG = logging.getLogger(__name__)

TASK_DEFINITION_SEPARATOR = '---'

_shared_options = [
    click.option('--account-id', default=os.environ.get('TMETRICS_ACCOUNT_ID'), required=True,
                 help='Account id, can be found in tmetrics url. Can be defined through env variable: TMETRICS_ACCOUNT_ID'),
    click.option('--user-token', default=os.environ.get('TMETRICS_TOKEN'), show_default=False, required=True,
                 help='User API token, you can generate it in TMetrics "My profile" section. Can be defined through env variable: TMETRICS_TOKEN'),
    click.option('--host', default='https://app.tmetric.com', help='TMetrics host.'),
    click.option('--dry-run', is_flag=True, default=False, help='Do not make any API calls.')
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


@click.group()
def cli():
    pass


@cli.command()
@add_options(_shared_options)
@click.option('--out-file', type=click.Path(exists=True), required=True)
def init_config(verbose, account_id, user_token, host, out_file, dry_run, assume_yes):
    config_logger(verbose)
    LOG.debug(f'Listing projects for account id: {account_id}')
    api = TMetricsAPI(account_id=account_id, token=user_token, host=host)
    if dry_run:
        LOG.error("Cannot generate config with dry run option.")
        exit(0)
    project_list = api.get_projects()
    config_projects = {}
    for project in project_list:
        client_name = project.get("client").get("name")
        project_name = project.get("name")
        project_id = project.get("id")
        key = f'{project_name}/{client_name}'
        config_projects[key] = {"id": project_id, "alias": ""}
    config = {"projects": config_projects}
    LOG.info(f'Generated config:\n{config}')
    if query_yes_no(f'Wrtie to file? ({out_file})'):
        with open(out_file, 'w', encoding='utf-8') as file:
            LOG.info(f'Writing config to file: {out_file}')
            json.dump(config, file)


@cli.command()
@add_options(_shared_options)
@click.option('--tasks-file', type=click.Path(exists=True), required=True)
@click.option('--config-file', type=click.Path(exists=True), required=True)
def run(verbose, account_id, user_token, host, tasks_file, config_file, dry_run, assume_yes):
    config_logger(verbose=verbose)
    LOG.debug(f'Running for account id: {account_id} on host: {host}')
    api = TMetricsAPI(account_id=account_id, token=user_token, host=host)
    with open(file=config_file, mode='r') as config_file:
        config = json.load(config_file)
    with open(file=tasks_file, mode='r') as tasks_file:
        tasks_definition_list = tasks_file.read().split(TASK_DEFINITION_SEPARATOR)
    parser = TasksParser(config)
    LOG.debug(f'Task definitions{tasks_definition_list}')
    for task_definition in tasks_definition_list:
        start_date, end_date, task_list = parser.parse(task_definition)
        planner = TimeEntryPlanner(start_date, end_date, task_list)
        planner.plan()
        planner.display_current_plan()
        if assume_yes or query_yes_no(question="Are you sure?"):
            for workday in planner.workday_list:
                for task in workday.task_list:
                    if not dry_run:
                        api.add_task_time_entry(task)
                        LOG.info(f'Pushed time entries for {workday}')


if __name__ == "__main__":
    cli()
