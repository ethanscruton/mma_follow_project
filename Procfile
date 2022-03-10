web: gunicorn mma_project.wsgi
worker: celery -A upcoming_fights.tasks worker -B --loglevel=info