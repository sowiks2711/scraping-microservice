from typing import NamedTuple

from flask import json

INITIATED_STATUS = 'initiated'
PENDING_STATUS = 'pending'
DONE_STATUS = 'done'

IMAGES_TYPE = 'images'
TEXTS_TYPE = 'texts'


class TaskModel(NamedTuple):
    id: str
    status: str
    url: str
    resource_name: str
    resource_type: str

    @classmethod
    def from_json(cls, task_json_dump: str):
        task_json = json.loads(task_json_dump)
        return cls(task_json['id'], task_json['status'], task_json['url'], task_json['resource_name'], task_json['resource_type'])

