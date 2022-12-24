import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
'mma_project.settings')

import django
django.setup()

import pandas as pd
from upcoming_fights.models import FighterRankingDataScraper

scraper = FighterRankingDataScraper()

scraper.update_fighter_rankings()

