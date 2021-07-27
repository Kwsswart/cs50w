from django.urls import path

from . import views

app_name = "myapp"

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry_page, name="entry_page"),
    path("search", views.search, name='search'),
    path('new_page', views.new_page, name="new_page"),
    path("random", views.random_entry, name="random"),
    path('edit/<str:title>', views.edit, name="edit"), 
    path('remove/<str:title>', views.remove, name="remove")
]
