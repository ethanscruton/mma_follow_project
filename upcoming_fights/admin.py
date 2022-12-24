from django.contrib import admin
from upcoming_fights.models import Fighter, Follow, UpcomingFight, FighterRanking, FighterRankingList
admin.site.register(Fighter)
admin.site.register(Follow)
admin.site.register(UpcomingFight)
admin.site.register(FighterRanking)
admin.site.register(FighterRankingList)

# Register your models here.
