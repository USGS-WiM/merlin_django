from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from mercurylab.forms import UserForm, UserProfileForm, CooperatorForm
import requests

REST_SERVICES_URL = 'http://localhost:8000/mercuryservices/'

def cooperators_list(request):
    #return HttpResponse("Hello World!")

    r = requests.get(REST_SERVICES_URL+'cooperators/', auth=('admin','admin'))
    data = r.json()
    #print(data)
    #return HttpResponse("Here are the cooperators:<br />data:<br />" + data)

    context = RequestContext(request)
    form = CooperatorForm()
    context_dict = {'list': data, 'form': form}

    return render_to_response('mercurylab/cooperators_list.html', context_dict, context)


def cooperators_detail(request, pk):
    #return HttpResponse("Hello World!")

    r = requests.get(REST_SERVICES_URL+'cooperators/'+pk, auth=('admin','admin'))
    data = r.json()
    print(data)
    #return HttpResponse("Here is the cooperator:<br />data:<br />" + data)

    context = RequestContext(request)
    context_dict = {'list': data}

    return render_to_response('mercurylab/cooperators_detail.html', context_dict, context)


def cooperator_add(request):
    context = RequestContext(request)

    if request.method == 'POST':
        form = CooperatorForm(request.POST)

        if form.is_valid():
            #form.save(commit=True)
            #print(form.data)
            #print(form.cleaned_data)
            #test = {'name': 'That Guy', 'agency': 'Overthere'}
            r = requests.post(REST_SERVICES_URL+'cooperators/', data=form.cleaned_data, auth=('admin','admin'))
            data = r.json()
            print(data)
            return index(request)
        else:
            print(form.errors)

    else:
        form = CooperatorForm()

    return render_to_response('mercurylab/cooperator_add.html', {'form': form}, context)


def register(request):
    context = RequestContext(request)

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
        'mercurylab/register.html',
        {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
        context)


def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/mercurylab/')
            else:
                return HttpResponse("Your account is disabled.")

        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    else:
        return render_to_response('mercurylab/login.html', {}, context)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/mercurylab/')


@login_required
def profile(request):
    context = RequestContext(request)

    context_dict = {'username': request.user.username,
                    'initials': request.user.userprofile.initials,
                    'phone': request.user.userprofile.phone, }

    return render_to_response('mercurylab/profile.html', context_dict, context)


@login_required
def restricted(request):
    #return HttpResponse("Since you're logged in, you can see this text!")
    context = RequestContext(request)
    return render_to_response('mercurylab/restricted.html', {}, context)


def about(request):
    context = RequestContext(request)
    return render_to_response('mercurylab/about.html', {}, context)


def index(request):
    context = RequestContext(request)
    context_dict = nav()
    return render_to_response('mercurylab/index.html', context_dict, context)


def nav():
    return {'navlist': ('cooperators_test', 'cooperators', 'projects', 'sites', 'samples', 'bottles', 'acids', 'brominations', 'blankwaters', 'batchuploads', 'results', )}
