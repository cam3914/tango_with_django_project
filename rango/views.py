# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page

def index(request):
    #Query db
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    # Construct a dictionary to pass to the template engine as its context
    context_dict = {'categories': category_list,
                    'pages': page_list }
    # Return  a rendered response to send to the client
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    # Construct a dictionary to pass to the template engine as its context
    context_dict = {'excerciseline': "This tutorial has been put together by Cameron McCosh."}
    # Return  a rendered response to send to the client
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    # Create context dictionary
    context_dict = {}

    try:
        # Exists?
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all associated pages
        pages = Page.objects.filter(category=category)

        # Add results list to template context
        context_dict['pages'] = pages
        
        #Add category object from db to context dict
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context_dict)
        
