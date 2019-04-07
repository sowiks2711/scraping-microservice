import json
from typing import List

from flask import Flask, request, jsonify, send_from_directory
import redis

from definitions import ARCHIVES_DIR, TEXTS_DIR
from models.models import Task, INITIATED_STATUS, IMAGES_TYPE, TEXTS_TYPE
from resource_scrapers.website_scraper import ImageScraper, TextScraper

app = Flask(__name__)
r = redis.Redis(decode_responses=True)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/list/archives')
def list_archives():
    return 'Hello World!'


@app.route('/scrap/images')
def scrap():
    url: str = request.args['x']

    resource_scraper = ImageScraper(url)
    resource_scraper.pull_images_from_html_references()
    response = 'Hello ' + request.args['x']
    return response


@app.route('/scrap/images', methods=['POST'])
def scrap_images() -> str:
    url: str = request.json['web_url']
    resource_scraper: ImageScraper = ImageScraper(url)

    task: Task = Task(resource_scraper.resource_guid, INITIATED_STATUS, url, None, IMAGES_TYPE)
    r.set(f'task:{task.id}', json.dumps(task._asdict()))

    resource_scraper.pull_images_from_html_references()
    return jsonify({'taskId': task.id})

@app.route('/scrap/texts', methods=['POST'])
def scrap_texts() -> str:
    url: str = request.json['web_url']
    resource_scraper: TextScraper = TextScraper(url)

    task: Task = Task(resource_scraper.resource_guid, INITIATED_STATUS, url, None, TEXTS_TYPE)
    r.set(f'task:{task.id}', json.dumps(task._asdict()))

    resource_scraper.pull_texts()

    return jsonify({'taskId': task.id})

@app.route('/tasks/status', methods=['GET'])
def get_task_status():
    task_id: str = request.args['task_id']
    task: Task = Task.from_json(r.get(f'task:{task_id}'))
    return jsonify({'task_id': task_id, 'task_status': task.status})


@app.route('/tasks/all', methods=['GET'])
def get_all_task_names():

    tasks: List[str] = [key[key.find(':')+1:] for key  in r.keys('*task*')]
    return jsonify(tasks)


@app.route('/tasks/task-resource-data', methods=['GET'])
def get_task_resource():
    task_id: str = request.args['task_id']
    task: Task = Task.from_json(r.get(f'task:{task_id}'))

    return jsonify({'task_id': task.id, 'resource_type': task.resource_type, 'task_resource_id': task.resource_name})


@app.route('/resources/download-images', methods=['GET'])
def get_images_archive():
    resource_file_name: str = request.args['task_resource_id']

    return send_from_directory(ARCHIVES_DIR, resource_file_name, as_attachment=True)


@app.route('/resources/download-texts', methods=['GET'])
def get_text_file():
    resource_file_name: str = request.args['task_resource_id']

    return send_from_directory(TEXTS_DIR, resource_file_name, as_attachment=True)



if __name__ == '__main__':
    app.run()
