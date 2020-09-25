from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import Bid, Category, Comment, Listing, User, Watchlist

class CreateForm(forms.Form):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control'}))
    startbid = forms.FloatField(label="Starting Bid ($)", min_value=1, widget=forms.NumberInput(attrs={'class' : 'form-control'}))
    imageurl = forms.URLField(label="Image URL", widget=forms.TextInput(attrs={'class' : 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Choose a Category", widget=forms.Select(attrs={'class' : 'form-control'}))

class CommentForm(forms.Form):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control'}))

class BidForm(forms.Form):
    bid = forms.FloatField(label="New Bid ($)", min_value=1, widget=forms.NumberInput(attrs={'class' : 'form-control'}))

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_active=True),
    })

@login_required
def create(request):
    if request.method == "GET":
        return render(request, "auctions/create.html", {
            "createform": CreateForm()
        })
    else:
        # Take in the data the user submitted and save it as form
        form = CreateForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the variables from the 'cleaned' version of form data
            category = form.cleaned_data["category"]
            description = form.cleaned_data["description"]
            imageurl = form.cleaned_data["imageurl"]
            startbid = form.cleaned_data["startbid"]
            title = form.cleaned_data["title"]
            who_created = request.user

            # Create a listing object and a bid object related to it
            listing = Listing(category=category, description=description, imageurl=imageurl, title=title, who_created=who_created)
            listing.save()
            bid = Bid(bid=startbid, who_bid=who_created, which_listing=listing)
            bid.save()

            # Redirect user to index
            return HttpResponseRedirect(reverse("index"))

        else:

            # If the form is invalid, re-render the page with existing information.
            return render(request, "auctions/create.html", {
                "createform": form
            })

    return render(request, "auctions/create.html", {
        "createform": CreateForm()
    })

def listing(request, id, title):
    #Get the objects to pass into the listing template
    listing = Listing.objects.get(id=id)
    this_comments = Comment.objects.filter(which_listing=listing)
    topbid = Bid.objects.filter(which_listing=listing).order_by('bid').last()

    if request.user.is_authenticated:
        watchlist = Watchlist.objects.filter(listing=listing, user=request.user)
    else:
        watchlist = None
    
    return render(request, "auctions/listing.html", {
        "bidform": BidForm(),
        "commentform": CommentForm(),
        "comments": this_comments,
        "listing": listing,
        "topbid": topbid,
        "watchlist": watchlist
    })

@login_required
def watchlist(request): 
    return render(request, "auctions/watchlist.html", {
        "watchlist": Watchlist.objects.filter(user=request.user)
    })

@login_required
def modify_watchlist(request, id, title):
    listing = Listing.objects.get(id=id) 

    #If watchlist object exists, delete it, otherwise create it
    in_watchlist = Watchlist.objects.filter(listing=listing, user=request.user)
    if in_watchlist:
        in_watchlist.delete()
    else:
        watchlist = Watchlist(listing=listing, user=request.user)
        watchlist.save()

    return HttpResponseRedirect(reverse("listing", args=(listing.id, listing.title)))

def categories(request): 
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

def category(request, title): 
    category = Category.objects.get(title=title)
    return render(request, "auctions/category.html", {
        "category": category,
        "listings": Listing.objects.filter(category=category, is_active=True)
    })

@login_required
def bid(request, id, title):
    listing = Listing.objects.get(id=id)
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = BidForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the variables from the 'cleaned' version of form data
            bid = form.cleaned_data["bid"]
            who_bid = request.user
            topbid = Bid.objects.filter(which_listing=listing).order_by('bid').last()

            if bid > float(topbid.bid):
                bid = Bid(bid=bid, who_bid=who_bid, which_listing=listing)
                bid.save()
            else:
                messages.error(request, "Error: The bid must be larger than the previous bids")
                return HttpResponseRedirect(reverse("listing", args=(listing.id, listing.title)))  

            # Redirect user to listing
            return HttpResponseRedirect(reverse("listing", args=(listing.id, listing.title)))

        else:
            # If the form is invalid, re-render the page
            messages.error(request, "Error: The bid was invalid, please try a positive number")
            return HttpResponseRedirect(reverse("listing", args=(listing.id, listing.title)))

    return HttpResponseRedirect(reverse("listing", args=(listing.id, listing.title)))

@login_required
def comment(request, id, title):
    listing = Listing.objects.get(id=id)
    this_comments = Comment.objects.filter(which_listing=listing)
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = CommentForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the variables from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            who_commented = request.user.username

            # Do something with variables
            comment = Comment(content=content, title=title, which_listing=listing, who_commented=who_commented,)
            comment.save()

            # Redirect user to listing
            return HttpResponseRedirect(reverse("listing", args=(listing.id, listing.title)))
        else:

            # If the form is invalid, re-render the page with existing information.
            return render(request, "auctions/listing.html", {
                "bidform": Bidform(),
                "comments": this_comments,
                "commentform": form,
                "listing": listing,
            })

    return HttpResponseRedirect(reverse("listing", args=(listing.id, listing.title)))

def end_auction(request, id):
    listing = Listing.objects.get(id=id)
    
    #Set who won as the user with the highest bid
    topbid = Bid.objects.filter(which_listing=listing).order_by('bid').last()
    who_won = topbid.who_bid

    #Update the listing object, make it inactive and save who won
    end_auction = Listing.objects.filter(id=id).update(is_active=False, who_won=who_won)

    #Redirect back to the listing
    return HttpResponseRedirect(reverse("listing", args=(listing.id, listing.title)))

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
