from exts import celery as celery_app
from flask import make_response, request
from flask_restful import Resource
from celery.result import AsyncResult
from celery import states
import json
from flasgger import swag_from


class TaskApiHandler(Resource):
    def get(self):
        task_id = request.args["taskId"]

        res = AsyncResult(task_id, app=celery_app)

        task_status = res.status
        task_res = res.get() if (task_status == states.SUCCESS) else ""

        str = f"""{{
      "TaskId": "{task_id}",
      "TaskStatus": "{task_status}",
      "TaskResponse": {json.dumps(task_res)}
}}"""

        response = make_response(str)
        response.headers['content-type'] = 'application/json'
        return