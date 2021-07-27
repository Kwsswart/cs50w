from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django import forms
from markdown2 import Markdown

from . import util
import re
import random


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry_page(request, title):
    markdown_converter = Markdown()
    
    if util.get_entry(title):
        return render(request, "encyclopedia/entry.html", {
            'title': title,
            'content': markdown_converter.convert(util.get_entry(title))
        })
    else:
        return render(request, "errors/404.html", {
            "title": title
        })
        
    
def search(request):
    markdown_converter = Markdown()
    if request.method == 'POST':
        if util.get_entry(request.POST.get("q")):
             return render(request, "encyclopedia/entry.html", {
            'title': request.POST.get("q"),
            'content': markdown_converter.convert(util.get_entry(request.POST.get("q")))
        })
        else:
            entries = util.list_entries()
            entries = [entry for entry in entries if re.search(re.compile(request.POST.get("q")), entry)]
            
            if entries:
                return render(request, "encyclopedia/index.html", {
                            "entries": entries
                        })
            else:
                return render(request,"encyclopedia/index.html", {
                            "entries": util.list_entries(),
                            "error": "Search Doesn't Match any entries"
                        })


def validate_title(title):
        if util.get_entry(title):
            raise forms.ValidationError("Title already exists")
        return title
    
class NewEntryform(forms.Form):
    
    title = forms.CharField(label='Entry Title', validators =[validate_title], widget=forms.TextInput(attrs={'class': 'title'}))
    textarea = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea', 'style': "max-height: 50vh"}))
        
            
def new_page(request):
    
    if request.method == "POST":
        
        form = NewEntryform(request.POST)
        
        if form.is_valid():
            # do whats needed
            title = form.cleaned_data["title"]
            text = form.cleaned_data["textarea"]
            
            util.save_entry(title, text)
            return HttpResponseRedirect(reverse("myapp:entry_page", args=[title]))
        else:
            #return HttpResponse(form.errors.values())
            return render(request, "encyclopedia/new_page.html", {
                "new_page": True,
                "heading": "New Entry",
                "form": form,
                "form_errors": form.errors["title"]
            })
    return render(request, "encyclopedia/new_page.html", {
        "new_page": True,
        "heading": "New Entry",
        'form': NewEntryform(),
        "form_errors": None
    })


def edit(request, title):
    
    if request.method == "POST":
        form = NewEntryform(request.POST)
        if form.data["textarea"] != util.get_entry(title) or form.data['title'] != title:
            if form.data['title'] != title:
                
                if form.is_valid():
                    util.delete_entry(title)
                    title = form.cleaned_data["title"]
                    text = form.cleaned_data["textarea"]
                else:
                    return render(request, "encyclopedia/new_page.html", {
                    "new_page": False,
                    "heading": "Edit Entry - " + title,
                    'title': title,
                    "form": form,
                    "form_errors": form.errors["title"]
                })
            else:
                title = form.data['title']
                text = form.data['textarea']
            
            util.save_entry(title, text)
            return HttpResponseRedirect(reverse("myapp:entry_page", args=[title]))
                
            
    
    content = util.get_entry(title)
    return render(request, "encyclopedia/new_page.html", {
        "new_page": False,
        "heading": "Edit Entry - " + title,
        'title': title,
        'form': NewEntryform({'title': title, 'textarea': content}),
        "form_errors": None
    })
  
  
def random_entry(request):
    list_entries = util.list_entries()
    
    markdown_converter = Markdown()
    rand_title = list_entries[random.randint(0, len(list_entries) - 1)]
    return render(request, "encyclopedia/entry.html", {
            'title': rand_title,
            'content': markdown_converter.convert(util.get_entry(rand_title))
        })
    
    
def remove(request, title):
    util.delete_entry(title)
    return HttpResponseRedirect(reverse("myapp:index"))