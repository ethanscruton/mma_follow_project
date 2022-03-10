from mma_project.celery import app

from .models import Follow, Fighter
from decouple import config

import celery

from celery.schedules import crontab

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(30.0, populate_followed_upcoming_fights.s())

@app.task
def populate_followed_upcoming_fights():
    all_followed_fighters = Fighter.objects.values_list('Fighter', flat=True).distinct()
    for fighter in all_followed_fighters:
        fighter.find_upcoming_fight_and_email_results()
    
    return