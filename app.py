from flask_restful import Api
from factory import create_app

app = create_app()
api = Api(app, prefix='/api')


@app.errorhandler(500)
def handle_exception(err):
    print(str(err))
    response = {
        "displayMessage": "A server error occurred",
        "error": str(err)
    }

    return response, 500


app.register_error_handler(500, handle_exception)


@app.route("/", defaults={'path': ''})
def serve(path):
    return "hello, world"
