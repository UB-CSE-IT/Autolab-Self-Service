import os

from flask import Flask, Blueprint, jsonify
from dotenv import load_dotenv

from backend.connections.AutolabApiConnection import AutolabApiConnection
from backend.connections.InfosourceConnection import InfoSourceConnection
from backend.CourseStore import CourseStore

load_dotenv()
app = Flask(__name__)
app.api = Blueprint("api", __name__)
app.autolab = AutolabApiConnection(os.getenv("AUTOLAB_ROOT"), os.getenv("AUTOLAB_CLIENT_ID"),
                                   os.getenv("AUTOLAB_CLIENT_SECRET"), os.getenv("AUTOLAB_CLIENT_CALLBACK"))
app.infosource = InfoSourceConnection(os.getenv("INFOSOURCE_USERNAME"),
                                      os.getenv("INFOSOURCE_PASSWORD"), os.getenv("INFOSOURCE_DSN"))
app.course_store = CourseStore(app.infosource)

@app.api.route("/")
def index():
    return jsonify({"message": "Hello, world!"})


@app.api.route("/my-courses/<string:username>/")
def my_courses(username: str):
    return jsonify(app.course_store.get_professors().get(username).to_dict())


def main():
    app.register_blueprint(app.api, url_prefix="/api")
    app.run("0.0.0.0", 5057)


if __name__ == '__main__':
    main()
