from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# username and password for testing
USERNAME = "admin"
PASSWORD = "1234"

app = Flask(__name__)

# jwt configuration
app.config['JWT_SECRET_KEY'] = "secret1246"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

jwt = JWTManager(app)

# setting our DB settiongs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)


class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    details = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'Task("{self.title}", "{self.created_at}")'


db.create_all()  # migration


@app.route('/task', methods=['GET', 'POST'])
def task():
    if request.method == 'GET':
        all_tasks = Task.query.all()
        result = []
        for task in all_tasks:
            dict = {}
            dict['id'] = task.id
            dict['title'] = task.title
            dict['details'] = task.details
            dict['created_at'] = task.created_at

            result.append(dict)

        return jsonify({
            "status": "success",
            "data": result
        })

    if request.method == 'POST':
        title = request.json.get('title')
        details = request.json.get('details')
        created_at = request.json.get('created_at')

        newTask = Task(title=title, details=details, created_at=created_at)
        db.session.add(newTask)
        db.session.commit()

        return jsonify({
            "status": "success",
            "data": f"task {title} added successfully"
        })


@app.route('/task/<int:id>', methods=['GET', 'DELETE', 'PUT'])
@jwt_required()
def edit_task(id):
    username = get_jwt_identity()
    print(username)
    task = Task.query.filter_by(id=id).first()
    if request.method == 'GET':
        dict = {}
        dict['id'] = task.id
        dict['title'] = task.title
        dict['details'] = task.details
        dict['created_at'] = task.created_at

        return jsonify({
            "data": dict
        })

    if request.method == 'PUT':
        if request.json.get('title'):
            task.title = request.json.get('title')
        if request.json.get('details'):
            task.details = request.json.get('details')

        db.session.commit()

        return jsonify({
            "status": "success",
            "data": "user upadted successfully"
        })

    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()

        return jsonify({
            "status": "success",
            "data": "user deleted successfully"
        })


# authentication end points
@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    if data['username'] == USERNAME and data['password'] == PASSWORD:
        access_token = create_access_token(identity=data["username"])

        return jsonify({
            "status": "success",
            "data": {'access_token': access_token}
        })

    else:
        return jsonify({
            "status": "fail",
            'msg': 'wrong username or password'
        })


@app.route('/')
def home():
    return "<h1> Welcome in Home Page </h1>"


app.run(debug=True)
