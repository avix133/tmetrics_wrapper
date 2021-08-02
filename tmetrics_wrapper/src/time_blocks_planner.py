import copy
import logging
from datetime import datetime, time, timedelta

from src.api import TMetricsAPI

LOG = logging.getLogger(__name__)

WORKDAY_START_TIME = time(hour=8)
WORKDAY_END_TIME = time(hour=17)
MAX_TASK_DURATION_TIMEDELTA = timedelta(hours=8)
PLANNING_ITERATIONS = 3


class NotFullyPlannedException(Exception):
    """Raised when some tasks couldn't be planned"""


class Task(object):
    def __init__(self, note: str, project_id: int, duration: timedelta, requested_split: int = 1):
        self.note = note
        self.project_id = project_id
        self.duration = duration
        self.start_date = None
        self.end_date = None
        self.requested_split = requested_split

    def is_similar_task(self, other):
        if isinstance(other, self.__class__):
            return self.note == other.note and self.project_id == other.project_id and self.duration == other.duration

    def is_scheduled(self) -> bool:
        return bool(self.start_date)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.note == other.note and self.project_id == other.project_id and \
               self.duration == other.duration and self.start_date == other.start_date and \
               self.end_date == other.end_date and self.requested_split == other.requested_split

    def __str__(self):
        if self.start_date:
            return '{' + f'{self.__class__.__name__}: {self.start_date} - {self.end_date}({str(self.duration)}) {self.note} [{self.project_id}]' + '}'
        return '{' + f'{self.__class__.__name__}:({str(self.duration)}) {self.note} [{self.project_id}]' + '}'


class WorkDay(object):
    def __init__(self, workday_date: datetime.date):
        self.start_date = datetime.combine(date=workday_date, time=WORKDAY_START_TIME)
        self.end_date = datetime.combine(date=workday_date, time=WORKDAY_END_TIME)
        self.task_list: [Task] = []
        self._last_task_end_date = self.start_date

    def add_task(self, task: Task):
        task.start_date = self._last_task_end_date
        task.end_date = task.start_date + task.duration
        self.task_list.append(task)
        self._last_task_end_date = task.end_date

    def get_occupied_time(self) -> timedelta:
        return sum([task.duration for task in self.task_list], timedelta())

    def get_free_time(self) -> timedelta:
        return self.end_date - self.start_date - self.get_occupied_time()

    def has_similar_task(self, other_task: Task) -> bool:
        return bool([task for task in self.task_list if task.is_similar_task(other_task)])

    def __str__(self):
        return '{' + f'{self.__class__.__name__}: {self.start_date} - {self.end_date}, occupied: {self.get_occupied_time()}' + '}'


class TimeBlocksPlanner(object):
    def __init__(self, start_date: datetime.date, end_date: datetime.date, task_list: [Task]):
        self.start_date = start_date
        self.end_date = end_date
        self.workday_list = self._generate_workdays(start_date, end_date)
        self.task_list = self._split_tasks(task_list, len(self.workday_list))

    def apply_plan(self, api: TMetricsAPI):
        for workday in self.workday_list:
            for task in workday.task_list:
                self._add_task_time_entry(api=api, task=task)
            LOG.info(f'Pushed time entries for {workday}')

    def get_total_planned_time(self) -> timedelta:
        return sum([workday.get_occupied_time() for workday in self.workday_list], timedelta())

    def display_current_plan(self):
        LOG.debug('Displaying plan.')

        for workday in self.workday_list:
            print(workday)
            for task in workday.task_list:
                print(task)
            print()
        print(
            f'Planned {self.get_total_planned_time().total_seconds() // 3600}h for {self.start_date} - {self.end_date}')

    def plan(self):
        remaining_task_list = sorted(self.task_list, key=lambda task: task.duration, reverse=True)
        for i in range(PLANNING_ITERATIONS):
            LOG.debug(f'Planning ({i})')
            remaining_task_list = [task for task in remaining_task_list if not task.is_scheduled()]
            if not remaining_task_list:
                LOG.info('Successfully planned all tasks.')
                break

            for workday in reversed(self.workday_list) if i % 2 == 0 else self.workday_list:
                self._plan_workday(i, remaining_task_list, workday)

        if remaining_task_list:
            raise NotFullyPlannedException(
                f"Couldn't schedule following tasks: {[str(task) for task in remaining_task_list]}")

    @staticmethod
    def _add_task_time_entry(api, task: Task):
        LOG.debug(f'Adding task time entry {task}')
        api.add_time_entry(project_id=task.project_id, note=task.note, start_time=task.start_date,
                           end_time=task.end_date)

    @staticmethod
    def _plan_workday(iteration, remaining_task_list, workday):
        for task in remaining_task_list:
            if not task.is_scheduled() and task.duration < workday.get_free_time():
                if iteration == 0 and (
                        workday.has_similar_task(task) or task.duration > workday.get_free_time() - timedelta(
                    minutes=20)):
                    LOG.debug(
                        'Similar task is already scheduled in the same workday or extending optimal daily workhours. Waiting for better opportunity.')
                else:
                    LOG.debug(f'Adding task {task} to workday {workday}')
                    workday.add_task(task)

    @staticmethod
    def _split_tasks(task_list: [Task], default_split: int) -> [Task]:
        result: [Task] = []
        for task in task_list:
            if task.requested_split > 1 and task.duration / task.requested_split < MAX_TASK_DURATION_TIMEDELTA:
                LOG.debug(f'Splitting task {task} into requested split ({task.requested_split})')
                for _ in range(task.requested_split):
                    new_task = copy.deepcopy(task)
                    new_task.duration /= task.requested_split
                    result.append(new_task)
            elif task.duration > MAX_TASK_DURATION_TIMEDELTA:
                LOG.debug(f'Splitting task {task} into daily split ({default_split})')
                for _ in range(default_split):
                    new_task = copy.deepcopy(task)
                    new_task.duration /= default_split
                    result.append(new_task)
            else:
                LOG.debug(f'Appending without split: {task}')
                result.append(task)

        return result

    @staticmethod
    def _generate_workdays(start_date: datetime.date, end_date: datetime.date) -> [WorkDay]:
        result = []
        delta = timedelta(days=1)
        while start_date <= end_date:
            result.append(WorkDay(start_date))
            start_date += delta
        return result
