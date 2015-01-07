import json
import ast
from itertools import chain
import requests
from collections import Counter
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from mercurylab.forms import *
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt


REST_SERVICES_URL = 'http://localhost:8000/mercuryservices/'
#REST_SERVICES_URL = 'http://130.11.161.159/mercuryservices/'

USER_AUTH = ('admin', 'admin')
#USER_TOKEN = ''
HEADERS_CONTENT_JSON = {'content-type': 'application/json'}
HEADERS_CONTENT_FORM = {'content-type': 'application/x-www-form-urlencoded'}


SAMPLE_KEYS_UNIQUE = ["project", "site", "time_stamp", "depth", "replicate"]
SAMPLE_KEYS = ["project", "site", "time_stamp", "depth", "length", "received_time_stamp", "comment",
                 "replicate", "medium_type", "lab_processing", "sample_bottles"]
SAMPLE_BOTTLE_KEYS = ["sample", "bottle", "filter_type", "volume_filtered",
                        "preservation_type", "preservation_volume", "preservation_acid", "preservation_comment"]
SAMPLE_ANALYSIS_KEYS = ["sample_bottle", "constituent", "isotope_flag"]

def sample_login_a(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'processings/', headers=headers_auth_token)
    processings = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'mediums/', headers=headers_auth_token)
    mediums = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'filters/', headers=headers_auth_token)
    filters = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'preservations/', headers=headers_auth_token)
    preservations = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids/', headers=headers_auth_token)
    acids = json.dumps(r.json(), sort_keys=True)
    context_dict = {'processings': processings, 'mediums': mediums, 'filters': filters, 'preservations': preservations, 'acids': acids}
    return render_to_response('mercurylab/sample_login_a.html', context_dict, context)


def sample_login(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
    projects = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'processings/', headers=headers_auth_token)
    processings = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'mediums/', headers=headers_auth_token)
    mediums = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'filters/', headers=headers_auth_token)
    filters = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'preservations/', headers=headers_auth_token)
    preservations = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'isotopeflags/', headers=headers_auth_token)
    isotope_flags = json.dumps(r.json(), sort_keys=True)
    context_dict = {'projects': projects, 'processings': processings, 'mediums': mediums, 'filters': filters, 'preservations': preservations, 'isotope_flags': isotope_flags}
    return render_to_response('mercurylab/sample_login.html', context_dict, context)


