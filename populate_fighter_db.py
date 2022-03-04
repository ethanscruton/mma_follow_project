import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
'mma_project.settings')

import django
django.setup()

import pandas as pd
from upcoming_fights.models import Fighter

tapology_data = pd.read_pickle('upcoming_fights/complete_sherdog_fighter_data.pkl')
tapology_data = tapology_data.drop_duplicates(subset=['Fighter ID'])

row_iter = tapology_data.iterrows()

fighters = [
    Fighter(
        fighter_id = row['Fighter ID'],
        name = row['Fighter Name'],
        nickname = row['Fighter Nickname'],
        height = row['Height'],
        weight_class = row['Weight Class'],
        association = row['Association'],
        country = row['Country']
    )
    for index, row in row_iter
]

Fighter.objects.bulk_create(fighters)