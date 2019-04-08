import json
from typing import List

from celery.result import AsyncResult
from flask import Flask, request, jsonify, send_from_directory
from celery import Celery
import redis


from definitions import ARCHIVES_DIR, TEXTS_DIR, IMAGES_SCRAPING_TYPE, TEXTS_SCRAPING_TYPE
from models.models import TaskModel, INITIATED_STATUS, IMAGES_TYPE, TEXTS_TYPE
from resource_scrapers.website_scraper import ImageScraper, TextScraper

app = Flask(__name__)
r = redis.Redis(decode_responses=True)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

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


@celery.task(bind=True)
def scraping_task(self, website_url: str, type: str):
    resource_name: str = None

    if type == IMAGES_SCRAPING_TYPE:
        resource_scraper: ImageScraper = ImageScraper(website_url, self.request.id.__str__())
        resource_scraper.pull_images_from_html_references()
        resource_name = resource_scraper.images_folder_name
    elif type == TEXTS_SCRAPING_TYPE:
        resource_scraper: TextScraper = TextScraper(website_url, self.request.id.__str__())
        resource_scraper.pull_texts()
        resource_name = resource_scraper.texts_file_name

    return {'resource_name': resource_name}


@app.route('/scrap/images', methods=['POST'])
def scrap_images() -> str:
    url: str = request.json['web_url']

    task = scraping_task.apply_async(kwargs={'website_url': url, 'type': IMAGES_SCRAPING_TYPE})
    task_model: TaskModel = TaskModel(task.id, INITIATED_STATUS, url, None, IMAGES_TYPE)
    r.set(f'task:{task_model.id}', json.dumps(task_model._asdict()))

    return jsonify({'taskId': task_model.id})


@app.route('/scrap/texts', methods=['POST'])
def scrap_texts() -> str:
    url: str = request.json['web_url']

    task = scraping_task.apply_async(kwargs={'website_url': url, 'type': TEXTS_SCRAPING_TYPE})

    task_model: TaskModel = TaskModel(task.id, INITIATED_STATUS, url, None, TEXTS_TYPE)
    r.set(f'task:{task.id}', json.dumps(task_model._asdict()))

    return jsonify({'taskId': task_model.id})


@app.route('/tasks/status', methods=['GET'])
def get_task_status():
    task_id: str = request.args['task_id']
    task_model: TaskModel = get_updated_task_model(task_id)

    return jsonify({'task_id': task_id, 'task_status': task_model.status})


@app.route('/tasks/all', methods=['GET'])
def get_all_task_names():

    tasks: List[str] = [key[key.find(':')+1:] for key in r.keys('*task*')]
    return jsonify(tasks)


@app.route('/tasks/task-resource-data', methods=['GET'])
def get_task_resource():
    task_id: str = request.args['task_id']

    task_model = get_updated_task_model(task_id)

    return jsonify({'task_id': task_model.id, 'resource_type': task_model.resource_type,
                    'task_resource_id': task_model.resource_name})


def get_updated_task_model(task_id) -> TaskModel:
    old_task_model: TaskModel = TaskModel.from_json(r.get(f'task:{task_id}'))
    result: AsyncResult = scraping_task.AsyncResult(task_id)

    if result is None:
        return None

    new_task_model = TaskModel(old_task_model.id, result.status, old_task_model.url,
                               result.info.get('resource_name', None), old_task_model.resource_type)
    r.set(f'task:{new_task_model.id}', json.dumps(new_task_model._asdict()))

    return new_task_model


@app.route('/resources/download-images', methods=['GET'])
def get_images_archive():
    resource_file_name: str = '.'.join([request.args['task_resource_id'], 'zip'])

    return send_from_directory(ARCHIVES_DIR, resource_file_name, as_attachment=True)


@app.route('/resources/download-texts', methods=['GET'])
def get_text_file():
    resource_file_name: str = '.'.join([request.args['task_resource_id'], 'txt'])

    return send_from_directory(TEXTS_DIR, resource_file_name, as_attachment=True)


if __name__ == '__main__':
    app.run()
