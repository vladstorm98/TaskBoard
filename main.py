from app import create_app
from app import db
from app import cli
from app.models.task import Task
from app.models.user import User
from app.search import add_to_index

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Task': Task, 'User': User}


if __name__ == '__main__':
    app.run()


# flask shell
