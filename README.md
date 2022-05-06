# [mmafollow.com](https://www.mmafollow.com)

## Short Description

A site where you can create an account and follow any Mixed Martial Arts (MMA) fighter. You receive email notifications whenever a fighter you follow has a new fight scheduled or has a scheduled fight changed.

## Background

As an avid UFC fan, I constantly found myself wasting an immense amount of time searching the internet for when new fights were being scheduled. I started brainstorming solutions to this problem and I finally settled on building a website where the news would be brought to me, instead of me searching for it.

I encountered many challenges while building this site and I learned a great deal about software/website development while overcoming these challenges. This project was by far the biggest I had ever undertaken. It was satisfying to be able to take an idea I had and build something at this scale that I am proud of.

## Built With

* [Django](https://www.djangoproject.com/)
* [Bootstrap](https://getbootstrap.com/)
* [JQuery](https://jquery.com/)
* [Heroku](https://www.heroku.com)

## Python Packages Used

* [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html): task queue
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): scraping web for fight data
* [django-registration-redux](https://django-registration-redux.readthedocs.io/en/latest/): user registration

## Website Features

### Homepage (logged out)

![homepage logged out](https://user-images.githubusercontent.com/67564744/167144231-a5e89579-bcac-47b7-aa42-4ae0175974f0.png)
---
### Homepage (logged in)

![homepage logged in](https://user-images.githubusercontent.com/67564744/167144447-09ae8462-cd25-44da-8967-e849176c9f60.png)
---
### Register

![register](https://user-images.githubusercontent.com/67564744/167144509-50790b84-274f-474b-b10e-9a2e9442a0b7.png)
---
### Login

![login](https://user-images.githubusercontent.com/67564744/167144590-ca14a947-1d2c-413b-8c02-5dbb8bebfe6e.png)
---
### Search Fighters
One of the two ways the user can find fighters to follow. The other way is through the trending page.

![search](https://user-images.githubusercontent.com/67564744/167144808-6729c482-434e-4bd2-9e09-ce97aaaeedd1.png)
---
### Following (unsorted)
A list of all fighters the user is following. The user can sort the list by clicking the table headers.

![following unsorted](https://user-images.githubusercontent.com/67564744/167144900-478d813e-b565-413a-abde-d46b22cc2fa4.png)
---
### Following (sorted by upcoming fight date)

![following sorted](https://user-images.githubusercontent.com/67564744/167144967-55dc1e7b-1360-4824-b3ae-cc9176786b1e.png)
---
### Trending
The second way a user can find fighters to follow. The trending page is a list of the most followed fighters by other users.

![trending](https://user-images.githubusercontent.com/67564744/167145006-c5451319-d9eb-4ef1-8ae3-e17733290d7b.png)
---
### E-mail Notification (fight scheduled)

![email fight scheduled](https://user-images.githubusercontent.com/67564744/167158700-122b3a5f-5369-4fd7-8322-bdab641fc107.png)
---
### E-mail Notification (fight changed)

![email fight changed](https://user-images.githubusercontent.com/67564744/167158881-11df9d47-90a6-46e0-bf0b-849b85e07b6a.png)
---
