from flask import request, make_response
from flask_restful import Resource

from optimos import run_optimization
import tempfile
import os


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

            sim_params_data = files_data.get('simScenarioFile')
            constraints_data = files_data.get('constraintsFile')
            xml_data = files_data.get('modelFile')

            curr_dir_path = os.path.abspath(os.path.dirname(__file__))
            celery_data_path = os.path.abspath(os.path.join(curr_dir_path, '..', 'celery/data'))

            constraints_file = self.__saveFile(constraints_data, "constraints_", celery_data_path)
            sim_params_file = self.__saveFile(sim_params_data, "params_", celery_data_path)
            bpmn_file = self.__saveFile(xml_data, "bpmn_model_", celery_data_path)

            model_path = os.path.abspath(os.path.join(celery_data_path, bpmn_file))
            sim_param_path = os.path.abspath(os.path.join(celery_data_path, sim_params_file))
            constraints_path = os.path.abspath(os.path.join(celery_data_path, constraints_file))

            res = run_optimization(model_path, sim_param_path, constraints_path, total_iterations, algorithm, approach)
            print(res)
            response = make_response(f"""{{"TaskId":"{123}"}}""")
            response.headers['content-type'] = 'application/json'
            return response
        except Exception as e:
            print(e)
            return "", 500
