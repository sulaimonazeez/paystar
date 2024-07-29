from django.urls import path
from . import views
urlpatterns = [
  path("", views.welcome),
  path("accounts/login/", views.logged),
  path("accounts/create/", views.register),
  path("home", views.home, name="home"),
  path("generate_account", views.generate_virtual_account),
  path("logout", views.push_out),
  path("history", views.transaction_history),
  path("notification", views.notification),
  path("nightmode", views.night_mode),
  path("databundle", views.purchase_data), 
  path("purchase", views.buy_bundle),
  path("myreciept/<int:id>/", views.myreciept),
  path("invoice/<int:id>/", views.InvoicePDFView.as_view()),
  path("profile", views.profile, name="profile"),
  path("change/password/", views.change_password),
  path("change/pin/", views.change_pin),
  path("finder/", views.SearchResultsView.as_view()),
]