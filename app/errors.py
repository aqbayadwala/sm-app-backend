from flask import jsonify
from app import sm_app


@sm_app.errorhandler(500)
def internal_server_error(error):
    print(f"{error}")
    response = jsonify({"error": f"{error}"})
    return response, 500
