from statistics import mode
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class auction_listings(models.Model):
    name = models.CharField(max_length=200)
    imgURL = models.URLField(blank=True)
    detail = models.TextField()
    starting = models.IntegerField(default=0)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

class bid_record(models.Model):
    aid = models.ForeignKey(auction_listings, on_delete=models.CASCADE)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.IntegerField()

class comments(models.Model):
    aid = models.ForeignKey(auction_listings, on_delete=models.CASCADE)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()

class Watch_list(models.Model):
    aid = models.ForeignKey(auction_listings, on_delete=models.CASCADE)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)