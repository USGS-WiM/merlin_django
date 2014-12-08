import json
import requests
from collections import Counter
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from mercurylab.forms import *
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt


REST_SERVICES_URL = 'http://localhost:8000/mercuryservices/'
#REST_SERVICES_URL = 'http://130.11.161.159/mercuryservices/'

TEMP_AUTH = ('admin', 'admin')
JSON_HEADERS = {'content-type': 'application/json'}

SAMPLE_KEYS_UNIQUE = ["project", "site", "time_stamp", "depth", "replicate"]
SAMPLE_KEYS = ["project", "site", "time_stamp", "depth", "length", "received_time_stamp", "login_comment",
                 "replicate", "medium_type", "lab_processing", "field_sample_bottles"]
SAMPLE_BOTTLE_KEYS = ["field_sample", "bottle", "constituent_type", "filter_type", "volume_filtered",
                        "preservation_type", "preservation_volume", "preservation_acid", "preservation_comment"]

def sample_login_a(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'processings/', auth=TEMP_AUTH)
    processings = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'mediums/', auth=TEMP_AUTH)
    mediums = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'filters/', auth=TEMP_AUTH)
    filters = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'preservations/', auth=TEMP_AUTH)
    preservations = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids/', auth=TEMP_AUTH)
    acids = json.dumps(r.json(), sort_keys=True)
    context_dict = {'processings': processings, 'mediums': mediums, 'filters': filters, 'preservations': preservations, 'acids': acids}
    return render_to_response('mercurylab/sample_login_a.html', context_dict, context)


def sample_login(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'processings/', auth=TEMP_AUTH)
    processings = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'mediums/', auth=TEMP_AUTH)
    mediums = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'filters/', auth=TEMP_AUTH)
    filters = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'preservations/', auth=TEMP_AUTH)
    preservations = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids/', auth=TEMP_AUTH)
    acids = json.dumps(r.json(), sort_keys=True)
    context_dict = {'processings': processings, 'mediums': mediums, 'filters': filters, 'preservations': preservations, 'acids': acids}
    return render_to_response('mercurylab/sample_login.html', context_dict, context)


