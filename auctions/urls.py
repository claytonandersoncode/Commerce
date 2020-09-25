from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:id>/<str:title>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("modify_watchlist/<int:id>/<str:title>", views.modify_watchlist, name="modify_watchlist"),
    path("categories", views.categories, name="categories"),
    path("category/<str:title>", views.category, name="category"),
    path("comment/<int:id>/<str:title>", views.comment, name="comment"),
    path("end_auction/<int:id>", views.end_auction, name="end_auction"),
    path("bid/<int:id>/<str:title>", views.bid, name="bid")
]
