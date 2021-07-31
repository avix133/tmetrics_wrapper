import logging
from datetime import datetime, timedelta, date

from src.time_entry_planner import Task

LOG = logging.getLogger(__name__)

ALIAS_PREFIX = '$'


class TasksParser(object):
    def __init__(self, config: {}):
        self.config: {} = config

    def parse(self, tasks_definition: str) -> (date, date, [Task]):
        with open(file=tasks_definition, mode='r') as file:
            lines = [line.rstrip() for line in file.readlines()]
            lines = [line for line in lines if line]

            date_range = lines[0].split('-')
            start_date = datetime.strptime(date_range[0], '%d.%m.%Y').date()
            end_date = datetime.strptime(date_range[1], '%d.%m.%Y').date()

            LOG.debug(f'Parsed start date: {start_date}')
            LOG.debug(f'Parsed end date: {end_date}')

            task_list: [Task] = []
            for line in lines[1:]:
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
                task_list.append(task)
            LOG.info('Task file parsed.')
            return start_date, end_date, task_list

    def _get_project_id(self, project) -> int:
        LOG.debug(f'Getting project id for {project}')
        project_id = None
        if project.startswith(ALIAS_PREFIX):
            for project_definition in self.config.get('projects').values():
                if project_definition.get('alias') == project[1:]:
                    project_id = int(project_definition.get('id'))
                    LOG.debug(f'Returning project id {project_id} for alias {project}')
        else:
            project_id = int(self.config.get('projects').get(project).get('id'))
            LOG.debug(f'Returning project id {project_id} project key {project}')
        return project_id