@csrf_exempt
def sample_login_save(request):
    table = json.loads(request.body.decode('utf-8'))
    unique_sample_ids = []
    unique_sample_bottles = []
    unique_sample_analyses = []
    sample_data = []
    sample_bottle_data = []

    ## PARSE ROWS AND VALIDATE ##
    # analyze each submitted row, parsing sample data and sample bottle data
    for row in table:
        print(row)
        # grab the data that uniquely identifies each sample
        this_sample_id = str(row['project'])+"|"+str(row['site'])+"|"+str(row['time_stamp'])+"|"+str(row['depth'])+"|"+str(row['replicate'])
        print(this_sample_id)
        # if this sample ID is not already in the unique list, add it, otherwise skip the sample data for this row
        if this_sample_id not in unique_sample_ids:
            unique_sample_ids.append(this_sample_id)

            # validate this sample doesn't exist in the database, otherwise notify the user
            sample_values_unique = [row['project'], row['site'], row['time_stamp'], row['depth'], row['replicate']]
            this_sample_unique = dict(zip(SAMPLE_KEYS_UNIQUE, sample_values_unique))
            # couldn't get requests.request() to work properly here, so using requests.get() instead
            #r = requests.request(method='GET', url=REST_SERVICES_URL+'samples/', data=this_sample_unique, auth=TEMP_AUTH, headers=JSON_HEADERS)
            r = requests.get(REST_SERVICES_URL+'samples/', params=this_sample_unique)
            response_data = r.json()
            print(response_data['count'])
            # if response count does not equal zero, then this sample already exists in the database
            if response_data['count'] != 0:
                this_sample_unique_str = str(json.loads(this_sample_unique))
                print(this_sample_unique_str)
                message = "\"This Sample already exists in the database: " + this_sample_unique_str + "\""
                print(message)
                return HttpResponse(message, content_type='text/html')
            print("count = 0")

            # if this is a new and valid sample, create a sample object using the sample data within this row
            print(row['length'])
            sample_values = [row['project'], row['site'], row['time_stamp'], row['depth'], row['length'], row['received_time_stamp'], row['login_comment'], row['replicate'], 47, 2] #row['medium_type'], row['lab_processing']]
            print(sample_values)
            this_sample = dict(zip(SAMPLE_KEYS, sample_values))
            sample_data.append(this_sample)

        print("validate bottle ID")
        # validate this bottle is used in only one sample, otherwise notify the user
        this_sample_bottle = [str(row['bottle']), this_sample_id]
        print(this_sample_bottle)
        if this_sample_bottle not in unique_sample_bottles:
            unique_sample_bottles.append(this_sample_bottle)
        unique_sample_bottle_counter = Counter()
        for unique_sample_bottle in unique_sample_bottles:
            unique_sample_bottle_counter[unique_sample_bottle] += 1
            print(unique_sample_bottle_counter[unique_sample_bottle])
            if unique_sample_bottle_counter[unique_sample_bottle] > 1:
                unique_sample_bottle_str = str(json.loads(unique_sample_bottle[0]))
                message = "\"This Bottle appears in more than one sample: " + unique_sample_bottle_str + "\""
                print(message)
                return HttpResponse(message, content_type='text/html')

        # validate no analysis is used more than once per sample, otherwise notify the user
        this_analysis = this_sample_id+"|"+str(row['constituent_type'])
        print(this_analysis)
        if this_analysis not in unique_sample_analyses:
            unique_sample_analyses.append(this_analysis)
        else:
            this_analysis_str = str(json.loads(this_analysis))
            message = "\"This Analysis appears more than once in this sample: " + this_analysis_str + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')

        # create a sample bottle object using the sample bottle data within this row
        sample_bottle_values = [this_sample_id, row['bottle'], row['constituent_type'], row['filter_type'], row['volume_filtered'], row['preservation_type'], row['preservation_volume'], row['preservation_acid'], row['preservation_comment']]
        this_sample_bottle = dict(zip(SAMPLE_BOTTLE_KEYS, sample_bottle_values))
        # add this new sample bottle object to the list
        sample_bottle_data.append(this_sample_bottle)

    ## SAVING ##
    # save samples first and then get their database IDs, which are required for saving the sample bottles afterward

    ## SAVE SAMPLES ##
    # send the samples to the database
    sample_data = json.dumps(sample_data)
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulksamples/', data=sample_data, auth=TEMP_AUTH, headers=JSON_HEADERS)
    response_data = r.json()
    # store the IDs as an array of dictionaries, where the keys are the combo IDs and the values are the database IDs
    sample_ids = []
    for item in response_data:
        # using a hacky workaround here to handle the "T" in the time_stamp; there's probably a better way to handle this
        sample_id = {'combo_id': str(item['project'])+"|"+str(item['site'])+"|"+str(item['time_stamp']).replace("T", " ")+"|"+str(int(item['depth']))+"|"+str(item['replicate']), 'db_id': item['id']}
        sample_ids.append(sample_id)

    ## SAVE SAMPLE BOTTLES ##
    # update the sample bottles with the database IDs, rather than the combo IDs
    for sample_id in sample_ids:
        for sample_bottle in sample_bottle_data:
            if sample_bottle['field_sample'] == sample_id['combo_id']:
                sample_bottle['field_sample'] = sample_id['db_id']
    # send the sample bottles to the database
    sample_bottle_data = json.dumps(sample_bottle_data)
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulksamplebottles/', data=sample_bottle_data, auth=TEMP_AUTH, headers=JSON_HEADERS)
    # send the response (data & messages) back to the user interface
    return HttpResponse(r, content_type='application/json')


def sample_bottles(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'samplebottles/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    form = SampleBottleForm()
    context_dict = {'data': data, 'form': form}
    return render_to_response('mercurylab/sample_bottles.html', context_dict, context)


def sample_bottles_load(request):
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'samplebottles?name='+data, auth=TEMP_AUTH)
    return HttpResponse(r, content_type='application/json')


@csrf_exempt
def sample_bottles_save(request):
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulksamplebottles/', data=data, auth=TEMP_AUTH, headers=JSON_HEADERS)
    return HttpResponse(r, content_type='application/json')


# Blank editable form to add a sample bottle
@csrf_exempt
def sample_bottle_add(request):
    form = SampleBottleForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'samplebottles/', data=form.cleaned_data, auth=TEMP_AUTH)
        return sample_bottles(request)
    else:
        print(form.errors)


