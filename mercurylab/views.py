import json
import requests
from datetime import datetime
from itertools import chain
from collections import Counter
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response


REST_SERVICES_URL = 'http://localhost:8000/mercuryservices/'
REST_AUTH_URL = 'http://localhost:8000/mercuryauth/'
#REST_SERVICES_URL = 'http://130.11.161.159/mercuryservices/'
#REST_AUTH_URL = 'http://130.11.161.159/mercuryauth/'

USER_AUTH = ('admin', 'admin')
#USER_TOKEN = ''
HEADERS_CONTENT_JSON = {'content-type': 'application/json'}
HEADERS_CONTENT_FORM = {'content-type': 'application/x-www-form-urlencoded'}


SAMPLE_KEYS_UNIQUE = ["project", "site", "sample_date_time", "depth", "replicate"]
SAMPLE_KEYS = ["project", "site", "sample_date_time", "depth", "length", "received_date", "comment",
                 "replicate", "medium_type", "lab_processing"]
SAMPLE_BOTTLE_KEYS = ["sample", "bottle", "filter_type", "volume_filtered",
                        "preservation_type", "preservation_volume", "preservation_acid", "preservation_comment"]
SAMPLE_ANALYSIS_KEYS = ["sample_bottle", "constituent", "isotope_flag"]
BOTTLE_KEYS = ["bottle_unique_name", "created_date", "tare_weight", "bottle_type", "description"]

