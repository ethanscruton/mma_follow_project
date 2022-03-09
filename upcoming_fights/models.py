from django.db import models
from django.contrib.auth.models import User
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import send_mail

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Fighter(models.Model):

    fighter_id = models.CharField(max_length=128, primary_key=True)
    name = models.CharField(max_length=256)
    nickname = models.CharField(max_length=256, default="")
    height = models.CharField(max_length=64)
    weight_class = models.CharField(max_length=128)
    association = models.CharField(max_length=256, default="")
    country = models.CharField(max_length=64, default="")
    upcoming_fight = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def find_upcoming_fight(self):
        # Parses the fighter's sherdog webpage. 
        # Sets Fighter.upcoming_fight = True for the fighter if there is an upcoming fight. False otherwise.
        # Returns a dictionary containing upcoming fight data if there is a upcoming fight. Returns an empty dictionary otherwise.

        URL = "https://www.sherdog.com/fighter/" + self.fighter_id
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, "html.parser")

        fight_dict = {}

        fight_preview = soup.find_all(class_="fight_card_preview")
        
        if fight_preview:
            self.upcoming_fight = True
            self.save()
            
            fight_preview = fight_preview[0]

            # opponent
            fight_opponent_id = fight_preview.find("div", class_='fighter right_side')
            fight_opponent_id = fight_opponent_id.find("a")['href']
            fight_opponent_id = fight_opponent_id.replace("/fighter/", "")
            opponent = Fighter.objects.get(fighter_id=fight_opponent_id)
            fight_dict['opponent'] = opponent

            # date
            fight_date_split = fight_preview.find("div", class_="date_location").text.split()
            fight_date = fight_date_split[0]
            for word in fight_date_split[1:3]:
                fight_date += " " + word
            fight_dict['date'] = fight_date

            # promotion
            fight_promotion = fight_preview.find("h2", itemprop="name").text.strip()
            fight_dict['promotion'] = fight_promotion

            # location
            fight_location = fight_date_split[3]
            for word in fight_date_split[4:]:
                fight_location += " " + word
            fight_dict['location'] = fight_location

        else:
            self.upcoming_fight = False
            self.save()

        return fight_dict

        '''
            try:
                fight = UpcomingFight.objects.get(fighter=self)
                fight_differences = {}
                if fight.opponent != opponent:
                    fight_differences['opponent'] = {'previous': fight.opponent, 'current': opponent}

                if fight.date != fight_date:
                    fight_differences['date'] = {'previous': fight.date, 'current': fight_date}
                
                if fight.promotion != fight_promotion:
                    fight_differences['promotion'] = {'previous': fight.promotion, 'current': fight_promotion}

                fight.opponent = opponent
                fight.date = fight_date
                fight.promotion = fight_promotion
                fight.save()

                # self.email_fight_changes(fight_differences)

            except UpcomingFight.DoesNotExist:
                fight = UpcomingFight.objects.create(
                    fighter = self,
                    opponent = opponent,
                    date=fight_date,
                    promotion=fight_promotion
                )

                # self.email_new_fight(fight)

        elif self.upcoming_fight:
            UpcomingFight.objects.get(fighter=self).delete()
            self.upcoming_fight = False
            self.save()

        return
        '''

    def is_first_follow(self):
        # Returns True if no one has followed this fighter before, False otherwise
        followers = Follow.objects.filter(fighter = self)
        if followers:
            return False
        else:
            return True


    def new_follow_find_upcoming_fight(self):
        # Checks if there is an upcoming fight for this fighter.
        # If there is an upcoming fight, creates a new UpcomingFight model for the fighter.
        fighter_dict = self.find_upcoming_fight()
        if fighter_dict:
            UpcomingFight.objects.get_or_create(
                fighter = self,
                opponent = fighter_dict['opponent'],
                date = fighter_dict['date'],
                promotion = fighter_dict['promotion'],
                location = fighter_dict['location']
            )
        return

    def find_upcoming_fight_and_email_results(self):
        # Function run periodically to find and email changes to fighter's upcoming fight status
        fighter_dict = self.find_upcoming_fight()
        if fighter_dict:
            opponent = fighter_dict['opponent']
            fight_date = fighter_dict['date']
            fight_promotion = fighter_dict['promotion']
            fight_location = fighter_dict['location']

            try:
                fight = UpcomingFight.objects.get(fighter=self)

                fight_differences = {}

                if fight.opponent != opponent:
                    fight_differences['opponent'] = {'previous': fight.opponent, 'current': opponent}

                if fight.date != fight_date:
                    fight_differences['date'] = {'previous': fight.date, 'current': fight_date}
                
                if fight.promotion != fight_promotion:
                    fight_differences['promotion'] = {'previous': fight.promotion, 'current': fight_promotion}

                if fight.location != fight_location:
                    fight_differences['location'] = {'previous': fight.location, 'current': fight_location}

                fight.opponent = opponent
                fight.date = fight_date
                fight.promotion = fight_promotion
                fight.location = fight_location
                fight.save()

                if fight_differences:
                    self.email_fight_changes(fight, fight_differences)
                    return

            except UpcomingFight.DoesNotExist:
                fight = UpcomingFight.objects.create(
                    fighter=self,
                    opponent=opponent,
                    date=fight_date,
                    promotion=fight_promotion,
                    location=fight_location
                )

                self.email_new_fight(fight)
            return

    def email_fight_changes(self, fight, fight_differences):
        subject = self.name + " Fight Changed"
        message = ""
        email_from = settings.EMAIL_HOST_USER

        follow_model_list = Follow.objects.filter(fighter=self)
        recipient_list = []
        for follow_model in follow_model_list:
            recipient_list.append(follow_model.user.email)

        if recipient_list:
            if 'opponent' in fight_differences:
                opponent = fight_differences['opponent']
                message += "Opponent changed from {} to {}\n".format(opponent['previous'].name, opponent['current'].name)
            if 'date' in fight_differences:
                date = fight_differences['date']
                message += "Date changed from {} to {}\n".format(date['previous'], date['current'])
            if 'promotion' in fight_differences:
                promotion = fight_differences['promotion']
                message += "Card changed from {} to {}\n".format(promotion['previous'], promotion['current'])
            if 'location' in fight_differences:
                location = fight_differences['location']
                message += "Location changed from {} to {}\n".format(location['previous'], location['current'])

            send_mail(subject, message, email_from, recipient_list)
        
        return

    def email_new_fight(self, fight):
        subject = "Fight Scheduled for " + self.name
        message = ""
        email_from = settings.EMAIL_HOST_USER        
        
        follow_model_list = Follow.objects.filter(fighter=self)
        recipient_list = []
        for follow_model in follow_model_list:
            recipient_list.append(follow_model.user.email)
        
        if recipient_list:
            message = "Opponent: {}\nDate: {}\nPromotion: {}\nLocation: {}\n".format(
                fight.opponent.name, fight.date, fight.promotion, fight.location
            )
            
            send_mail(subject, message, email_from, recipient_list)
        
        return

class Follow(models.Model):

    fighter = models.ForeignKey(Fighter, related_name='follow', on_delete=models.PROTECT)
    user = models.ForeignKey(User, related_name='follow', on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username + ": " + self.fighter.name

class UpcomingFight(models.Model):

    fighter = models.OneToOneField(Fighter, related_name='upcoming_fighter', on_delete=models.PROTECT)
    opponent = models.OneToOneField(Fighter, related_name='upcoming_opponent', on_delete=models.PROTECT)
    date = models.CharField(max_length=64)
    promotion = models.CharField(max_length=128)
    location = models.CharField(max_length=128)

    def __str__(self):
        return self.fighter.name + " vs. " + self.opponent.name
