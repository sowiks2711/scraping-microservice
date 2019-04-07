import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(ROOT_DIR, 'tmp/images')
ARCHIVES_DIR = os.path.join(ROOT_DIR, 'tmp/archives')
TEXTS_DIR = os.path.join(ROOT_DIR, 'tmp/texts')

redis_host = "localhost"
redis_port = 6379
redis_password = ""