def sample_login(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/mercurylab/')
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


def sample_login_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    table = json.loads(request.body.decode('utf-8'))
    row_number = 0
    unique_sample_ids = []
    unique_bottles = []
    non_unique_bottles = []
    suspect_sample_bottles = []
    unique_sample_analyses = []
    sample_data = []
    sample_bottle_data = []
    sample_analysis_data = []

    ## PARSE ROWS AND VALIDATE ##
    # analyze each submitted row, parsing sample data and sample bottle data
    for row in table:
        row_number += 1
        row_message = "for row " + str(row_number) + " in table..."
        print(row_message)
        print(row)
        # grab the data that uniquely identifies each sample
        this_sample_id = str(row.get('project'))+"|"+str(row.get('site'))+"|"+str(row.get('sample_date_time'))+"|"+str(row.get('depth'))+"|"+str(row.get('replicate'))
        print("this sample id:")
        print(this_sample_id)
        # if this sample ID is not already in the unique list, add it, otherwise skip the sample data for this row
        if this_sample_id not in unique_sample_ids:
            unique_sample_ids.append(this_sample_id)

            # validate this sample doesn't exist in the database, otherwise notify the user
            sample_values_unique = [row.get('project'), row.get('site'), row.get('sample_date_time'), row.get('depth'), row.get('replicate')]
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
                this_sample_unique_str = str(this_sample_unique)
                print(this_sample_unique_str)
                r = requests.get(REST_SERVICES_URL+'projects/', params={'id': row.get('project')})
                project_name = r.json()[0]['name']
                r = requests.get(REST_SERVICES_URL+'sites/', params={'id': row.get('site')})
                site_name = r.json()['results'][0]['name']
                message = "\"Error in row " + str(row_number) + ": This Sample already exists in the database: " + project_name + "|" + site_name + "|" + str(row.get('sample_date_time')) + "|" + str(row.get('depth')) + "|" + str(row.get('replicate')) + "\""
                print(message)
                return HttpResponse(message, content_type='text/html')

            # if this is a new and valid sample, create a sample object using the sample data within this row
            print("test for length...")
            print(row.get('length'))
            sample_values = [row.get('project'), row.get('site'), row.get('sample_date_time'), row.get('depth'), row.get('length'), row.get('received_date'), row.get('comment'), row.get('replicate'), row.get('medium_type'), row.get('lab_processing')]
            print("sample values:")
            print(sample_values)
            this_sample = dict(zip(SAMPLE_KEYS, sample_values))
            sample_data.append(this_sample)

        print("validate bottle ID part 1")
        # validate this bottle is used only once, otherwise hold onto its details for further validation
        this_bottle = row.get('bottle')
        if this_bottle not in unique_bottles:
            unique_bottles.append(this_bottle)
        else:  # not unique, so compare sample IDs
            non_unique_bottles.append(this_bottle)
            this_sample_bottle = (this_bottle, this_sample_id)
            suspect_sample_bottles.append(this_sample_bottle)

        # validate no analysis is used more than once per sample, otherwise notify the user
        print("validate analysis")
        this_analysis = this_sample_id+"|"+str(row.get('constituent_type'))
        print(this_analysis)
        if this_analysis not in unique_sample_analyses:
            print("unique sample analysis")
            unique_sample_analyses.append(this_analysis)
        else:
            this_analysis_str = str(this_analysis)
            r = requests.get(REST_SERVICES_URL+'projects/', params={'id': row.get('project')})
            project_name = r.json()[0]['name']
            r = requests.get(REST_SERVICES_URL+'sites/', params={'id': row.get('site')})
            site_name = r.json()['results'][0]['name']
            r = requests.get(REST_SERVICES_URL+'constituents/', params={'id': row.get('constituent_type')})
            constituent_name = r.json()[0]['constituent']
            message = "\"Error in row " + str(row_number) + ": This Analysis (" + constituent_name + ") appears more than once in this sample: " + project_name + "|" + site_name + "|" + str(row.get('sample_date_time')) + "|" + str(row.get('depth')) + "|" + str(row.get('replicate')) + "\""
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

    print("validate bottle ID part 2")
    # validate this bottle is used in only one sample, otherwise notify the user (it can be used more than once within a sample, though)
    suspect_sample_bottle_counter = Counter()
    for suspect_sample_bottle in suspect_sample_bottles:
        print(suspect_sample_bottle)
        suspect_sample_bottle_counter[suspect_sample_bottle] += 1
    for suspect_sample_bottle in suspect_sample_bottles:
        # if there is only one, then the combination of bottle ID and sample ID is unique, meaning this bottle is used in more than one sample
        if suspect_sample_bottle_counter[suspect_sample_bottle] == 1:
            print("==1")
            params = {"id": suspect_sample_bottle[0]}
            r = requests.get(REST_SERVICES_URL+'bottles/', params=params)
            print(r)
            response_data = r.json()
            print(response_data)
            bottle_unique_name = response_data['results'][0]['bottle_unique_name']
            print(bottle_unique_name)
            message = "\"Error in row " + str(row_number) + ": This Container appears in more than one sample: " + bottle_unique_name + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')
        else:
            print(">1")

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
        sample_id = {'combo_id': str(item.get('project'))+"|"+str(item.get('site'))+"|"+str(item.get('sample_date_time')).replace("T", " ")+"|"+str(int(item.get('depth')))+"|"+str(item.get('replicate')), 'db_id': item.get('id')}
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


def sample_search(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/mercurylab/')
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
        if params['depth']:
            params_dict["depth"] = str(params['depth']).strip('[]')
        if params['replicate']:
            params_dict["replicate"] = str(params['replicate']).strip('[]')
        if params['date_after']:
            params_dict["date_after"] = datetime.strptime(str(params['date_after']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before']:
            params_dict["date_before"] = datetime.strptime(str(params['date_before']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        #print(params_dict)

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
        r = requests.request(method='GET', url=REST_SERVICES_URL+'isotopeflags/', headers=headers_auth_token)
        isotope_flags = json.dumps(r.json(), sort_keys=True)
        context_dict = {'projects': projects, 'processings': processings, 'constituents': constituents, 'mediums': mediums, 'filters': filters, 'preservations': preservations, 'isotope_flags': isotope_flags}

        return render_to_response('mercurylab/sample_search.html', context_dict, context)


def sample_search_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    table = json.loads(request.body.decode('utf-8'))
    row_number = 0
    unique_sample_ids = []
    sample_data = []
    sample_bottle_data = []
    sample_analysis_data = []

    ## PARSE ROWS AND VALIDATE ##
    # analyze each submitted row, parsing sample data and sample bottle data
    for row in table:
        row_number += 1
        row_message = "for row " + str(row_number) + " in table..."
        print(row_message)
        print(row)
        # grab the data that uniquely identifies each sample
        this_sample_id = row.get('sample_bottle.sample.id')
        print("this sample id:")
        print(this_sample_id)
        # if this sample ID is not already in the unique list, add it, otherwise skip the sample data for this row
        if this_sample_id not in unique_sample_ids:
            unique_sample_ids.append(this_sample_id)

            # validate this sample already exists in the database, otherwise notify the user
            sample_values_unique = [row.get('project'), row.get('site'), row.get('sample_date_time'), row.get('depth'), row.get('replicate')]
            this_sample_unique = dict(zip(SAMPLE_KEYS_UNIQUE, sample_values_unique))
            # couldn't get requests.request() to work properly here, so using requests.get() instead
            #r = requests.request(method='GET', url=REST_SERVICES_URL+'samples/', data=this_sample_unique, headers=headers_auth_token)
            r = requests.get(REST_SERVICES_URL+'samples/', params=this_sample_unique)
            print(r)
            response_data = r.json()
            print("count:")
            print(response_data['count'])
            # if response count equals zero, then this sample already does not exist in the database
            if response_data['count'] == 0:
                print("count == 0")
                this_sample_unique_str = str(this_sample_unique)
                print(this_sample_unique_str)
                r = requests.get(REST_SERVICES_URL+'projects/', params={'id': row.get('project')})
                project_name = r.json()[0]['name']
                r = requests.get(REST_SERVICES_URL+'sites/', params={'id': row.get('site')})
                site_name = r.json()['results'][0]['name']
                message = "\"Error in row " + str(row_number) + ": This Sample does not exist in the database: " + project_name + "|" + site_name + "|" + str(row.get('sample_date_time')) + "|" + str(row.get('depth')) + "|" + str(row.get('replicate')) + ". Please use the Sample Login tool to add it.\""
                print(message)
                return HttpResponse(message, content_type='text/html')

            # if this is an existing and valid sample, create a sample object using the sample data within this row
            sample_values = [row.get('sample_bottle.sample.id'), row.get('project'), row.get('site'), row.get('sample_date_time'), row.get('depth'), row.get('length'), row.get('received_date'), row.get('comment'), row.get('replicate'), row.get('medium_type'), row.get('lab_processing')]
            print("sample values:")
            print(sample_values)
            this_sample_keys = ["id", "project", "site", "sample_date_time", "depth", "length", "received_date", "comment", "replicate", "medium_type", "lab_processing"]
            this_sample = dict(zip(this_sample_keys, sample_values))
            print(this_sample)
            sample_data.append(this_sample)

        # create a sample bottle object using the sample bottle data within this row
        sample_bottle_values = [row.get('sample_bottle.id'), row.get('sample_bottle.sample.id'), row.get('bottle'), row.get('filter_type'), row.get('volume_filtered'), row.get('preservation_type'), row.get('preservation_volume'), row.get('preservation_acid'), row.get('preservation_comment')]
        this_sample_bottle_keys = ["id", "sample", "bottle", "filter_type", "volume_filtered", "preservation_type", "preservation_volume", "preservation_acid", "preservation_comment"]
        this_sample_bottle = dict(zip(this_sample_bottle_keys, sample_bottle_values))
        print(this_sample_bottle)
        # add this new sample bottle object to the list
        sample_bottle_data.append(this_sample_bottle)

        # create a result object using the result data within this row
        sample_analysis_values = [row.get('id'), row.get('sample_bottle.id'), row.get('constituent_type'), row.get('isotope_flag')]
        this_sample_analysis_keys = ["id", "sample_bottle", "constituent", "isotope_flag"]
        this_sample_analysis = dict(zip(this_sample_analysis_keys, sample_analysis_values))
        # add this new sample bottle object to the list
        sample_analysis_data.append(this_sample_analysis)

    ## SAVING ##
    # save samples first and then get their database IDs, which are required for saving the sample bottles afterward

    ## SAVE SAMPLES ##
    # send the samples to the database
    print("SAVE SAMPLES")
    #sample_data = json.dumps(sample_data)
    print(sample_data)
    sample_response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    item_number = 0
    for item in sample_data:
        item_number += 1
        item = json.dumps(item)
        r = requests.request(method='PUT', url=REST_SERVICES_URL+'samples/', data=item, headers=headers)
        print(r)
        if r.status_code != 200 or r.status_code != 201:
            print("ERROR")
            message = "\"Error in row " + str(item_number) + ": Encountered an error while attempting to save sample " + item["id"] + ": " + r.status_code + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')
        else:
            this_response_data = r.json()
            sample_response_data.append(this_response_data)
    # store the IDs as an array of dictionaries, where the keys are the combo IDs and the values are the database IDs
    sample_ids = []
    for item in sample_response_data:
        # using a hacky workaround here to handle the "T" in the time_stamp; there's probably a better way to handle this
        sample_id = {'combo_id': str(item.get('project'))+"|"+str(item.get('site'))+"|"+str(item.get('sample_date_time')).replace("T", " ")+"|"+str(int(item.get('depth')))+"|"+str(item.get('replicate')), 'db_id': item.get('id')}
        sample_ids.append(sample_id)

    ## SAVE SAMPLE BOTTLES ##
    # update the sample bottles with the database IDs, rather than the combo IDs
    print("SAVE SAMPLE BOTTLES")
    for sample_id in sample_ids:
        for sample_bottle in sample_bottle_data:
            if sample_bottle['sample'] == sample_id['combo_id']:
                sample_bottle['sample'] = sample_id['db_id']
    # send the sample bottles to the database
    #sample_bottle_data = json.dumps(sample_bottle_data)
    print(sample_bottle_data)
    sample_bottle_response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    item_number = 0
    for item in sample_bottle_data:
        item_number += 1
        item = json.dumps(item)
        r = requests.request(method='PUT', url=REST_SERVICES_URL+'samplebottles/', data=item, headers=headers)
        print(r)
        if r.status_code != 200 or r.status_code != 201:
            print("ERROR")
            message = "\"Error in row " + str(item_number) + ": Encountered an error while attempting to save sample bottle in sample " + item["id"] + ": " + r.status_code + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')
        else:
            this_response_data = r.json()
            sample_bottle_response_data.append(this_response_data)
    # store the IDs as an array of dictionaries, where the keys are the bottle IDs and the values are the sample bottle IDs
    sample_bottle_ids = []
    for item in sample_bottle_response_data:
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
    #sample_analysis_data = json.dumps(sample_analysis_data)
    print(sample_analysis_data)
    sample_analysis_response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    item_number = 0
    for item in sample_analysis_data:
        item_number += 1
        item = json.dumps(item)
        r = requests.request(method='PUT', url=REST_SERVICES_URL+'results/', data=item, headers=headers)
        print(r)
        if r.status_code != 200 or r.status_code != 201:
            print("ERROR")
            message = "\"Error in row " + str(item_number) + ": Encountered an error while attempting to save sample analysis " + item["id"] + ": " + r.status_code + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')
        else:
            this_response_data = r.json()
            sample_analysis_response_data.append(this_response_data)
    # send the response (data & messages) back to the user interface
    return HttpResponse(sample_analysis_response_data, content_type='application/json')


def result_search(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/mercurylab/')
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
            params_dict["date_after"] = datetime.strptime(str(params['date_after']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before']:
            params_dict["date_before"] = datetime.strptime(str(params['date_before']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')

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


def result_search_cooperators(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    context = RequestContext(request)

    if request.method == 'POST':
        params_dict = {}
        params = json.loads(request.body.decode('utf-8'))
        if params['cooperator']:
            params_dict["cooperator"] = str(params['cooperator']).strip('[]').replace(', ', ',')
        if params['project']:
            params_dict["project"] = str(params['project']).strip('[]').replace(', ', ',')
        if params['date_after']:
            params_dict["date_after"] = datetime.strptime(str(params['date_after']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before']:
            params_dict["date_before"] = datetime.strptime(str(params['date_before']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')

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


def bottles(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/mercurylab/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'bottles/')#, headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'bottletypes/')#, headers=headers_auth_token)
    bottletypes = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data, 'bottletypes': bottletypes}
    return render_to_response('mercurylab/bottles.html', context_dict, context)


def bottles_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'bottles?name='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


def bottles_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkbottles/', data=data, headers=headers)
    #return HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    for item in data:
        item = json.dumps(item)
        r = requests.request(method='PUT', url=REST_SERVICES_URL+'bottles/', data=item, headers=headers)
        print(r)
        if r.status_code != 200 or r.status_code != 201:
            print("ERROR")
            message = "\"Encountered an error while attempting to save bottle " + item["id"] + ": " + r.status_code + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')
        else:
            this_response_data = r.json()
            response_data.append(this_response_data)
    return HttpResponse(response_data, content_type='application/json')


def bottle_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkbottles/', data=data, headers=headers)
    # check for status code
    return HttpResponse(r, content_type='application/json')


def bottles_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    # table = json.loads(request.body.decode('utf-8'))
    # bottle_data = []
    #
    # for row in table:
    #     bottle_values = [row.get('bottle_unique_name'), row.get('time_stamp'), row.get('tare_weight'), row.get('bottle_type'), row.get('description')]
    #     this_bottle = dict(zip(BOTTLE_KEYS, bottle_values))
    #     bottle_data.append(this_bottle)
    #
    # bottle_data = json.dumps(bottle_data)
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkbottles/', data=data, headers=headers)
    return HttpResponse(r, content_type='application/json')


def bottle_range_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    params = json.loads(request.body.decode('utf-8'))

    digits = len(params['range_start'])
    start = int(params['range_start'])
    end = int(params['range_end'])
    new_bottles = []
    for i in range(start, end+1, 1):
        new_name = params['prefix'] + str(i).rjust(digits, '0') + params['suffix']
        new_bottle = {'bottle_unique_name': new_name, 'description': params['description'], 'tare_weight': float(params['tare_weight']), 'bottle_type': int(params['bottle_type']), 'created_date': params['created_date']}
        new_bottles.append(new_bottle)
    new_bottles = json.dumps(new_bottles)
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkbottles/', data=new_bottles, headers=headers)
    #return HttpResponseRedirect('/mercurylab/bottles/')
    return HttpResponse(r, content_type='application/json')


def brominations(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/mercurylab/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'brominations/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'samplebottlebrominations/', headers=headers_auth_token)
    samples = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data, 'samples': samples}
    return render_to_response('mercurylab/brominations.html', context_dict, context)


def brominations_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'brominations?id='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


def brominations_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkbrominations/', data=data, headers=headers_auth_token)
    #return HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    for item in data:
        item = json.dumps(item)
        r = requests.request(method='PUT', url=REST_SERVICES_URL+'brominations/', data=item, headers=headers)
        print(r)
        if r.status_code != 200 or r.status_code != 201:
            print("ERROR")
            message = "\"Encountered an error while attempting to save bromination " + item["id"] + ": " + r.status_code + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')
        else:
            this_response_data = r.json()
            response_data.append(this_response_data)
    return HttpResponse(response_data, content_type='application/json')


def bromination_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkbrominations/', data=data, headers=headers)
    return HttpResponse(r, content_type='application/json')


def samplebottlebromination_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulksamplebottlebrominations/', data=data, headers=headers)
    return HttpResponse(r, content_type='application/json')


def samplebottlebromination_search(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    context = RequestContext(request)

    if request.method == 'POST':
        params_dict = {}
        params = json.loads(request.body.decode('utf-8'))
        print(params)
        if params['bottle']:
            params_dict["bottle"] = str(params['bottle']).strip('[]').replace(', ', ',')
        if params['date_after']:
            params_dict["date_after"] = datetime.strptime(str(params['date_after']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before']:
            params_dict["date_before"] = datetime.strptime(str(params['date_before']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        print(params_dict)

        r = requests.request(method='GET', url=REST_SERVICES_URL+'samplebottlebrominations/', params=params_dict, headers=headers)
        r_dict = r.json()
        print(r_dict['count'])
        r_json = json.dumps(r_dict)
        return HttpResponse(r_json, content_type='application/json')


def blankwaters(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/mercurylab/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'blankwaters/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/blankwaters.html', context_dict, context)


def blankwaters_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'blankwaters?id='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


def blankwaters_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkblankwaters/', data=data, headers=headers_auth_token)
    #return HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    for item in data:
        item = json.dumps(item)
        r = requests.request(method='PUT', url=REST_SERVICES_URL+'blankwaters/', data=item, headers=headers)
        print(r)
        if r.status_code != 200 or r.status_code != 201:
            print("ERROR")
            message = "\"Encountered an error while attempting to save blank water " + item["id"] + ": " + r.status_code + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')
        else:
            this_response_data = r.json()
            response_data.append(this_response_data)
    return HttpResponse(response_data, content_type='application/json')


def blankwater_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkblankwaters/', data=data, headers=headers)
    return HttpResponse(r, content_type='application/json')


def acids(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/mercurylab/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/acids.html', context_dict, context)


def acids_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids?id='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


def acids_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkacids/', data=data, headers=headers_auth_token)
    #eturn HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    for item in data:
        item = json.dumps(item)
        r = requests.request(method='PUT', url=REST_SERVICES_URL+'acids/', data=item, headers=headers)
        print(r)
        if r.status_code != 200 or r.status_code != 201:
            print("ERROR")
            message = "\"Encountered an error while attempting to save acid " + item["id"] + ": " + r.status_code + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')
        else:
            this_response_data = r.json()
            response_data.append(this_response_data)
    return HttpResponse(response_data, content_type='application/json')


def acid_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkacids/', data=data, headers=headers)
    return HttpResponse(r, content_type='application/json')


def sites(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/mercurylab/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'sites/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/sites.html', context_dict, context)


def sites_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'sites?name='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


def sites_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulksites/', data=data, headers=headers_auth_token)
    #return HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    for item in data:
        item = json.dumps(item)
        r = requests.request(method='PUT', url=REST_SERVICES_URL+'sites/', data=item, headers=headers)
        print(r)
        if r.status_code != 200 or r.status_code != 201:
            print("ERROR")
            message = "\"Encountered an error while attempting to save site " + item["id"] + ": " + r.status_code + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')
        else:
            this_response_data = r.json()
            response_data.append(this_response_data)
    return HttpResponse(response_data, content_type='application/json')


def site_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'sites/', data=data, headers=headers)
    return HttpResponse(r, content_type='application/json')


def projects(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/mercurylab/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/projects.html', context_dict, context)


def projects_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects?name='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


def projects_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkprojects/', data=data, headers=headers_auth_token)
    #return HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    for item in data:
        item = json.dumps(item)
        r = requests.request(method='PUT', url=REST_SERVICES_URL+'projects/', data=item, headers=headers)
        print(r)
        if r.status_code != 200 or r.status_code != 201:
            print("ERROR")
            message = "\"Encountered an error while attempting to save project " + item["id"] + ": " + r.status_code + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')
        else:
            this_response_data = r.json()
            response_data.append(this_response_data)
    return HttpResponse(response_data, content_type='application/json')


def project_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'projects/', data=data, headers=headers)
    return HttpResponse(r, content_type='application/json')


def cooperators(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/mercurylab/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('mercurylab/cooperators.html', context_dict, context)


def cooperators_load(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    data = request.body
    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators?name='+data, headers=headers_auth_token)
    return HttpResponse(r, content_type='application/json')


def cooperators_save(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkcooperators/', data=data, headers=headers_auth_token)
    #return HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    for item in data:
        item = json.dumps(item)
        r = requests.request(method='PUT', url=REST_SERVICES_URL+'cooperators/', data=item, headers=headers)
        print(r)
        if r.status_code != 200 or r.status_code != 201:
            print("ERROR")
            message = "\"Encountered an error while attempting to save cooperator " + item["id"] + ": " + r.status_code + "\""
            print(message)
            return HttpResponse(message, content_type='text/html')
        else:
            this_response_data = r.json()
            response_data.append(this_response_data)
    return HttpResponse(response_data, content_type='application/json')


def cooperator_add(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'cooperators/', data=data, headers=headers)
    return HttpResponse(r, content_type='application/json')


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

        r = requests.request(method='POST', url=REST_AUTH_URL+'login', data=data, headers=HEADERS_CONTENT_FORM)

        if r.status_code == 200:
            # global USER_TOKEN
            # USER_TOKEN = eval(r.content)['auth_token']
            # global USER_AUTH
            # USER_AUTH = (username, password)
            token = eval(r.content)['auth_token']
            #print(token)
            request.session['token'] = token
            #request.session['username'] = username
            #request.session['password'] = password

            params_dict = {"username": username}
            headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
            r = requests.request(method='GET', url=REST_SERVICES_URL+'users/', params=params_dict, headers=headers_auth_token)

            if r.status_code == 200:
                user = r.json()[0]
                request.session['username'] = user['username']
                request.session['first_name'] = user['first_name']
                request.session['last_name'] = user['last_name']
                request.session['email'] = user['email']
                request.session['is_staff'] = user['is_staff']
                request.session['is_active'] = user['is_active']

                return HttpResponseRedirect('/mercurylab/')

            else:
                print(r)
                return render_to_response('mercurylab/login.html', r, context)

        else:
            print(r)
            #print(r.status_code)
            #print(r.reason)
            #print(r.text)
            #print(r.request.url)
            #print(r.request.headers)
            #print(r.request.method)
            #print(r.request.body)
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
    r = requests.request(method='POST', url=REST_AUTH_URL+'logout', headers=headers_auth_token)
    print(r)

    if r.status_code == 200:
        del request.session['token']
        del request.session['username']
        del request.session['first_name']
        del request.session['last_name']
        del request.session['email']
        del request.session['is_staff']
        del request.session['is_active']
        request.session.modified = True
        # global USER_AUTH
        # USER_AUTH = ('guest', 'guest')
        # global USER_TOKEN
        # USER_TOKEN = ''
        return HttpResponseRedirect('/mercurylab/')

    else:
        return HttpResponse("<h1>"+ str(r.status_code) + ": " + r.reason + "</h1><p>Logout wasn't performed. Please contact the administrator.</p>")

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
