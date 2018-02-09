# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime

# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val
    
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1' ))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time= datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] =  last_visit_cookie

    request.session['visits'] =  visits
    
def index(request):
    request.session.set_test_cookie()
    #Query db
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    # Construct a dictionary to pass to the template engine as its context
    context_dict = {'categories': category_list,
                    'pages': page_list }
    
    # Call cookie helper function
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    context_dict['last_visit'] = request.session['last_visit']

    # Create response object    
    response = render(request, 'rango/index.html', context_dict)

    return response
    

def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

    # Construct a dictionary to pass to the template engine as its context
    context_dict = {'excerciseline': "This tutorial has been put together by Cameron McCosh."}
    
    # Call cookie helper function
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    # Create response object    
    response = render(request, 'rango/about.html', context_dict)

    return response

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

@login_required
def add_category(request):
    form =CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Form valid?
        if form.is_valid():
            form.save(commit=True)
            return index(request)

        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)

        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    registered = False

    # If POST, process data
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            # Now sort out user profile
            profile = profile_form.save(commit=False)
            profile.user = user

            # Profile picture provided?
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Save UserProfile
            profile.save()

            # Update success variable
            registered = True

        else:
            #Invalid form etc
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()


    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})
    
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your Rango account is disabled.")

        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'rango/login.html', {})
        
@login_required
def restricted(request):
        return render(request, 'rango/restricted.html', {} )

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
    
    
