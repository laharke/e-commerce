from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages


from .models import User, Listing, Comment


def index(request):
    #Necesito primero hacer un query para agarrar toda la info de las listing que tengo
    #Y despues lo mando al HTML y de ahi loopeo
    
    #dejo esto out a ver si puedo agarrar las listing sol oactives
    #listings = Listing.objects.all()
    listings = Listing.objects.filter(active=True)

    return render(request, "auctions/index.html", {
            "listing": listings
            })

def watchedListings(request):
    user = request.user
    listings = user.watchedListings.all()

    return render(request, "auctions/index.html", {
            "listing": listings
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

class NewListingForm(forms.Form):
    CATEGORY = (
            ('Fashion', 'Fashion'),
            ('Home', 'Home'),
            ('Electronics', 'Electronics'),
            ('Toys', 'Toys'),
            ('Games', 'Games'),
            )

    title = forms.CharField(max_length=100)
    description = forms.CharField(max_length=300)
    starting_bid = forms.FloatField()
    category = forms.ChoiceField(choices=CATEGORY)
    img_url = forms.CharField(required=False, max_length=300)

    

def newListing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            #esto es para crear el model y dsp guardarl oen la base de datos
            listing = Listing()
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            category = form.cleaned_data["category"]
            if form.cleaned_data["img_url"] != "":
                img_url = form.cleaned_data["img_url"]
                listing.img_url = img_url
            username = request.user
            print(title, description, starting_bid, username)
            listing.title = title
            listing.description = description
            listing.starting_bid = starting_bid
            listing.current_bid = 0
            listing.creatorUser = username
            listing.category = category
            listing.save()
            id = listing.id
            return redirect('listingPage', number=id)
    else:
        return render(request, "auctions/newlisting.html", {
        "form": NewListingForm()
    })


def listingPage(request, number):
    listing = Listing.objects.get(id=number)
    #print(listing)
    comments = listing.get_comments.all()
    #print(comments)
    #ya tengo los commetns habria que populrlso allá

    #Necesito saber si el usuario loggeado sigue la lista para ver que boton le muestro, si el de follow o unfollow
    print(listing.watchers.all())
    if request.user in listing.watchers.all():
        watched = True
    else:
        watched = False
    
    #necesito saber si el usuario que entra al listing es el mismo que la creó.
    if request.user == listing.creatorUser:
        creator = True
    else:
        creator = False

    #necesito saber si seta active o no
    active = listing.active

    #sabre si es el buyer
    if request.user == listing.buyerUser:
        buyer = True
    else:
        buyer = False

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "watched": watched,
        "creator": creator,
        "active": active,
        "buyer": buyer
    })

    #IMPORTANTE NO OLVIDARSE DE IMPLEMTNAR ESTO:
    #si no existe mando el not found
    #else:
    #    messages.error(request, 'Entry not found')
    #    return redirect('/')

def listingUpdates(request):
    if request.POST["newBid"]:
            print("ES NEW BID")
            newBid = request.POST["newBid"]
            id = request.POST["listingID"]
            listing = Listing.objects.get(id=id)

            if listing.current_bid == 0:
                #si current bid es 0 quiere decir que nadie ofert'o asique una oferta IGUAL O MAYOR a la starting es aceptada
                if int(newBid) >= int(listing.starting_bid):
                    listing.current_bid = newBid
                    listing.buyerUser = request.user
                    listing.save()
                    messages.success(request, 'You have set an offer for this item')
                    return redirect('listingPage', number=id)
                else:
                    messages.error(request, 'Invalid Bid') #esto anda porque importa messages, y dsp tengo que recibirlo (en listing, la verdad que GENIALDAID ESTO, en la docu esta como)
                    return redirect('listingPage', number=id)
            else:
                if int(newBid) > int(listing.current_bid):
                    listing.current_bid = newBid
                    listing.buyerUser = request.user
                    listing.save()
                    messages.success(request, 'You have set an offer for this item')
                    return redirect('listingPage', number=id)
                else:
                    messages.error(request, 'Invalid Bid') #esto anda porque importa messages, y dsp tengo que recibirlo (en listing, la verdad que GENIALDAID ESTO, en la docu esta como)
                    return redirect('listingPage', number=id)
    #aca voy a hacerun if post [] si me llega el post de lwtachlist para add o remove
    #CREO QUE LO VOY A SEPARAR DE VIEW PORQUE SINO ES UN QUILOMBO CORROBAR EN QUE POST ESTO

def watchList(request):
    if request.POST.get('removeWatchlist', False):
        #Aca lo que voy a hacer es listing_object.watchers.remove(request.user) si tengo que removerlo y listing_object.watchers.add(request.user) si necesito agregalo
        id = request.POST["listingID"]
        user = request.user
        listing = Listing.objects.get(id=id)
        listing.watchers.remove(user)
        messages.success(request, 'You have removed this listing from your watchlist')
        return redirect('listingPage', number=id)
    if request.POST.get('addWatchlist', False):
        id = request.POST["listingID"]
        user = request.user
        listing = Listing.objects.get(id=id)
        listing.watchers.add(user)
        messages.success(request, 'You have added this listing to your watchlist')
        return redirect('listingPage', number=id)

    #la joda seria hacer un if request.POST[""] con cada uno de los datos del post: el bid / agregar a watchlist / agregar comment /
    #/cerrar la bid si soy el user que la creó

def endBid(request):
    id = request.POST["listingID"]
    listing = Listing.objects.get(id=id)
    listing.active = False
    listing.save()
    messages.success(request, 'You have sucessfully closed the auction!')
    return redirect('listingPage', number=id)

def newComment(request):
    id = request.POST["listingID"]
    comment = request.POST["comment"]
    print(comment)
    listing = Listing.objects.get(id=id)
    newComment = Comment()
    newComment.user = request.user
    newComment.listing = listing
    newComment.comment = comment
    newComment.save()
    return redirect('listingPage', number=id)

def categories(request):
    #si llega un get, muestor un HTML con todas las categorias, y si llega un post queire decir que tocaron alguna categoria y tengo que popoular como con el INDEX y WATHCLISt
    # PERO con esa categoria asique CREO que es facil
    #primero el get
    if request.method == "GET":
        #html con las categorias
        listing = Listing()
        categoriesTuple = listing.CATEGORY
        categoriesTuple[0][0]
        print(categoriesTuple, categoriesTuple[0][0])
        categories = []
        for category in categoriesTuple:
            categories.append(category[0])
        print(categories)
        return render(request, "auctions/categories.html", {
        "categories": categories
    })


def categories2(request, category):
    listings = Listing.objects.filter(category=category, active=True)

    
    return render(request, "auctions/index.html", {
            "listing": listings,
            "category": category
            })