#@ensure_csrf_cookie
def sample_login_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    table = json.loads(request.body.decode('utf-8'))
    unique_sample_ids = []
    unique_sample_bottles = []
    unique_sample_analyses = []
    sample_data = []
    sample_bottle_data = []
    sample_analysis_data = []

    ## PARSE ROWS AND VALIDATE ##
    # analyze each submitted row, parsing sample data and sample bottle data
    for row in table:
        print("for row in table...")
        print(row)
        # grab the data that uniquely identifies each sample
        this_sample_id = str(row.get('project'))+"|"+str(row.get('site'))+"|"+str(row.get('time_stamp'))+"|"+str(row.get('depth'))+"|"+str(row.get('replicate'))
        print("this sample id:")
        print(this_sample_id)
        # if this sample ID is not already in the unique list, add it, otherwise skip the sample data for this row
        if this_sample_id not in unique_sample_ids:
            unique_sample_ids.append(this_sample_id)

            # validate this sample doesn't exist in the database, otherwise notify the user
            sample_values_unique = [row.get('project'), row.get('site'), row.get('time_stamp'), row.get('depth'), row.get('replicate')]
            this_sample_unique = dict(zip(SAMPLE_KEYS_UNIQUE, sample_values_unique))
            # couldn't get requests.request() to work properly here, so using requests.get() instead
            #r = requests.request(method='GET', url=REST_SERVICES_URL+'samples/', data=this_sample_unique, headers=headers_auth_token)
            r = requests.get(REST_SERVICES_URL+'samples/', params=this_sample_unique)
            print(r)
            response_data = r.json()
            print("count:")
            print(response_data['count'])
            # if response count does not equal zero, then this sample already exists in the database
            if response_data['count'] != 0:
                print("count != 0")
                this_sample_unique_str = str(json.loads(this_sample_unique))
                print(this_sample_unique_str)
                message = "\"This Sample already exists in the database: " + this_sample_unique_str + "\""
                print(message)
                return HttpResponse(message, content_type='text/html')

            # if this is a new and valid sample, create a sample object using the sample data within this row
            print("test for length...")
            print(row.get('length'))
            sample_values = [row.get('project'), row.get('site'), row.get('time_stamp'), row.get('depth'), row.get('length'), row.get('received_time_stamp'), row.get('comment'), row.get('replicate'), row.get('medium_type'), row.get('lab_processing')]
            print("sample values:")
            print(sample_values)
            this_sample = dict(zip(SAMPLE_KEYS, sample_values))
            sample_data.append(this_sample)

        print("validate bottle ID")
        # validate this bottle is used in only one sample, otherwise notify the user
        this_sample_bottle = (str(row['bottle']), this_sample_id)
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
        print("validate analysis")
        this_analysis = this_sample_id+"|"+str(row.get('constituent_type'))
        print(this_analysis)
        if this_analysis not in unique_sample_analyses:
            print("unique sample analysis")
            unique_sample_analyses.append(this_analysis)
        else:
            this_analysis_str = str(json.loads(this_analysis))
            message = "\"This Analysis appears more than once in this sample: " + this_analysis_str + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')

        # create a sample bottle object using the sample bottle data within this row
        sample_bottle_values = [this_sample_id, row.get('bottle'), row.get('filter_type'), row.get('volume_filtered'), row.get('preservation_type'), row.get('preservation_volume'), row.get('preservation_acid'), row.get('preservation_comment')]
        this_sample_bottle = dict(zip(SAMPLE_BOTTLE_KEYS, sample_bottle_values))
        print(this_sample_bottle)
        # add this new sample bottle object to the list
        sample_bottle_data.append(this_sample_bottle)

        # create a result object using the result data within this row
        sample_analysis_values = [str(row.get('bottle')), row.get('constituent_type'), row.get('isotope_flag')]
        this_sample_analysis = dict(zip(SAMPLE_ANALYSIS_KEYS, sample_analysis_values))
        # add this new sample bottle object to the list
        sample_analysis_data.append(this_sample_analysis)

    ## SAVING ##
    # save samples first and then get their database IDs, which are required for saving the sample bottles afterward

    ## SAVE SAMPLES ##
    # send the samples to the database
    print("SAVE SAMPLES")
    sample_data = json.dumps(sample_data)
    print(sample_data)
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulksamples/', data=sample_data, headers=headers)
    print(r)
    response_data = r.json()
    print(len(response_data))
    # store the IDs as an array of dictionaries, where the keys are the combo IDs and the values are the database IDs
    sample_ids = []
    for item in response_data:
        # using a hacky workaround here to handle the "T" in the time_stamp; there's probably a better way to handle this
        sample_id = {'combo_id': str(item.get('project'))+"|"+str(item.get('site'))+"|"+str(item.get('time_stamp')).replace("T", " ")+"|"+str(int(item.get('depth')))+"|"+str(item.get('replicate')), 'db_id': item.get('id')}
        sample_ids.append(sample_id)

    ## SAVE SAMPLE BOTTLES ##
    # update the sample bottles with the database IDs, rather than the combo IDs
    print("SAVE SAMPLE BOTTLES")
    for sample_id in sample_ids:
        for sample_bottle in sample_bottle_data:
            if sample_bottle['sample'] == sample_id['combo_id']:
                sample_bottle['sample'] = sample_id['db_id']
    # send the sample bottles to the database
    sample_bottle_data = json.dumps(sample_bottle_data)
    print(sample_bottle_data)
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulksamplebottles/', data=sample_bottle_data, headers=headers)
    print(r)
    response_data = r.json()
    print(len(response_data))
    # store the IDs as an array of dictionaries, where the keys are the bottle IDs and the values are the sample bottle IDs
    sample_bottle_ids = []
    for item in response_data:
        sample_bottle_id = {'bottle_id': str(item['bottle']), 'db_id': item['id']}
        sample_bottle_ids.append(sample_bottle_id)

    ## SAVE SAMPLE ANALYSES (placeholder records in Results table) ##
    # update the sample analyses with the sample bottle IDs, rather than the bottle IDs
    print("SAVE RESULTS")
    for sample_bottle_id in sample_bottle_ids:
        for sample_analysis in sample_analysis_data:
            if sample_analysis['sample_bottle'] == sample_bottle_id['bottle_id']:
                sample_analysis['sample_bottle'] = sample_bottle_id['db_id']
    # send the sample analyses to the database
    sample_analysis_data = json.dumps(sample_analysis_data)
    print(sample_analysis_data)
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkresults/', data=sample_analysis_data, headers=headers)
    print(r)
    response_data = r.json()
    print(len(response_data))
    # send the response (data & messages) back to the user interface
    return HttpResponse(r, content_type='application/json')


