# from curses import flash
# from itertools import chain

from wsgiref.util import request_uri
from django.db.models import Max
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse


from .models import User, Watch_list, auction_listings,bid_record, comments
from .forms import CreateForm


def index(request):
    data = auction_listings.objects.filter(is_active = True)
    
    return render(request, "auctions/index.html", {
        "data":data,
        "title": "Active"
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='/login')
def create_listing(request):
    if request.method == 'GET':
        form = CreateForm()
        return render(request, "auctions/createlist.html", {
            "form": form
        })
    else:
        name = request.POST['name']
        detail = request.POST['detail']
        imgURL = request.POST['imgURL']
        starting = request.POST['starting']
        user = User.objects.get(id = request.user.id)
        auction_listing = auction_listings(name=name,imgURL=imgURL, detail=detail,starting=starting, is_active = True)
        auction_listing.uid = user
        auction_listing.save()
        return redirect('/')



@login_required(login_url='/login')
def listings(request, auction_id):
    if request.method == 'GET':
        data = auction_listings.objects.get(id = auction_id)
        lists = Watch_list.objects.filter(aid = auction_id)

        now_price = data.starting
        maxPrice = bid_record.objects.filter(aid = auction_id).aggregate(Max('price'))
        if maxPrice['price__max'] != None:
            now_price = maxPrice['price__max']

        is_newOwner = False
        if data.is_active == False and request.user.id == bid_record.objects.get(aid = auction_id, price=now_price).uid.id:
            is_newOwner = True

        is_author = False
        if data.uid.id == request.user.id:
            is_author = True
        watched = False
        for list in lists:
            if request.user.id == list.uid.id:
                watched = True
                break;

        # 待测试
        auction_comments = comments.objects.filter(aid = auction_id)
        
        return render (request, "auctions/categories.html", {
            "data": data,
            "watched": watched,
            "minPrice": now_price,
            "isAuthor": is_author,
            "isNewOwner": is_newOwner,
            "comments": auction_comments
        })
    else:
        bid_price = request.POST['price']
        new_bid = bid_record(price = bid_price)
        aid = auction_listings.objects.get(id = auction_id)
        uid = User.objects.get(id = request.user.id)
        new_bid.aid = aid
        new_bid.uid = uid
        new_bid.save()
        return redirect('/listings/'+str(auction_id)+'/')


def addWatch(request, auction_id):
    aid = auction_listings.objects.get(id = auction_id)
    uid = User.objects.get(id = request.user.id)
    watched = Watch_list()
    watched.aid = aid
    watched.uid = uid
    watched.save()
    return redirect('/listings/'+str(auction_id)+'/')

def deleteWatch(request, auction_id):
    entry = Watch_list.objects.get(aid = auction_id, uid = request.user.id)
    entry.delete()
    return redirect('/listings/'+str(auction_id)+'/')


# # python 如何迭代查询呢
def watchList(request):
    lists = Watch_list.objects.filter(uid = request.user.id)
    return render(request, "auctions/watchlist.html", {
        "title": "Watched",
        "data": lists
    })


def close_auction(request, auction_id):
    data = auction_listings.objects.get(id = auction_id, uid = request.user.id)
    data.is_active = False
    data.save()
    return redirect('/')


def newcomment(request,auction_id):
    comment = request.POST['comment']
    aid = auction_listings.objects.get(id = auction_id)
    uid = User.objects.get(id = request.user.id)
    new_comment = comments(comment=comment)
    new_comment.aid = aid
    new_comment.uid = uid
    new_comment.save()
    return redirect('/listings/'+str(auction_id)+'/')
