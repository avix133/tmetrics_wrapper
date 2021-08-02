import logging
from datetime import datetime, timedelta, date

from src.time_blocks_planner import Task

LOG = logging.getLogger(__name__)

DATE_FORMAT = '%d.%m.%Y'
ALIAS_PREFIX = '$'


class TasksParser(object):
    def __init__(self, config: {}):
        self.config: {} = config

    def parse(self, tasks_definition: str) -> (date, date, [Task]):
        LOG.debug(f'Parsing task definition:\n{tasks_definition}')
        lines = [line.rstrip() for line in tasks_definition.splitlines()]
        lines = [line for line in lines if line]

        date_range = lines[0].split('-')
        start_date = datetime.strptime(date_range[0], DATE_FORMAT).date()
        end_date = datetime.strptime(date_range[1], DATE_FORMAT).date()

        if start_date > end_date:
            raise ValueError("Wrong date range.")

        LOG.debug(f'Parsed start date: {start_date}')
        LOG.debug(f'Parsed end date: {end_date}')

        task_list: [Task] = [self._parse_task_line(line) for line in lines[1:]]

        if not task_list:
            raise ValueError("Empty task list.")

        LOG.info('Task file parsed.')
        return start_date, end_date, task_list

    def _parse_task_line(self, line) -> Task:
        LOG.debug(f'Parsing line: {line}')
        split_line = line.split('|')
        hours = int(split_line[0].split(':')[0])
        try:
            minutes = int(split_line[0].split(':')[1])
        except IndexError:
            minutes = 0
        note = split_line[1]
        project = split_line[2]
        try:
            requested_split = int(split_line[3])
        except IndexError:
            requested_split = 1
        task = Task(note, self._get_project_id(project), duration=timedelta(hours=hours, minutes=minutes),
                    requested_split=requested_split)
        LOG.debug(f'Line parsed to task: {task}')
        return task

    def _get_project_id(self, project) -> int:
        LOG.debug(f'Getting project id for {project}')
        project_id = None
        if project.startswith(ALIAS_PREFIX):
            for project_definition in self.config.get('projects').values():
                if project_definition.get('alias') == project[1:]:
                    project_id = int(project_definition.get('id'))
                    LOG.debug(f'Returning project id {project_id} for alias {project}')
            if not project_id:
                LOG.error(f'Project id not found for alias {project}')
                raise ValueError
        else:
            try:
                project_id = int(self.config.get('projects').get(project).get('id'))
                LOG.debug(f'Returning project id {project_id} project key {project}')
            except AttributeError:
                LOG.error(f'Project id not found for {project}.')
                raise
        return project_id
