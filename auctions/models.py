from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

#Voy a crear tres classes, una listing enorme, una de commetnarios y una de biddings, deberia ser suficente.
class Listing(models.Model):
    CATEGORY = (
            ('Fashion', 'Fashion'),
            ('Home', 'Home'),
            ('Electronics', 'Electronics'),
            ('Toys', 'Toys'),
            ('Games', 'Games'),
            )

    title = models.CharField(max_length = 50)
    description = models.CharField(max_length = 300)
    starting_bid = models.FloatField()
    current_bid = models.FloatField(blank=True, null=True)
    category = models.CharField(max_length=150, null=True, choices=CATEGORY)
    img_url = models.CharField(blank=True, null=True, max_length=300)
    creatorUser = models.ForeignKey(User, on_delete=models.PROTECT, related_name="allCreatorsListings") # con un user, pongo user.allCreatorsListings.all()
    buyerUser = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT)
    watchers = models.ManyToManyField(User, blank=True, related_name='watchedListings') # con un user, pongo user.watchedListings.all()
    active = models.BooleanField(default=True) #esto es para ver si est'a activa, empiza default true, pero si el usuaro creador pone finalizar, se pone false, y no se puede ofertar

    def __str__(self):
        return f"{self.title} - {self.starting_bid} - {self.category}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="get_comments")   #con esto puedo sacar todos los comennts de una listing con listing.get_comments.all() una vez filtrada
    comment = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user} commented {self.comment} on {self.listing}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE)
    offer = models.FloatField()

    def __str__(self):
        return f"{self.user} bid {self.bid} on {self.auction}"