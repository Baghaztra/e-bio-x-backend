from src import app
from src.config.database import db

@app.route('/')
def hello_world():
    return 'Server is running!'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
