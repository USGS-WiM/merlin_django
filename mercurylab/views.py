from datetime import datetime
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import *
from django.template import RequestContext
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from mercurylab.forms import UserForm, UserProfileForm, CooperatorForm, AcidForm
from django.forms.formsets import formset_factory
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import requests


REST_SERVICES_URL = 'http://localhost:8000/mercuryservices/'
#REST_SERVICES_URL = 'http://130.11.161.159/mercuryservices/'

TEMP_AUTH = ('admin', 'admin')
JSON_HEADERS = {'content-type': 'application/json'}


def samples(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'mediums/', auth=TEMP_AUTH)
    mediums = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'filters/', auth=TEMP_AUTH)
    filters = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'preservations/', auth=TEMP_AUTH)
    preservations = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids/', auth=TEMP_AUTH)
    acids = json.dumps(r.json(), sort_keys=True)
    context_dict = {'mediums': mediums, 'filters': filters, 'preservations': preservations, 'acids': acids}
    return render_to_response('mercurylab/samples.html', context_dict, context)


def bottles(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'bottles/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/bottles.html', context_dict, context)


def bottles_load(request):
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'bottles?name='+data, auth=TEMP_AUTH)
    return HttpResponse(r, content_type='application/json')


@csrf_exempt
def bottles_save(request):
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkbottles/', data=data, auth=TEMP_AUTH, headers=JSON_HEADERS)
    return HttpResponse(r, content_type='application/json')


def brominations(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'brominations/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/brominations.html', context_dict, context)


def brominations_load(request):
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'brominations?id='+data, auth=TEMP_AUTH)
    return HttpResponse(r, content_type='application/json')


@csrf_exempt
def brominations_save(request):
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkbrominations/', data=data, auth=TEMP_AUTH, headers=JSON_HEADERS)
    return HttpResponse(r, content_type='application/json')


def blankwaters(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'blankwaters/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/blankwaters.html', context_dict, context)


def blankwaters_load(request):
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'blankwaters?id='+data, auth=TEMP_AUTH)
    return HttpResponse(r, content_type='application/json')


@csrf_exempt
def blankwaters_save(request):
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkblankwaters/', data=data, auth=TEMP_AUTH, headers=JSON_HEADERS)
    return HttpResponse(r, content_type='application/json')


def acids(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/acids.html', context_dict, context)


def acids_load(request):
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids?id='+data, auth=TEMP_AUTH)
    return HttpResponse(r, content_type='application/json')


@csrf_exempt
def acids_save(request):
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkacids/', data=data, auth=TEMP_AUTH, headers=JSON_HEADERS)
    return HttpResponse(r, content_type='application/json')


def sites(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'sites/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/sites.html', context_dict, context)


def sites_load(request):
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'sites?name='+data, auth=TEMP_AUTH)
    return HttpResponse(r, content_type='application/json')


@csrf_exempt
def sites_save(request):
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulksites/', data=data, auth=TEMP_AUTH, headers=JSON_HEADERS)
    return HttpResponse(r, content_type='application/json')


