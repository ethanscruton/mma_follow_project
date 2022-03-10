import os
from decouple import config
import celery

app = celery.Celery('upcoming_fights')
app.conf.update(BROKER_URL=config('REDIS_URL'),
                CELERY_RESULT_BACKEND=config('REDIS_URL'))

@app.task
def add(x, y):
    return x + y