from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newListing", views.newListing, name="newListing"),
    path("listing/<int:number>", views.listingPage, name="listingPage"),
    path("listingUpdates", views.listingUpdates, name="listingUpdates"),
    path("watchList", views.watchList, name="watchList"),
    path("endBid", views.endBid, name="endBid"),
    path("newComment", views.newComment, name="newComment"),
    path("watchedListings", views.watchedListings, name="watchedListings"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.categories2, name="categories2")
]