def bottles(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'bottles/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    bottle_form = BottleForm()
    bottle_range_form = BottleRangeForm()
    context_dict = {'data': data, 'bottle_form': bottle_form, 'bottle_range_form': bottle_range_form}
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


# Blank editable form to add a bottle
@csrf_exempt
def bottle_add(request):
    form = BottleForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'bottles/', data=form.cleaned_data, auth=TEMP_AUTH)
        return HttpResponseRedirect('/mercurylab/bottles/')
    else:
        print(form.errors)


# Blank editable form to add a range of bottles
@csrf_exempt
def bottle_range_add(request):
    form = BottleRangeForm(request.POST)

    if form.is_valid():
        params = form.cleaned_data
        digits = len(params['range_start'])
        start = int(params['range_start'])
        end = int(params['range_end'])
        new_bottles = []
        for i in range(start, end+1, 1):
            new_name = params['prefix'] + str(i).rjust(digits, '0') + params['suffix']
            new_bottle = {'bottle_unique_name': new_name, 'description': params['description'], 'tare_weight': float(params['tare_weight']), 'bottle_type': int(params['bottle_type'])}
            new_bottles.append(new_bottle)
        new_bottles = json.dumps(new_bottles)
        r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkbottles/', data=new_bottles, auth=TEMP_AUTH, headers=JSON_HEADERS)
        response_data = r.json()
        print(response_data)
        return HttpResponseRedirect('/mercurylab/bottles/')
    else:
        print(form.errors)


def brominations(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'brominations/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    form = BrominationForm()
    context_dict = {'data': data, 'form': form}
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


# Blank editable form to add a bromination
@csrf_exempt
def bromination_add(request):
    form = BrominationForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'brominations/', data=form.cleaned_data, auth=TEMP_AUTH)
        return brominations(request)
    else:
        print(form.errors)


def blankwaters(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'blankwaters/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    form = BlankWaterForm()
    context_dict = {'data': data, 'form': form}
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


# Blank editable form to add a blank water
@csrf_exempt
def blankwater_add(request):
    form = BlankWaterForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'blankwaters/', data=form.cleaned_data, auth=TEMP_AUTH)
        return blankwaters(request)
    else:
        print(form.errors)


def acids(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    form = AcidForm()
    context_dict = {'data': data, 'form': form}
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


# Blank editable form to add an acid
@csrf_exempt
def acid_add(request):
    form = AcidForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'acids/', data=form.cleaned_data, auth=TEMP_AUTH)
        return acids(request)
    else:
        print(form.errors)


def sites(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'sites/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    form = SiteForm()
    context_dict = {'data': data, 'form': form}
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


# Blank editable form to add a site
@csrf_exempt
def site_add(request):

    form = SiteForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'sites/', data=form.cleaned_data, auth=TEMP_AUTH)
        return sites(request)
    else:
        print(form.errors)


def projects(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    form = ProjectForm()
    context_dict = {'data': data, 'form': form}
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


# Blank editable form to add a project
@csrf_exempt
def project_add(request):

    form = ProjectForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'projects/', data=form.cleaned_data, auth=TEMP_AUTH)
        return projects(request)
    else:
        print(form.errors)


def cooperators(request):
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', auth=TEMP_AUTH)
    data = json.dumps(r.json(), sort_keys=True)
    form = CooperatorForm()
    context_dict = {'data': data, 'form': form}
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


# Blank editable form to add a cooperator
@csrf_exempt
def cooperator_add(request):

    form = CooperatorForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'cooperators/', data=form.cleaned_data, auth=TEMP_AUTH)
        return cooperators(request)
    else:
        print(form.errors)


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


@csrf_exempt
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

    context_dict = {'username': request.user.username, 'fname': request.user.first_name, 'lname': request.user.last_name,
                    'initials': request.user.userprofile.initials, 'phone': request.user.userprofile.phone, }

    return render_to_response('mercurylab/profile.html', context_dict, context)


def about(request):
    context = RequestContext(request)
    return render_to_response('mercurylab/about.html', {}, context)


def index(request):
    context = RequestContext(request)
    context_dict = nav()
    return render_to_response('mercurylab/index.html', context_dict, context)


def nav():
    return {'navlist': ('cooperators', 'projects', 'sites', 'samples', 'bottles', 'acids', 'brominations', 'blankwaters', 'batchuploads', 'results', )}