def projects(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/projects.html', context_dict, context)


def projects_load(request):
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects?name='+data, auth=TEMP_AUTH)
    return HttpResponse(r, content_type='application/json')


@csrf_exempt
def projects_save(request):
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkprojects/', data=data, auth=TEMP_AUTH, headers=JSON_HEADERS)
    return HttpResponse(r, content_type='application/json')


def cooperators(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/cooperators.html', context_dict, context)


def cooperators_load(request):
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators?name='+data, auth=TEMP_AUTH)
    return HttpResponse(r, content_type='application/json')


@csrf_exempt
def cooperators_save(request):
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkcooperators/', data=data, auth=TEMP_AUTH, headers=JSON_HEADERS)
    return HttpResponse(r, content_type='application/json')


def cooperator(request, pk):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/'+pk+'/', auth=TEMP_AUTH)
    data = json.dumps(r.json())
    context_dict = {'data': data, 'id': pk}
    return render_to_response('mercurylab/cooperator.html', context_dict, context)


@csrf_exempt
def cooperator_save(request, pk):
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'cooperators/'+pk+'/', data=data, auth=TEMP_AUTH, headers=JSON_HEADERS)
    return HttpResponse(r, content_type='application/json')


def cooperators_formset(request):
    context = RequestContext(request)
    CooperatorFormSet = formset_factory(CooperatorForm)
    if request.method == 'POST':
        r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', auth=TEMP_AUTH)
        data = r.json()
        formset = CooperatorFormSet(initial=data)
        if formset.is_valid():
            # do something with the formset.cleaned_data
            pass
    else:
        r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', auth=TEMP_AUTH)
        data = r.json()
        #return HttpResponse("Here is the cooperator:<br />data:<br />" + data)
        formset = CooperatorFormSet(initial=data)

    return render_to_response('mercurylab/cooperators_formset.html', {'formset': formset}, context)


# Plain HTML list of cooperators
def cooperators_list(request):
    #return HttpResponse("Hello World!")
    context = RequestContext(request)

    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', auth=TEMP_AUTH)
    data = r.json()
    #return HttpResponse("Here are the cooperators:<br />data:<br />" + data)

    context_dict = {'list': data}

    return render_to_response('mercurylab/cooperators_list.html', context_dict, context)


def cooperator_detail_formset(request, pk):
    context = RequestContext(request)
    CooperatorFormSet = formset_factory(CooperatorForm)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/'+pk, auth=TEMP_AUTH)
    data = r.json()
    formset = CooperatorFormSet(initial=data)

    return render_to_response('mercurylab/cooperators_formset.html', {'formset': formset}, context)


# Plain HTML list of a cooperator's fields
def cooperator_detail(request, pk):
    #return HttpResponse("Hello World!")
    context = RequestContext(request)

    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/'+pk, auth=TEMP_AUTH)
    data = r.json()
    #return HttpResponse("Here is the cooperator:<br />data:<br />" + data)

    form = CooperatorForm(initial=data)
    context_dict = {'form': form, 'list': data}
    #return HttpResponse(r, content_type='application/json')

    return render_to_response('mercurylab/cooperator_detail.html', context_dict, context)


# Populated editable form to edit details of a cooperator
class CooperatorEdit(FormView):
    template_name = 'mercurylab/cooperator_edit.html'
    form_class = CooperatorForm

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        url = REST_SERVICES_URL+'cooperators/'+pk+'/'
        r = requests.request(method='GET', url=url, auth=TEMP_AUTH)
        data = r.json()
        form = self.form_class(initial=data)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            pk = self.kwargs['pk']
            data = form.cleaned_data
            url = REST_SERVICES_URL+'cooperators/'+pk+'/'
            r = requests.request(method='PUT', url=url, data=data, auth=TEMP_AUTH)
            rid = str(r.json()['id'])
            return HttpResponseRedirect('/mercurylab/cooperators_list/'+rid+'/')

        return render(request, self.template_name, {'form': form})


# def cooperator_edit(request, pk):
#     context = RequestContext(request)
#     context_dict = {}
#
#     if request.method == 'POST':
#         form = CooperatorForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data
#             auth = ('admin', 'admin')
#             r = requests.request(method='PUT', url=REST_SERVICES_URL+'cooperators/'+pk+'/', data=data, auth=TEMP_AUTH)
#             data = r.json()
#             return cooperator_detail(request, str(data['id']))
#         else:
#             print(form.errors)
#
#     else:
#         r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/'+pk, auth=TEMP_AUTH)
#         data = r.json()
#         form = CooperatorForm(initial=data)
#         context_dict = {'form': form, 'list': data}
#
#     return render_to_response('mercurylab/cooperator_edit.html', context_dict, context)


def cooperator_add_formset(request):
    context = RequestContext(request)
    CooperatorFormSet = formset_factory(CooperatorForm)
    if request.method == 'POST':
        formset = CooperatorFormSet(request.POST, request.FILES)
        if formset.is_valid():
            print(formset.cleaned_data)
            r = requests.request(method='POST', url=REST_SERVICES_URL+'cooperators/', data=formset.cleaned_data[0], auth=TEMP_AUTH)
            data = r.json()
            return cooperator_detail(request, str(data['id']))
        else:
            print(formset.errors)
    else:
        formset = CooperatorFormSet()

    return render_to_response('mercurylab/cooperators_formset.html', {'formset': formset}, context)


# Blank editable form to add a cooperator
def cooperator_add(request):
    context = RequestContext(request)
    context_dict = {}

    if request.method == 'POST':
        form = CooperatorForm(request.POST)

        if form.is_valid():
            r = requests.request(method='POST', url=REST_SERVICES_URL+'cooperators/', data=form.cleaned_data, auth=TEMP_AUTH)
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
        r = requests.request(method='DELETE', url=REST_SERVICES_URL+'cooperators/'+pk+'/', auth=TEMP_AUTH)

        if r.status_code == 204:
            return cooperators(request)

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
