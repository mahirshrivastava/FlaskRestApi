
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restapi.db'

class TaskList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    summary = db.Column(db.String(500))

# db.create_all()

class HelloWorld(Resource):
    def get(self):
        return { 'data' : 'Hello ! World'}

class HelloName(Resource):
    def get(self, name):
        return { 'data' : 'Hello, {}'.format(name)}

resource_field = {
    'id' : fields.Integer,
    'task': fields.String,
    'summary': fields.String
}

post_args = reqparse.RequestParser()
post_args.add_argument("task", type=str, help="Task is required", required=True  )
post_args.add_argument("summary", type=str, help="Task is required", required=True  )

update_args = reqparse.RequestParser()
update_args.add_argument("task", type=str)
update_args.add_argument("summary",type=str)

class GetTaskList(Resource):
    def get(self):
        task = TaskList.query.all()
        task_list = {}
        for tasks in task:
            task_list[tasks.id] = { 'task': tasks.task, 'summary': tasks.summary}
        return task_list

class TaskPerform(Resource):
    @marshal_with(resource_field)
    def get(self, id):
        task = TaskList.query.filter_by(id=id).first()
        if not task:
            abort(408, 'Task is not present in the list.')
        return task

    @marshal_with(resource_field)
    def post(self, id):
        args = post_args.parse_args()
        task = TaskList.query.filter_by(id=id).first()
        if task:
            abort(409, "Task is already present in Task List")
        add_task = TaskList(id=id, task=args['task'], summary=args['summary'])
        db.session.add(add_task)
        db.session.commit()
        return add_task

    @marshal_with(resource_field)
    def put(self, id):
        args = update_args.parse_args()
        task = TaskList.query.filter_by(id=id).first()
        if not task:
            abort(408, "Task is not present in Task List")
        if args['task']:
            task.task = args['task']
        if args['summary']:
            task.summary = args['summary']
        db.session.commit()
        return task

    def delete(self, id):
        task = TaskList.query.filter_by(id=id).first()
        db.session.delete(task)
        db.session.commit()
        return 'Task Deleted', 204



api.add_resource(HelloWorld, '/helloworld')
api.add_resource(HelloName, '/helloworld/<string:name>')
api.add_resource(TaskPerform, '/tasklist/<int:id>')
api.add_resource(GetTaskList, '/tasklist')


if __name__ == '__main__':
    app.run(debug=True)