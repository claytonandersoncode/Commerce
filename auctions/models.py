from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.title}"

class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    startbid = models.FloatField(null=True)
    imageurl = models.URLField()
    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE, related_name="category")
    is_active = models.BooleanField(default=True)
    who_created = models.ForeignKey(User, on_delete=models.CASCADE, related_name="who_created")
    who_won = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="who_won")


    def __str__(self):
        return f"{self.title} by {self.who_created}"

class Bid(models.Model):
    bid = models.FloatField()
    who_bid = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    which_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.who_bid} bid {self.bid} on {self.which_listing} at {self.time}"

class Comment(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    who_commented = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now=True)
    which_listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} by {self.who_commented} on {self.which_listing}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} is watching {self.listing}"
