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

DATE_FORMAT = '%d.%m.%Y'

start_date = datetime.datetime.strptime('12.07.2021', DATE_FORMAT)
end_date = datetime.datetime.strptime('16.07.2021', DATE_FORMAT)

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
@click.option('-v', '--verbose', is_flag=True, default=False, help='Enable debug logs.')
def cli(verbose):
    config_logger(verbose=verbose)


@cli.command()
@add_options(_shared_options)
def list_projects(account_id, user_token, host, dry_run):
    LOG.debug(f'Listing projects for account id: {account_id}')
    api = TMetricsAPI(account_id=account_id, token=user_token, host=host)
    print(api.get_projects())


@cli.command()
@add_options(_shared_options)
@click.option('--tasks-file', type=click.Path(exists=True), required=True)
@click.option('--config-file', type=click.Path(exists=True), required=True)
def run(account_id, user_token, host, tasks_file, config_file, dry_run):
    LOG.debug(f'Running for account id: {account_id} on host: {host}')
    api = TMetricsAPI(account_id=account_id, token=user_token, host=host)
    with open(file=config_file, mode='r') as config_file:
        config = json.load(config_file)
    parser = TasksParser(config)
    start_date, end_date, task_list = parser.parse(tasks_file)
    planner = TimeEntryPlanner(start_date, end_date, task_list)
    planner.plan()
    planner.display_current_plan()

    for workday in planner.workday_list:
        for task in workday.task_list:
            if not dry_run:
                api.add_task_time_entry(task)
                LOG.info(f'Pushed time entries for {workday}')


if __name__ == "__main__":
    cli()
