from flask import abort, request, send_file
from flask_restful import Resource
from flasgger import swag_from
import os


class FileApiHandler(Resource):

    # @swag_from('./../swagger/file_get.yml', methods=['GET'])
    def get(self):
        try:
            filename = request.args["fileName"]

            if (filename == ""):
                raise ""

            curr_dir_path = os.path.abspath(os.path.dirname(__file__))
            file_path = os.path.abspath(os.path.join(curr_dir_path, '..', 'celery/data/', filename))

            filename_general_parts = filename.rsplit('_')[:-1]
            filename_general = '_'.join(filename_general_parts)
            filename_ext = filename.rsplit('.')[-1]

            return send_file(file_path,
                             attachment_filename=f"{filename_general}.{filename_ext}",
                             as_attachment=True)

        except FileNotFoundError as e:
            response = {
                "displayMessage": "The file was not found",
            }

            return response, 404
        except Exception as e:
            abort(500, e)