#@ensure_csrf_cookie
def sample_search(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    context = RequestContext(request)

    if request.method == 'POST':
        params_dict = {}
        params = json.loads(request.body.decode('utf-8'))
        if params['project']:
            params_dict["project"] = str(params['project']).strip('[]').replace(', ', ',')
        if params['site']:
            params_dict["site"] = str(params['site']).strip('[]').replace(', ', ',')
        if params['depth']:
            params_dict["depth"] = str(params['depth']).strip('[]')
        if params['replicate']:
            params_dict["replicate"] = str(params['replicate']).strip('[]')
        if params['date_after']:
            params_dict["date_after"] = str(params['date_after']).strip('[]')
        if params['date_before']:
            params_dict["date_before"] = str(params['date_before']).strip('[]')

        # r = requests.request(method='GET', url=REST_SERVICES_URL+'samples/', params=d, headers=headers_auth_token, headers=HEADERS_CONTENT_JSON)
        # samples = r.json()['results']
        # bottle_ids = str(samples[0]['sample_bottles']).strip('[]').replace(', ', ',')
        # d = dict({"id": bottle_ids})
        r = requests.request(method='GET', url=REST_SERVICES_URL+'fullresults/', params=params_dict, headers=headers)
        r_dict = r.json()
        print(r_dict['count'])
        r_json = json.dumps(r_dict)
        return HttpResponse(r_json, content_type='application/json')

    else:  # request.method == 'GET'
        r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
        projects = json.dumps(r.json(), sort_keys=True)
        r = requests.request(method='GET', url=REST_SERVICES_URL+'processings/', headers=headers_auth_token)
        processings = json.dumps(r.json(), sort_keys=True)
        r = requests.request(method='GET', url=REST_SERVICES_URL+'constituents/', headers=headers_auth_token)
        constituents = json.dumps(r.json(), sort_keys=True)
        r = requests.request(method='GET', url=REST_SERVICES_URL+'mediums/', headers=headers_auth_token)
        mediums = json.dumps(r.json(), sort_keys=True)
        r = requests.request(method='GET', url=REST_SERVICES_URL+'filters/', headers=headers_auth_token)
        filters = json.dumps(r.json(), sort_keys=True)
        r = requests.request(method='GET', url=REST_SERVICES_URL+'preservations/', headers=headers_auth_token)
        preservations = json.dumps(r.json(), sort_keys=True)
        context_dict = {'projects': projects, 'processings': processings, 'constituents': constituents, 'mediums': mediums, 'filters': filters, 'preservations': preservations}

        return render_to_response('mercurylab/sample_search.html', context_dict, context)


#@ensure_csrf_cookie
def result_search(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    context = RequestContext(request)

    if request.method == 'POST':
        params_dict = {}
        params = json.loads(request.body.decode('utf-8'))
        if params['bottle']:
            params_dict["bottle"] = str(params['bottle']).strip('[]').replace(', ', ',')
        if params['project']:
            params_dict["project"] = str(params['project']).strip('[]').replace(', ', ',')
        if params['site']:
            params_dict["site"] = str(params['site']).strip('[]').replace(', ', ',')
        if params['constituent']:
            params_dict["constituent"] = str(params['constituent']).strip('[]')
        if params['date_after']:
            params_dict["date_after"] = str(params['date_after']).strip('[]')
        if params['date_before']:
            params_dict["date_before"] = str(params['date_before']).strip('[]')

        # r = requests.request(method='GET', url=REST_SERVICES_URL+'samples/', params=d, headers=headers_auth_token, headers=HEADERS_CONTENT_JSON)
        # samples = r.json()['results']
        # bottle_ids = str(samples[0]['sample_bottles']).strip('[]').replace(', ', ',')
        # d = dict({"id": bottle_ids})
        r = requests.request(method='GET', url=REST_SERVICES_URL+'fullresults/', params=params_dict, headers=headers)
        r_dict = r.json()
        print(r_dict['count'])
        r_json = json.dumps(r_dict)
        return HttpResponse(r_json, content_type='application/json')

    else:  # request.method == 'GET'
        r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
        projects = json.dumps(r.json(), sort_keys=True)
        r = requests.request(method='GET', url=REST_SERVICES_URL+'constituents/', headers=headers_auth_token)
        constituents = json.dumps(r.json(), sort_keys=True)
        context_dict = {'projects': projects, 'constituents': constituents}

        return render_to_response('mercurylab/result_search.html', context_dict, context)


def sample_bottles(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'samplebottles/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    form = SampleBottleForm()
    context_dict = {'data': data, 'form': form}
    return render_to_response('mercurylab/sample_bottles.html', context_dict, context)


def sample_bottles_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'samplebottles?name='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


#@ensure_csrf_cookie
def sample_bottles_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulksamplebottles/', data=data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


# Blank editable form to add a sample bottle
#@ensure_csrf_cookie
def sample_bottle_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    form = SampleBottleForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'samplebottles/', data=form.cleaned_data, headers=headers_auth_token)
        return sample_bottles(request)
    else:
        print(form.errors)


def bottles(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'bottles/')#, headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    bottle_form = BottleForm()
    bottle_range_form = BottleRangeForm()
    context_dict = {'data': data, 'bottle_form': bottle_form, 'bottle_range_form': bottle_range_form}
    return render_to_response('mercurylab/bottles.html', context_dict, context)


def bottles_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'bottles?name='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


#@ensure_csrf_cookie
def bottles_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkbottles/', data=data, headers=headers)
    return HttpResponse(r, content_type='application/json')


# Blank editable form to add a bottle
#@ensure_csrf_cookie
def bottle_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    form = BottleForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'bottles/', data=form.cleaned_data, headers=headers_auth_token)
        return HttpResponseRedirect('/mercurylab/bottles/')
    else:
        print(form.errors)


# Blank editable form to add a range of bottles
#@ensure_csrf_cookie
def bottle_range_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
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
        r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkbottles/', data=new_bottles, headers=headers)
        response_data = r.json()
        print(response_data)
        return HttpResponseRedirect('/mercurylab/bottles/')
    else:
        print(form.errors)


def brominations(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'brominations/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    form = BrominationForm()
    context_dict = {'data': data, 'form': form}
    return render_to_response('mercurylab/brominations.html', context_dict, context)


def brominations_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'brominations?id='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


#@ensure_csrf_cookie
def brominations_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkbrominations/', data=data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


# Blank editable form to add a bromination
#@ensure_csrf_cookie
def bromination_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    form = BrominationForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'brominations/', data=form.cleaned_data, headers=headers_auth_token)
        return brominations(request)
    else:
        print(form.errors)


def blankwaters(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'blankwaters/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    form = BlankWaterForm()
    context_dict = {'data': data, 'form': form}
    return render_to_response('mercurylab/blankwaters.html', context_dict, context)


def blankwaters_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'blankwaters?id='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


#@ensure_csrf_cookie
def blankwaters_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkblankwaters/', data=data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


# Blank editable form to add a blank water
#@ensure_csrf_cookie
def blankwater_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    form = BlankWaterForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'blankwaters/', data=form.cleaned_data, headers=headers_auth_token)
        return blankwaters(request)
    else:
        print(form.errors)


def acids(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    form = AcidForm()
    context_dict = {'data': data, 'form': form}
    return render_to_response('mercurylab/acids.html', context_dict, context)


def acids_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids?id='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


#@ensure_csrf_cookie
def acids_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkacids/', data=data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


# Blank editable form to add an acid
##@ensure_csrf_cookie
def acid_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    form = AcidForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'acids/', data=form.cleaned_data, headers=headers_auth_token)
        return acids(request)
    else:
        print(form.errors)


def sites(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'sites/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    form = SiteForm()
    context_dict = {'data': data, 'form': form}
    return render_to_response('mercurylab/sites.html', context_dict, context)


def sites_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'sites?name='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


#@ensure_csrf_cookie
def sites_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulksites/', data=data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


# Blank editable form to add a site
#@ensure_csrf_cookie
def site_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    form = SiteForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'sites/', data=form.cleaned_data, headers=headers_auth_token)
        return sites(request)
    else:
        print(form.errors)


def projects(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    form = ProjectForm()
    context_dict = {'data': data, 'form': form}
    return render_to_response('mercurylab/projects.html', context_dict, context)


def projects_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects?name='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


#@ensure_csrf_cookie
def projects_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkprojects/', data=data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


# Blank editable form to add a project
#@ensure_csrf_cookie
def project_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    form = ProjectForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'projects/', data=form.cleaned_data, headers=headers_auth_token)
        return projects(request)
    else:
        print(form.errors)


def cooperators(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    form = CooperatorForm()
    context_dict = {'data': data, 'form': form}
    return render_to_response('mercurylab/cooperators.html', context_dict, context)


def cooperators_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators?name='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


#@ensure_csrf_cookie
def cooperators_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkcooperators/', data=data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


# def cooperator(request, pk):
#     context = RequestContext(request)
#     r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/'+pk+'/', headers=headers_auth_token)
#     data = json.dumps(r.json())
#     context_dict = {'data': data, 'id': pk}
#     return render_to_response('mercurylab/cooperator.html', context_dict, context)
#
#
# #@ensure_csrf_cookie
# def cooperator_save(request, pk):
#     data = request.body
#     r = requests.request(method='PUT', url=REST_SERVICES_URL+'cooperators/'+pk+'/', data=data, headers=headers_auth_token)
#     return HttpResponse(r, content_type='application/json')


# Blank editable form to add a cooperator
#@ensure_csrf_cookie
def cooperator_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    form = CooperatorForm(request.POST)

    if form.is_valid():
        requests.request(method='POST', url=REST_SERVICES_URL+'cooperators/', data=form.cleaned_data, headers=headers_auth_token)
        return cooperators(request)
    else:
        print(form.errors)


# def register(request):
#     context = RequestContext(request)
#
#     registered = False
#
#     if request.method == 'POST':
#         user_form = UserForm(data=request.POST)
#         profile_form = UserProfileForm(data=request.POST)
#
#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save()
#
#             user.set_password(user.password)
#             user.save()
#
#             profile = profile_form.save(commit=False)
#             profile.user = user
#
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']
#
#             profile.save()
#
#             registered = True
#
#         else:
#             print(user_form.errors, profile_form.errors)
#
#     else:
#         user_form = UserForm()
#         profile_form = UserProfileForm()
#
#     return render_to_response(
#         'mercurylab/register.html',
#         {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
#         context)


#login using Session Authentication
#@ensure_csrf_cookie
# This may not be the right way to do this. We need to decouple the client from the database and log in through services instead.
# def user_login(request):
#     context = RequestContext(request)
#
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#
#         user = authenticate(username=username, password=password)
#
#         if user:
#             if user.is_active:
#                 login(request, user)
#                 global USER_AUTH
#                 USER_AUTH = (username, password)
#                 return HttpResponseRedirect('/mercurylab/')
#             else:
#                 return HttpResponse("Your account is disabled.")
#
#         else:
#             print("Invalid login details: {0}, {1}".format(username, password))
#             return HttpResponse("Invalid login details supplied.")
#
#     else:
#         return render_to_response('mercurylab/login.html', {}, context)


# #login using Basic Authentication
# #@ensure_csrf_cookie
# def user_login(request):
#     context = RequestContext(request)
#
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#
#         r = requests.request(method='POST', url=REST_SERVICES_URL+'login/', data=request.POST)
#
#         if r.status_code == 200:
#             r_dict = ast.literal_eval(r.text)
#             # user = User.objects.create_user(username, None, None)
#             # print("User:")
#             # print(user)
#             # login(request, user)
#             request.session['username'] = r_dict['username']
#             global USER_AUTH
#             USER_AUTH = (username, password)
#             return HttpResponseRedirect('/mercurylab/')
#
#         else:
#             r_dict = json.loads(r.json())
#             return HttpResponse("<h1>" + str(r.status_code) + "</h1><h3>" + r_dict['status'] + "</h3><p>" + r_dict['message'] + "</p>")
#
#     else:
#         return render_to_response('mercurylab/login.html', {}, context)


#login using Token Authentication
def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        data = {"username": username, "password": password}

        r = requests.request(method='POST', url=REST_SERVICES_URL+'auth/login', data=data, headers=HEADERS_CONTENT_FORM)

        if r.status_code == 200:
            # global USER_TOKEN
            # USER_TOKEN = eval(r.content)['auth_token']
            # global USER_AUTH
            # USER_AUTH = (username, password)
            token = eval(r.content)['auth_token']
            request.session['token'] = token
            request.session['username'] = username
            request.session['password'] = password
            return HttpResponseRedirect('/mercurylab/')

        else:
            print(r)
            print(r.status_code)
            print(r.reason)
            #print(r.text)
            print(r.request.url)
            print(r.request.headers)
            print(r.request.method)
            print(r.request.body)
            return render_to_response('mercurylab/login.html', r, context)

    else:
        return render_to_response('mercurylab/login.html', {}, context)


#logout using Session Authentication
# def user_logout(request):
#     logout(request)
#     return HttpResponseRedirect('/mercurylab/')


# #logout using Basic Authentication
# def user_logout(request):
#     r = requests.request(method='POST', url=REST_SERVICES_URL+'/logout/')
#     if r.status_code == 204:
#         del request.session['username']
#         request.session.modified = True
#         global USER_AUTH
#         USER_AUTH = ('guest', 'guest')
#         return HttpResponseRedirect('/mercurylab/')
#
#     else:
#         return HttpResponse("<h1>Logout wasn't performed. Please contact the administrator.</h1>")


#logout using Token Authentication
def user_logout(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    r = requests.request(method='POST', url=REST_SERVICES_URL+'auth/logout', headers=headers_auth_token)
    print(r)

    if r.status_code == 200:
        del request.session['token']
        del request.session['username']
        del request.session['password']
        request.session.modified = True
        # global USER_AUTH
        # USER_AUTH = ('guest', 'guest')
        # global USER_TOKEN
        # USER_TOKEN = ''
        return HttpResponseRedirect('/mercurylab/')

    else:
        return HttpResponse("<h1>Logout wasn't performed. Please contact the administrator.</h1>")

# #force logout by clearing session variables
# def user_logout(request):
#     del request.session['token']
#     del request.session['username']
#     del request.session['password']
#     request.session.modified = True
#     # global USER_AUTH
#     # USER_AUTH = ('guest', 'guest')
#     # global USER_TOKEN
#     # USER_TOKEN = ''
#     return HttpResponseRedirect('/mercurylab/')


# @login_required
# def profile(request):
#     context = RequestContext(request)
#
#     context_dict = {'username': request.user.username, 'fname': request.user.first_name, 'lname': request.user.last_name,
#                     'initials': request.user.userprofile.initials, 'phone': request.user.userprofile.phone, }
#
#     return render_to_response('mercurylab/profile.html', context_dict, context)


def about(request):
    context = RequestContext(request)
    return render_to_response('mercurylab/about.html', {}, context)


def index(request):
    context = RequestContext(request)
    context_dict = nav()
    return render_to_response('mercurylab/index.html', context_dict, context)


def nav():
    return {'navlist': ('cooperators', 'projects', 'sites', 'samples', 'bottles', 'acids', 'brominations', 'blankwaters', 'batchuploads', 'results', )}
