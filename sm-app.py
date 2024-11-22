from app import sm_app, db
from app.models import Moallim


@sm_app.shell_context_processor
def make_shell_context():
    return {"sm_app": sm_app, "db": db, "Moallim": Moallim}

    # if __name__ == '__main__':
    # serve(sm_app, host='0.0.0.0', port=8080)
    # sm_app.run()
