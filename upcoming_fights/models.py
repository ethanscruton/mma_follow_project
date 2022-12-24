from django.db import models
from django.contrib.auth.models import User
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime
import string
from unidecode import unidecode

class Fighter(models.Model):
    fighter_id = models.CharField(max_length=128, primary_key=True)
    name = models.CharField(max_length=256)
    nickname = models.CharField(max_length=256, default="")
    height = models.CharField(max_length=64, default="")
    weight = models.CharField(max_length=64, default="")
    reach = models.CharField(max_length=64, default="")
    stance = models.CharField(max_length=64, default="")
    wins = models.IntegerField(default = 0)
    losses = models.IntegerField(default = 0)
    draws = models.IntegerField(default = 0)
    followers = models.IntegerField(default = 0)

    def __str__(self):
        return self.name

    def get_URL(self):
        return "http://www.ufcstats.com/fighter-details/" + self.fighter_id

    def get_upcoming_fight(self):
        try:
            return self.upcoming_fight
        except UpcomingFight.DoesNotExist:
            return None

    def is_first_follow(self):
        # Returns True if no one has followed this fighter before, False otherwise
        followers = Follow.objects.filter(fighter = self)
        if followers:
            return False
        else:
            return True


class Follow(models.Model):

    fighter = models.ForeignKey(Fighter, related_name='follow', on_delete=models.PROTECT)
    user = models.ForeignKey(User, related_name='follow', on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username + ": " + self.fighter.name

    
class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    

class UpcomingFight(models.Model):

    fighter = models.OneToOneField(Fighter, related_name='upcoming_fight', on_delete=models.PROTECT)
    opponent = models.OneToOneField(Fighter, related_name='o_upcoming_fight', on_delete=models.PROTECT)
    date = models.DateField()
    event = models.CharField(max_length=128)

    def __str__(self):
        return self.fighter.name + " vs. " + self.opponent.name

class FighterRankingList(models.Model):
    
    list_name = models.CharField(max_length = 128)

    def __str__(self):
        return self.list_name

    def add_fighter_by_name(self, fighter_name, rank_num):
        try:
            fighter = Fighter.objects.get(name=fighter_name)
            FighterRanking.objects.create(
                fighter=fighter,
                rank=rank_num,
                ranking_list=self
            )
        except Fighter.DoesNotExist:
            pass
    
    def get_ordered_ranking_list(self):
        ordered_list = FighterRanking.objects.filter(ranking_list=self).order_by('rank')
        return ordered_list

class FighterRanking(models.Model):

    fighter = models.ForeignKey(Fighter, on_delete=models.PROTECT)
    rank = models.IntegerField(default=-1)
    ranking_list = models.ForeignKey(FighterRankingList, on_delete=models.CASCADE)

    def __str_(self):
        return self.ranking_list.list_name + ": " + str(self.rank) + ". " + self.fighter.name

# scrapes ufcstats.com to create fighter database
class FighterDataScraper():

    def create_fighters_from_ufcstats(self):
        alphabet = list(string.ascii_lowercase)
        base_URL = "http://www.ufcstats.com/statistics/fighters"
        for c in alphabet:
            curr_URL = base_URL + "?char={}&page=all".format(c)
            self.__create_fighters_from_ufcstats_page(curr_URL)
    
    def __create_fighters_from_ufcstats_page(self, curr_URL):
        page = requests.get(curr_URL)
        soup = BeautifulSoup(page.text, "html.parser")
        fighter_table = soup.find("tbody")
        fighter_rows = fighter_table.find_all("tr")

        for row in fighter_rows[1:]:
            self.__create_fighter_from_row(row)
    
    def __create_fighter_from_row(self, row):
        base_URL = "http://www.ufcstats.com/fighter-details/"
        columns = row.find_all("td")

        fighter_URL = columns[0].find("a")['href']
        fighter_id = fighter_URL.replace(base_URL, "")

        firstname = columns[0].text.strip()
        lastname = columns[1].text.strip()
        name = firstname + " " + lastname

        nickname = columns[2].text.strip()
        height = columns[3].text.strip()
        weight = columns[4].text.strip()
        reach = columns[5].text.strip()
        stance = columns[6].text.strip()
        wins = int(columns[7].text)
        losses = int(columns[8].text)
        draws = int(columns[9].text)

        Fighter.objects.create(
            fighter_id=fighter_id,
            name=name,
            nickname=nickname,
            height=height,
            weight=weight,
            reach=reach,
            stance=stance,
            wins=wins,
            losses=losses,
            draws=draws,
        )

# scrapes ufcstats.com to find information about a fighters upcoming fight
class UpcomingFightDataScraper():
    
    # returns upcoming fight data for fighter as an UpcomingFight model
    def find_upcoming_fight(self, fighter):
        page = requests.get(fighter.get_URL())
        soup = BeautifulSoup(page.text, "html.parser")
        if soup.find("tr", class_="b-fight-details__table-row_type_first"):
            fight_row = soup.find(class_="b-fight-details__table-row_type_first")
            self.__update_fighter_upcoming_fight_data(fighter, fight_row)
    
    # updates upcoming fight data
    def __update_fighter_upcoming_fight_data(self, fighter, fight_row):
        scraped_fight = self.__get_scraped_fight(fight_row)
        curr_fight = fighter.get_upcoming_fight()

        if curr_fight:
            fight_changes = self.__check_fight_changes(curr_fight, scraped_fight)
            if fight_changes:
                self.__email_fight_changes(fighter, fight_changes)
        else:
            created_fight = UpcomingFight.objects.create(
                fighter = fighter,
                opponent = scraped_fight['opponent'],
                event = scraped_fight['event'],
                date = scraped_fight['date']
            )
            self.__email_new_fight(created_fight)


    # scrapes fight_row for the upcoming fight data and returns a dictionary of it
    def __get_scraped_fight(self, fight_row):
        columns = fight_row.find_all("td")
        base_URL = "http://www.ufcstats.com/fighter-details/"

        # opponent
        opponent_id = columns[1].find_all("p")[1]
        opponent_id = opponent_id.find("a")['href'].replace(base_URL, "")
        opponent = Fighter.objects.get(fighter_id = opponent_id)

        # event
        event_details = columns[5].find_all("p")
        event = event_details[0].text.strip()

        # date
        date_text = event_details[1].text.strip()
        date = datetime.strptime(date_text, '%b. %d, %Y').date()

        # populate dictionary
        scraped_fight = {}
        scraped_fight['opponent'] = opponent
        scraped_fight['event'] = event
        scraped_fight['date'] = date
        return scraped_fight

    # checks for any updates to existing fight and returns changes.
    # also updates the existing UpcomingFight model
    def __check_fight_changes(self, curr_fight, scraped_fight):
        fight_changes = {}

        if curr_fight.opponent != scraped_fight['opponent']:
            fight_changes['opponent'] = {'previous': curr_fight.opponent, 
                'current': scraped_fight['opponent']}
            curr_fight.opponent = scraped_fight['opponent']

        if curr_fight.date != scraped_fight['date']:
            fight_changes['date'] = {'previous': curr_fight.date, 
                'current': scraped_fight['date']}
            curr_fight.date = scraped_fight['date']

        if curr_fight.event != scraped_fight['event']:
            fight_changes['event'] = {'previous': curr_fight.event, 
                'current': scraped_fight['event']}
            curr_fight.event = scraped_fight['event']

        curr_fight.save()
        return fight_changes

    # emails fight change details to any followers of fighter
    def __email_fight_changes(self, fighter, fight_changes):
        subject = fighter.name + " Fight Changed"
        message = ""
        email_from = settings.EMAIL_HOST_USER

        follow_model_list = Follow.objects.filter(fighter=fighter)
        recipient_list = []
        for follow_model in follow_model_list:
            recipient_list.append(follow_model.user.email)

        if recipient_list:
            if 'opponent' in fight_changes:
                opponent = fight_changes['opponent']
                message += "Opponent changed from {} to {}\n".format(opponent['previous'].name, opponent['current'].name)
            if 'date' in fight_changes:
                date = fight_changes['date']
                message += "Date changed from {} to {}\n".format(date['previous'], date['current'])
            if 'event' in fight_changes:
                promotion = fight_changes['event']
                message += "Event changed from {} to {}\n".format(promotion['previous'], promotion['current'])

            for recipient in recipient_list:
                send_mail(subject, message, email_from, [recipient])
        
        return
    
    # emails new fight details to any followers of fighter
    def __email_new_fight(self, new_fight):
        subject = "Fight Scheduled for " + new_fight.fighter.name
        message = ""
        email_from = settings.EMAIL_HOST_USER        
        
        follow_model_list = Follow.objects.filter(fighter=new_fight.fighter)
        recipient_list = []
        for follow_model in follow_model_list:
            recipient_list.append(follow_model.user.email)
        
        if recipient_list:
            message = "Opponent: {}\nDate: {}\nEvent: {}\n".format(
                new_fight.opponent.name, new_fight.date, new_fight.event
            )
            
            for recipient in recipient_list:
                send_mail(subject, message, email_from, [recipient])
        
        return

class FighterRankingDataScraper(models.Model):
    ranking_list_names = [
        "Men's pound for pound",
        "Women's pound for pound",
        "Heaveyweight",
        "Light Heavyweight",
        "Middleweight",
        "Welterweight",
        "Lightweight",
        "Featherweight",
        "Bantamweight",
        "Flyweight",
        "Women's Bantamweight",
        "Women's Flyweight",
        "Women's Strawweight"
    ]
    ranking_URL = "https://en.wikipedia.org/wiki/UFC_Rankings"
    
    def update_fighter_rankings(self):
        FighterRankingList.objects.all().delete()
        ranking_tables = self.__get_ranking_tables()
        for (list_name,table) in zip(self.ranking_list_names,ranking_tables):
            self.__create_ranking_list_by_table(list_name, table)

    def __get_ranking_tables(self):
        page = requests.get(self.ranking_URL)
        soup = BeautifulSoup(page.text, "html.parser")
        ranking_tables = soup.find_all(class_="wikitable")[1:]
        return ranking_tables

    def __create_ranking_list_by_table(self, list_name, table):
        ranking_list = FighterRankingList.objects.create(list_name=list_name)
        rows = table.find_all("tr")[2:]
        if "pound for pound" in list_name:
            rank_num = 1
        else:
            rank_num = 0
        for row in rows:
            fighter_name = row.find_all("td")[1].text.strip()
            fighter_name = unidecode(fighter_name)
            ranking_list.add_fighter_by_name(fighter_name, rank_num)
            rank_num += 1
