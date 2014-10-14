from datetime import datetime
from simplejson import dumps
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import *
from django.template import RequestContext
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from mercurylab.forms import UserForm, UserProfileForm, CooperatorForm
from django.forms.formsets import formset_factory
import requests


REST_SERVICES_URL = 'http://localhost:8000/mercuryservices/'


def cooperators_grid(request):
    if request.method == 'POST':
        r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', auth=('admin', 'admin'))
        data = r.json()

    else:
        r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', auth=('admin', 'admin'))
        data = r.json()
        #return HttpResponse("Here is the cooperator:<br />data:<br />" + data)

    return render_to_response('mercurylab/cooperators_grid.html', {'data': data})


def cooperators_manage(request):
    CooperatorFormSet = formset_factory(CooperatorForm)
    if request.method == 'POST':
        r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', auth=('admin', 'admin'))
        data = r.json()
        formset = CooperatorFormSet(initial=data)
        if formset.is_valid():
            # do something with the formset.cleaned_data
            pass
    else:
        r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', auth=('admin', 'admin'))
        data = r.json()
        #return HttpResponse("Here is the cooperator:<br />data:<br />" + data)
        formset = CooperatorFormSet(initial=data)

    return render_to_response('mercurylab/cooperators_manage.html', {'formset': formset})


# Plain HTML list of cooperators
def cooperators_list(request):
    #return HttpResponse("Hello World!")
    context = RequestContext(request)

    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', auth=('admin', 'admin'))
    data = r.json()
    #print(data)
    #return HttpResponse("Here are the cooperators:<br />data:<br />" + data)

    context_dict = {'list': data}

    return render_to_response('mercurylab/cooperators_list.html', context_dict, context)


# Plain HTML list of a cooperator's fields
def cooperator_detail(request, pk):
    #return HttpResponse("Hello World!")
    context = RequestContext(request)

    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/'+pk, auth=('admin', 'admin'))
    data = r.json()
    #return HttpResponse("Here is the cooperator:<br />data:<br />" + data)

    form = CooperatorForm(initial=data)
    context_dict = {'form': form, 'list': data}

    return render_to_response('mercurylab/cooperator_detail.html', context_dict, context)


# Populated editable form to edit details of a cooperator
class CooperatorEdit(FormView):
    template_name = 'mercurylab/cooperator_edit.html'
    form_class = CooperatorForm

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        auth = ('admin', 'admin')
        url = REST_SERVICES_URL+'cooperators/'+pk+'/'
        r = requests.request(method='GET', url=url, auth=auth)
        data = r.json()
        form = self.form_class(initial=data)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            pk = self.kwargs['pk']
            data = form.cleaned_data
            auth = ('admin', 'admin')
            url = REST_SERVICES_URL+'cooperators/'+pk+'/'
            r = requests.request(method='PUT', url=url, data=data, auth=auth)
            rid = str(r.json()['id'])
            return HttpResponseRedirect('/mercurylab/cooperators/'+rid+'/')

        return render(request, self.template_name, {'form': form})


# def cooperator_edit(request, pk):
#     #return HttpResponse("Hello World!")
#     context = RequestContext(request)
#     context_dict = {}
#
#     if request.method == 'POST':
#         form = CooperatorForm(request.POST)
#
#         if form.is_valid():
#             data = form.cleaned_data
#             auth = ('admin', 'admin')
#             r = requests.request(method='PUT', url=REST_SERVICES_URL+'cooperators/'+pk+'/', data=data, auth=auth)
#             data = r.json()
#             return cooperator_detail(request, str(data['id']))
#         else:
#             print(form.errors)
#
#     else:
#         r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/'+pk, auth=('admin', 'admin'))
#         data = r.json()
#         #return HttpResponse("Here is the cooperator:<br />data:<br />" + data)
#
#         form = CooperatorForm(initial=data)
#         context_dict = {'form': form, 'list': data}
#
#     return render_to_response('mercurylab/cooperator_edit.html', context_dict, context)


# Blank editable form to add a cooperator
def cooperator_add(request):
    context = RequestContext(request)
    context_dict = {}

    if request.method == 'POST':
        form = CooperatorForm(request.POST)

        if form.is_valid():
            r = requests.request(method='POST', url=REST_SERVICES_URL+'cooperators/', data=form.cleaned_data, auth=('admin', 'admin'))
            data = r.json()
            return cooperator_detail(request, str(data['id']))
        else:
            print(form.errors)

    else:
        form = CooperatorForm()
        context_dict = {'form': form}

    return render_to_response('mercurylab/cooperator_add.html', context_dict, context)


# Simple button to delete a cooperator
def cooperator_delete(request, pk):
    context = RequestContext(request)

    if request.method == 'GET':
        r = requests.request(method='DELETE', url=REST_SERVICES_URL+'cooperators/'+pk+'/', auth=('admin', 'admin'))

        if r.status_code == 204:
            return cooperators_list(request)

        else:
            message = 'There was an error deleting this cooperator (id='+pk+').\r\n' \
                'It is likely this cooperator no longer exists and thus could not be deleted again.\r\n' \
                'Please contact your administrator.'
            context_dict = {'error_code': str(r.status_code), 'error_message': message}
            return render_to_response('mercurylab/error.html', context_dict, context)



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
