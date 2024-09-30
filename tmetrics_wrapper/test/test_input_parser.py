from datetime import date, timedelta

import pytest
from input_parser import TasksParser
from time_blocks_planner import Task

DEFAULT_CONFIG = {
    "projects": {
        "Test/Abc": {"id": 123, "alias": "test"},
        "Test/Xyz": {"id": 456, "alias": "xyz"},
        "Alpha/Beta": {"id": 98765, "alias": "gamma"},
    }
}


class TestTasksParser:
    def setup_method(
        self,
    ):
        self.parser = TasksParser(DEFAULT_CONFIG)

    def test_invalid_task_definition(self):
        invalid_task_definition_list = [
            """26.07.2021-30.07.2021
                                            6|Wrong project|not_a_project|5""",
            """07.2021-30.07.2021
                                            6|Wrong date A|Test/Abc|5""",
            """26.07.2021-32.07.2021
                                            6|Wrong date B|Test/Abc|5""",
            """26.07.2021-20.07.2021
                                            6|Wrong date range|Test/Abc|5""",
            """26.07.2021-30.07.2021
                                            No hours|Test/Abc|5""",
            """26.07.2021-30.07.2021
                                            1|No project""",
            """26.07.2021-30.07.2021
                                            1|Wrong alias|$no_alias|5""",
            """26.07.2021-30.07.2021
                                            1|Wrong split|Test/Abc|abc""",
            """26.07.2021-30.07.2021""",
        ]

        for task_definition in invalid_task_definition_list:
            with pytest.raises((AttributeError, ValueError, IndexError)):
                self.parser.parse(task_definition)

    def test_parse(self):
        task_definition = """26.07.2021-30.07.2021
                            1|Task with split|Test/Abc|2
                            6:00|Task without split|Test/Xyz
                            6:20|Task with alias|$test
                            4:56|Task with alias2|$gamma|4"""

        task_with_split = Task("Task with split", 123, timedelta(hours=1), 2)
        task_without_split = Task("Task without split", 456, timedelta(hours=6))
        task_with_alias = Task("Task with alias", 123, timedelta(hours=6, minutes=20))
        task_with_alias2 = Task("Task with alias2", 98765, timedelta(hours=4, minutes=56), 4)

        start_date, end_date, task_list = self.parser.parse(task_definition)

        assert start_date == date(2021, 7, 26)
        assert end_date == date(2021, 7, 30)

        assert [task for task in task_list if task == task_with_split]
        assert [task for task in task_list if task == task_without_split]
        assert [task for task in task_list if task == task_with_alias]
        assert [task for task in task_list if task == task_with_alias2]
