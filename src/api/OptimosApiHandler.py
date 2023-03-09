import uuid

from flask import request, make_response
from flask_restful import Resource

import tempfile
import os

from src.tasks import optimization_task


class OptimosApiHandler(Resource):

    def __saveFile(self, fileStorage, prefix, filePath):
        file_ext = fileStorage.filename.split(".")[-1]
        temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix="." + file_ext, prefix=prefix, delete=False,
                                                dir=filePath)
        fileStorage.save(temp_file.name)
        filename = temp_file.name.split(os.sep)[-1]

        return filename

    def post(self):
        try:
            form_data = request.form
            files_data = request.files

            total_iterations = int(form_data.get('total_iterations'))
            algorithm = form_data.get('algorithm')
            approach = form_data.get('approach')
            # log_name = form_data.get('logName')
            log_name = str(uuid.uuid4())

            sim_params_data = files_data.get('simScenarioFile')
            constraints_data = files_data.get('constraintsFile')
            xml_data = files_data.get('modelFile')

            curr_dir_path = os.path.abspath(os.path.dirname(__file__))
            celery_data_path = os.path.abspath(os.path.join(curr_dir_path, '..', 'celery/data'))

            constraints_file = self.__saveFile(constraints_data, "constraints_", celery_data_path)
            sim_params_file = self.__saveFile(sim_params_data, "params_", celery_data_path)
            bpmn_file = self.__saveFile(xml_data, "bpmn_model_", celery_data_path)

            task = optimization_task.delay(bpmn_file, sim_params_file, constraints_file, total_iterations, algorithm, approach, log_name)
            task_id = task.id

            task_response = f"""{{"TaskId": "{task_id}"}}"""

            response = make_response(task_response)
            response.headers['content-type'] = 'application/json'
            return response
        except Exception as e:
            print(e)
            response = {
                "displayMessage": "Something went wrong"
            }

            return response, 500
