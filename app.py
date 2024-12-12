from app.models import Users, Secrets
from app import create_app, db

app = create_app()


@app.shell_context_processor
def make_shell_context():
    from app.models import Users, Secrets
    return {'db': db, 'User': Users, 'Secret': Secrets}


if __name__ == '__main__':
    app.run(debug=True)
