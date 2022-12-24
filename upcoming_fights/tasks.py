from mma_project.celery import app

from .models import Follow, UpcomingFightDataScraper, FighterRankingDataScraper
from decouple import config

from celery.schedules import crontab

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1800.0, populate_followed_upcoming_fights.s())
    sender.add_periodic_task(86400.0, populate_fighter_rankings.s())

@app.task
def populate_followed_upcoming_fights():
    scraper = UpcomingFightDataScraper
    all_followed_fighters = []
    for follow in Follow.objects.all():
        if not follow.fighter in all_followed_fighters:
            all_followed_fighters.append(follow.fighter)
    for fighter in all_followed_fighters:
        scraper.find_upcoming_fight(fighter)
    
    return

@app.task
def populate_fighter_rankings():
    scraper = FighterRankingDataScraper
    scraper.update_fighter_rankings()
    
    return