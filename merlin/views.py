import logging
import json
import requests
from datetime import datetime
from itertools import chain
from collections import Counter
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse


########################################################################################################################
##
## copyright: 2015 WiM - USGS
## authors: Aaron Stephenson USGS WiM (Wisconsin Internet Mapping)
##
## In Django, a view is what takes a Web request and returns a Web response. The response can be many things, but most
## of the time it will be a Web page, a redirect, or a document.
##
## All these views are written as Function-Based Views (https://docs.djangoproject.com/en/1.7/topics/http/views/)
## because that is the paradigm used by most Django projects, especially tutorials for learning Django.
##
##
########################################################################################################################


logger = logging.getLogger(__name__)

## localhost dev
REST_SERVICES_URL = 'http://localhost:8000/mercuryservices/'
REST_AUTH_URL = 'http://localhost:8000/mercuryauth/'
## WIM5
#REST_SERVICES_URL = 'http://130.11.161.159/mercuryservices/'
#REST_AUTH_URL = 'http://130.11.161.159/mercuryauth/'
## WIM2
#REST_SERVICES_URL = 'http://130.11.161.247/mercuryservices/'
#REST_AUTH_URL = 'http://130.11.161.247/mercuryauth/'

#USER_AUTH = ('user', 'password')
#USER_TOKEN = ''
HEADERS_CONTENT_JSON = {'content-type': 'application/json'}
HEADERS_CONTENT_FORM = {'content-type': 'application/x-www-form-urlencoded'}


SAMPLE_KEYS_UNIQUE = ["project", "site", "sample_date_time", "depth", "replicate"]
SAMPLE_KEYS = ["project", "site", "sample_date_time", "depth", "length", "received_date", "comment",
               "replicate", "medium_type", "lab_processing"]
SAMPLE_BOTTLE_KEYS = ["sample", "bottle", "filter_type", "volume_filtered",
                      "preservation_type", "preservation_volume", "preservation_acid", "preservation_comment"]
SAMPLE_ANALYSIS_KEYS = ["sample_bottle", "constituent", "isotope_flag"]
BOTTLE_KEYS = ["bottle_prefix", "bottle_unique_name", "created_date", "description"]


def sample_login(request):
    if not request.session.get('token'):
        return HttpResponseRedirect(reverse('index'))
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
    projects = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'processings/', headers=headers_auth_token)
    processings = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'mediums/', headers=headers_auth_token)
    mediums = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'constituents/', headers=headers_auth_token)
    constituents = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'filters/', headers=headers_auth_token)
    filters = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'preservations/', headers=headers_auth_token)
    preservations = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'isotopeflags/', headers=headers_auth_token)
    isotope_flags = json.dumps(r.json(), sort_keys=True)
    context_dict = {'projects': projects, 'processings': processings, 'mediums': mediums,
                    'constituents': constituents, 'filters': filters, 'preservations': preservations,
                    'isotope_flags': isotope_flags}
    return render_to_response('merlin/sample_login.html', context_dict, context)


def samples_create(request):
    logger.info("SAMPLE LOGIN CREATE")
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    table = json.loads(request.body.decode('utf-8'))
    table_rows = len(table)
    logger.info("submitted table contains " + str(table_rows) + " rows")
    row_number = 0
    unique_sample_ids = []
    unique_bottles = []
    bottle_filter_volumes = []
    unique_sample_bottles = []
    unique_sample_analyses = []
    sample_data = []
    sample_bottle_data = []
    sample_analysis_data = []

    ## PARSE ROWS AND VALIDATE ##
    # analyze each submitted row, parsing sample data and sample bottle data
    for row in table:
        row_number += 1
        row_message = "for row " + str(row_number) + " of " + str(table_rows) + " in table..."
        logger.info(row_message)
        # grab the data that uniquely identifies each sample
        this_depth = str(row.get('depth'))
        if this_depth.startswith("."):
            this_depth = "0" + this_depth
        this_sample_id = str(row.get('project'))+"|"+str(row.get('site'))+"|"
        this_sample_id += str(row.get('sample_date_time'))+"|"+this_depth+"|"+str(row.get('replicate'))
        logger.info("this sample id: " + this_sample_id)
        # if this sample ID is not already in the unique list, add it, otherwise skip the sample data for this row
        if this_sample_id not in unique_sample_ids:
            unique_sample_ids.append(this_sample_id)

            # validate this sample doesn't exist in the database, otherwise notify the user
            logger.info("VALIDATE Sample")
            sample_values_unique = [
                row.get('project'), row.get('site'), row.get('sample_date_time'), row.get('depth'), row.get('replicate')
            ]
            this_sample_unique = dict(zip(SAMPLE_KEYS_UNIQUE, sample_values_unique))
            logger.info(str(this_sample_unique))
            # couldn't get requests.request() to work properly here, so using requests.get() instead
            r = requests.get(REST_SERVICES_URL+'samples/', params=this_sample_unique)
            logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
            response_data = r.json()
            logger.info("count: " + str(response_data['count']))
            # if response count does not equal zero, then this sample already exists in the database
            if response_data['count'] != 0:
                logger.warning("Validation Warning: " + str(sample_values_unique) + " count != 0")
                r = requests.get(REST_SERVICES_URL+'projects/', params={'id': row.get('project')})
                project_name = r.json()[0]['name']
                r = requests.get(REST_SERVICES_URL+'sites/', params={'id': row.get('site')})
                site_name = r.json()['results'][0]['name']
                message = "\"Error in row " + str(row_number) + ": This Sample already exists in the database: "
                message += project_name + "|" + site_name + "|" + str(row.get('sample_date_time')) + "|"
                message += str(row.get('depth')) + "|" + str(row.get('replicate')) + "\""
                logger.error(message)
                return HttpResponse(message, content_type='text/html')

            # if this is a new and valid sample, create a sample object using the sample data within this row
            sample_values = [row.get('project'), row.get('site'), row.get('sample_date_time'),
                             row.get('depth'), row.get('length'), row.get('received_date'), row.get('comment'),
                             row.get('replicate'), row.get('medium_type'), row.get('lab_processing')]
            this_sample = dict(zip(SAMPLE_KEYS, sample_values))
            logger.info("Creating sample: " + str(this_sample))
            sample_data.append(this_sample)

        # validate this bottle has never been used in a sample before
        logger.info("VALIDATE Bottle ID part 1 of 3")
        this_bottle = row.get('bottle')
        logger.info(this_bottle)
        r = requests.get(REST_SERVICES_URL+'samplebottles/', params={"bottle": this_bottle})
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        response_data = r.json()
        logger.info("count: " + str(response_data['count']))
        # if response count does not equal zero, then this bottle is already used by a sample in the database
        if response_data['count'] != 0:
            logger.warning("Validation Warning: " + str(this_bottle) + " count != 0")
            bottle_name = response_data['results'][0]['bottle_string']
            r = requests.get(REST_SERVICES_URL+'projects/', params={'id': row.get('project')})
            project_name = r.json()[0]['name']
            r = requests.get(REST_SERVICES_URL+'sites/', params={'id': row.get('site')})
            site_name = r.json()['results'][0]['name']
            message = "\"Error in row " + str(row_number) + ": This Bottle already used by a Sample in the database: "
            message += bottle_name + "\""
            logger.error(message)
            return HttpResponse(message, content_type='text/html')

        # validate this bottle is used only once within this sample login session,
        # otherwise hold onto its details for further validation
        logger.info("VALIDATE Bottle ID part 2 of 3")
        if this_bottle not in unique_bottles:
            logger.info(str(this_bottle) + " is unique")
            unique_bottles.append(this_bottle)
        this_sample_bottle = (this_bottle, this_sample_id)
        if this_sample_bottle not in unique_sample_bottles:
            logger.info(str(this_sample_bottle) + " is unique")
            unique_sample_bottles.append(this_sample_bottle)

        # validate no analysis(+isotope) is used more than once per sample, otherwise notify the user
        logger.info("VALIDATE Analysis")
        this_analysis = this_sample_id+"|"+str(row.get('constituent_type'))+"|"+str(row.get('isotope_flag'))
        logger.info(this_analysis)
        if this_analysis not in unique_sample_analyses:
            logger.info(this_analysis + " is unique")
            unique_sample_analyses.append(this_analysis)
        else:
            logger.warning("Validation Warning: " + this_analysis + " is not unique")
            r = requests.get(REST_SERVICES_URL+'projects/', params={'id': row.get('project')})
            project_name = r.json()[0]['name']
            r = requests.get(REST_SERVICES_URL+'sites/', params={'id': row.get('site')})
            site_name = r.json()['results'][0]['name']
            r = requests.get(REST_SERVICES_URL+'constituents/', params={'id': row.get('constituent_type')})
            constituent_name = r.json()[0]['constituent']
            r = requests.get(REST_SERVICES_URL+'isotopeflags/', params={'id': row.get('isotope_flag')})
            isotope_flag = r.json()[0]['isotope_flag']
            message = "\"Error in row " + str(row_number) + ": This Analysis (" + constituent_name + ")"
            message += " and Isotope (" + isotope_flag + ") combination appears more than once in this sample: "
            message += project_name + "|" + site_name + "|" + str(row.get('sample_date_time')) + "|"
            message += str(row.get('depth')) + "|" + str(row.get('replicate')) + "\""
            logger.error(message)
            return HttpResponse(message, content_type='text/html')

        # validate the filter volume is the same for each unique bottle
        logger.info("VALIDATE Bottle Filter Volume")
        this_bottle_filter_volume = (row.get('bottle'), row.get('volume_filtered'))
        logger.info(str(this_bottle_filter_volume))
        bottle_filter_volumes.append(this_bottle_filter_volume)
        # loop through all bottle-filter volume combinations
        for bottle_filter_volume in bottle_filter_volumes:
            # find a matching bottle record
            if this_bottle_filter_volume[0] == bottle_filter_volume[0]:
                # check if the filter volume in this bottle record is the same as the matching bottle record
                # if they don't match, stop the save and return a validation error message, otherwise move on
                if this_bottle_filter_volume[1] != bottle_filter_volume[1]:
                    logger_message = "Validation Warning: " + str(this_bottle_filter_volume)
                    logger_message += " has a mismatch with a previous bottle filter volume " + bottle_filter_volume
                    logger.warning(logger_message)
                    params = {"id": this_bottle_filter_volume[0]}
                    r = requests.get(REST_SERVICES_URL+'bottles/', params=params)
                    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
                    response_data = r.json()
                    bottle_unique_name = response_data['results'][0]['bottle_unique_name']
                    message = "\"Error in row " + str(row_number)
                    message += ": This Filter Vol (" + str(this_bottle_filter_volume[1]) + ")"
                    message += " does not match a previous Filter Vol (" + str(bottle_filter_volume[1]) + ")"
                    message += " for this Container: " + str(bottle_unique_name) + "\""
                    logger.error(message)
                    return HttpResponse(message, content_type='text/html')

        # create a sample bottle object using the sample bottle data within this row
        sample_bottle_values = [
            this_sample_id, row.get('bottle'), row.get('filter_type'), row.get('volume_filtered'),
            row.get('preservation_type'), row.get('preservation_volume'), row.get('preservation_acid'),
            row.get('preservation_comment')
        ]
        this_sample_bottle = dict(zip(SAMPLE_BOTTLE_KEYS, sample_bottle_values))
        logger.info("Creating sample bottle: " + str(this_sample_bottle))
        # add this new sample bottle object to the list
        sample_bottle_data.append(this_sample_bottle)

        # create a result object using the result data within this row
        sample_analysis_values = [str(row.get('bottle')), row.get('constituent_type'), row.get('isotope_flag')]
        this_sample_analysis = dict(zip(SAMPLE_ANALYSIS_KEYS, sample_analysis_values))
        logger.info("Creating result: " + str(this_sample_analysis))
        # add this new sample bottle object to the list
        sample_analysis_data.append(this_sample_analysis)

    # validate this bottle is used in only one sample in this sample login session,
    # otherwise notify the user (it can be used more than once within a sample, however)
    logger.info("VALIDATE Bottle ID part 3 of 3")
    sample_bottle_counter = Counter()
    for unique_bottle in unique_bottles:
        logger.info(str(unique_bottle))
        for unique_sample_bottle in unique_sample_bottles:
            logger.info(str(unique_sample_bottle))
            if unique_bottle in unique_sample_bottle:
                logger.info("bottle " + str(unique_bottle) + " is in " + str(unique_sample_bottle))
                sample_bottle_counter[unique_bottle] += 1

    for unique_bottle in unique_bottles:
        # if there is only one, then the combination of bottle ID and sample ID is unique,
        # meaning this bottle is used in more than one sample
        if sample_bottle_counter[unique_bottle] > 1:
            logger.warning("Validation Warning: " + str(unique_bottle) + " count > 1")
            params = {"id": unique_bottle}
            r = requests.get(REST_SERVICES_URL+'bottles/', params=params)
            logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
            response_data = r.json()
            bottle_unique_name = response_data['results'][0]['bottle_unique_name']
            message = "\"Error in row " + str(row_number) + ": This Container appears in more than one sample: "
            message += bottle_unique_name + "\""
            logger.error(message)
            return HttpResponse(message, content_type='text/html')
        else:
            logger.info(str(unique_bottle) + " is only used in one sample")

    ## SAVING ##
    # save samples first and then get their database IDs, which are required for saving the sample bottles afterward

    ## SAVE SAMPLES ##
    # send the samples to the database
    logger.info("SAVE Samples")
    sample_data = json.dumps(sample_data)
    logger.info(sample_data)
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulksamples/', data=sample_data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
    if r.status_code != 201:
        message = "\"Error " + str(r.status_code) + ": " + r.reason + "."
        message += " Unable to save samples. Please contact the administrator.\""
        logger.error(message)
        return HttpResponse(message, content_type='text/html')
    response_data = r.json()
    logger.info(str(len(response_data)) + " samples saved")
    logger.info(response_data)
    # store the IDs as an array of dictionaries, where the keys are the combo IDs and the values are the database IDs
    sample_ids = []
    item_number = 0
    for item in response_data:
        item_number += 1
        # using a hacky workaround here to handle the "T" in the time_stamp; there's likely a better way to handle this
        combo_id = str(item.get('project')) + "|"+str(item.get('site')) + "|"
        combo_id += str(item.get('sample_date_time')).replace("T", " ") + "|"
        combo_id += str(item.get('depth')) + "|"+str(item.get('replicate'))
        sample_id = {'combo_id': combo_id, 'db_id': item.get('id')}
        logger.info("item " + str(item_number) + ": " + str(sample_id))
        sample_ids.append(sample_id)

    ## SAVE SAMPLE BOTTLES ##
    # update the sample bottles with the database IDs, rather than the combo IDs
    logger.info("SAVE Sample Bottles")
    for sample_bottle in sample_bottle_data:
        for sample_id in sample_ids:
            logger.info("Sample Bottle Sample ID: " + str(sample_bottle['sample']))
            logger.info("Combo ID:                " + sample_id['combo_id'])
            if sample_bottle['sample'] == sample_id['combo_id']:
                sample_bottle['sample'] = sample_id['db_id']
                break
        if not isinstance(sample_bottle['sample'], int):
            logger.warning("Could not match sample and combo IDs!")
            logger.warning("Deleting samples that were just saved.")
            for sample_id in sample_ids:
                r = requests.request(
                    method='DELETE', url=REST_SERVICES_URL+'samples/' + str(sample_id['db_id']), headers=headers)
                if r.status_code != 204:
                    message = "\"Error: Able to save samples, but unable to save sample bottles."
                    message += " Encountered problem reversing saved samples"
                    message += " (specifically sample ID " + str(sample_id['db_id']) + ")."
                    message += " Please contact the administrator.\""
                    logger.error(message)
                    return HttpResponse(message, content_type='text/html')
            message = "\"Error: Can save samples, but cannot save sample bottles. Please contact the administrator.\""
            logger.error(message)
            return HttpResponse(message, content_type='text/html')
    # send the sample bottles to the database
    sample_bottle_data = json.dumps(sample_bottle_data)
    logger.info(sample_bottle_data)
    r = requests.request(
        method='POST', url=REST_SERVICES_URL+'bulksamplebottles/', data=sample_bottle_data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
    if r.status_code != 201:
        logger.warning("Could not save sample bottles!")
        logger.warning("Deleting samples that were just saved.")
        for sample_id in sample_ids:
            r = requests.request(
                method='DELETE', url=REST_SERVICES_URL+'samples/' + str(sample_id['db_id']), headers=headers)
            if r.status_code != 204:
                message = "\"Error: Can save samples, but cannot save sample bottles."
                message += " Encountered problem reversing saved samples"
                message += " (specifically sample ID " + str(sample_id['db_id']) + ")."
                message += " Please contact the administrator.\""
                logger.error(message)
                return HttpResponse(message, content_type='text/html')
        message = "\"Error " + str(r.status_code) + ": " + r.reason + "."
        message += " Can save samples, but cannot save sample bottles. Please contact the administrator.\""
        logger.error(message)
        return HttpResponse(message, content_type='text/html')
    response_data = r.json()
    logger.info(str(len(response_data)) + " sample bottles saved")
    # store the IDs as an array of dictionaries, where keys are bottle IDs and values are sample bottle IDs
    sample_bottle_ids = []
    for item in response_data:
        sample_bottle_id = {'bottle_id': str(item['bottle']), 'db_id': item['id']}
        sample_bottle_ids.append(sample_bottle_id)

    ## SAVE SAMPLE ANALYSES (placeholder records in Results table) ##
    # update the sample analyses with the sample bottle IDs, rather than the bottle IDs
    logger.info("SAVE Sample Analyses")
    for sample_analysis in sample_analysis_data:
        for sample_bottle_id in sample_bottle_ids:
            logger.info("Sample Analysis Bottle ID: " + str(sample_analysis['sample_bottle']))
            logger.info("Sample Bottle ID:          " + str(sample_bottle_id['bottle_id']))
            if sample_analysis['sample_bottle'] == sample_bottle_id['bottle_id']:
                sample_analysis['sample_bottle'] = sample_bottle_id['db_id']
                break
        if not isinstance(sample_analysis['sample_bottle'], int):
            logger.warning("Could not match sample bottle and combo bottle IDs!")
            logger.warning("Deleting sample bottles that were just saved.")
            for sample_bottle_id in sample_bottle_ids:
                this_id = str(sample_bottle_id['db_id'])
                r = requests.request(method='DELETE', url=REST_SERVICES_URL+'samplebottles/' + this_id + '/', headers=headers)
                if r.status_code != 204:
                    message = "\"Error: Can save samples and sample bottles, but cannot save analyses."
                    message += " Encountered problem reversing saved sample bottles"
                    message += " (specifically sample bottle ID " + str(sample_bottle_id['db_id']) + ")."
                    message += " Please contact the administrator.\""
                    logger.error(message)
                    return HttpResponse(message, content_type='text/html')
            logger.warning("Deleting samples that were just saved.")
            for sample_id in sample_ids:
                this_id = str(sample_id['db_id'])
                r = requests.request(method='DELETE', url=REST_SERVICES_URL+'samples/' + this_id + '/', headers=headers)
                if r.status_code != 204:
                    message = "\"Error: Can save samples and sample bottles, but cannot save analyses."
                    message += " Encountered problem reversing saved samples"
                    message += " (specifically sample ID " + str(sample_id['db_id']) + ")."
                    message += " Please contact the administrator.\""
                    logger.error(message)
                    return HttpResponse(message, content_type='text/html')
            message = "\"Error: Can save samples and sample bottles, but cannot save analyses."
            message += " Please contact the administrator.\""
            logger.error(message)
            return HttpResponse(message, content_type='text/html')
    # send the sample analyses to the database
    sample_analysis_data = json.dumps(sample_analysis_data)
    logger.info(sample_analysis_data)
    r = requests.request(
        method='POST', url=REST_SERVICES_URL+'bulkresults/', data=sample_analysis_data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
    if r.status_code != 201:
        logger.warning("Could not save sample analyses!")
        logger.warning("Deleting sample bottles that were just saved.")
        for sample_bottle_id in sample_bottle_ids:
            this_id = str(sample_bottle_id['db_id'])
            r = requests.request(method='DELETE', url=REST_SERVICES_URL+'samplebottles/' + this_id + '/', headers=headers)
            if r.status_code != 204:
                message = "\"Error: Can save samples and sample bottles, but cannot save analyses."
                message += " Encountered problem reversing saved sample bottles"
                message += " (specifically sample bottle ID " + str(sample_bottle_id['db_id']) + ")."
                message += " Please contact the administrator.\""
                logger.error(message)
                return HttpResponse(message, content_type='text/html')
        logger.warning("Deleting samples that were just saved.")
        for sample_id in sample_ids:
            this_id = str(sample_id['db_id'])
            r = requests.request(method='DELETE', url=REST_SERVICES_URL+'samples/' + this_id + '/', headers=headers)
            if r.status_code != 204:
                message = "\"Error: Can save samples and sample bottles, but cannot save analyses."
                message += " Encountered problem reversing saved samples"
                message += " (specifically sample ID " + str(sample_id['db_id']) + ")."
                message += " Please contact the administrator.\""
                logger.error(message)
                return HttpResponse(message, content_type='text/html')
        message = "\"Error: Can save samples and sample bottles, but cannot save analyses."
        message += " Please contact the administrator.\""
        logger.error(message)
        return HttpResponse(message, content_type='text/html')
    response_data = r.json()
    logger.info(str(len(response_data)) + " sample analyses saved")
    # send the response (data & messages) back to the user interface
    return HttpResponse(r, content_type='application/json')


def samples_search(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
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
        if params['constituent']:
            params_dict["constituent"] = str(params['constituent']).strip('[]')
        if params['date_after_sample']:
            params_dict["date_after_sample"] = datetime.strptime(
                str(params['date_after_sample']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before_sample']:
            params_dict["date_before_sample"] = datetime.strptime(
                str(params['date_before_sample']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['page_size']:
            params_dict["page_size"] = str(params['page_size']).strip('[]')
        if params['format']:
            params_dict["format"] = str(params['format']).strip('[]')
        if params['table']:
            params_dict["table"] = str(params['table']).strip('[]')

        r = requests.request(method='GET', url=REST_SERVICES_URL+'fullresults/', params=params_dict, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        if params['format'] == 'csv':
            response = HttpResponse(r, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="results.csv"'
            response.write(r.content)
            return response
        else:
            r_dict = r.json()
            logger.info("search results count: " + str(r_dict['count']))
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
        context_dict = {'projects': projects, 'processings': processings,
                        'constituents': constituents, 'mediums': mediums, 'filters': filters,
                        'preservations': preservations, 'isotope_flags': isotope_flags}

        return render_to_response('merlin/sample_search.html', context_dict, context)


def samples_update(request):
    logger.info("SAMPLE LOGIN UPDATE")
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    table = json.loads(request.body.decode('utf-8'))
    table_rows = len(table)
    logger.info("submitted table contains " + str(table_rows) + " rows")
    row_number = 0
    unique_sample_ids = []
    sample_data = []
    sample_bottle_data = []
    sample_analysis_data = []

    ## PARSE ROWS AND VALIDATE ##
    # analyze each submitted row, parsing sample data and sample bottle data
    for row in table:
        row_number += 1
        row_message = "for row " + str(row_number) + " of " + str(table_rows) + " in table..."
        logger.info(row_message)
        # grab the data that uniquely identifies each sample
        this_sample_id = row.get('sample_bottle.sample.id')
        logger.info("this sample id: " + str(this_sample_id))
        # if this sample ID is not already in the unique list, add it, otherwise skip the sample data for this row
        if this_sample_id not in unique_sample_ids:
            unique_sample_ids.append(this_sample_id)

            # validate this sample already exists in the database, otherwise notify the user
            logger.info("VALIDATE Sample in Search Save")
            #sample_values_unique = [
            #    row.get('project'), row.get('site'), row.get('sample_date_time'), row.get('depth'), row.get('replicate')
            #]
            #this_sample_unique = dict(zip(SAMPLE_KEYS_UNIQUE, sample_values_unique))
            #logger.info(str(this_sample_unique))
            # couldn't get requests.request() to work properly here, so using requests.get() instead
            #r = requests.get(REST_SERVICES_URL+'samples/', params=this_sample_unique)
            r = requests.get(REST_SERVICES_URL+'samples/', params={"id": this_sample_id})
            logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
            response_data = r.json()
            logger.info("count: " + str(response_data['count']))
            # if response count equals zero, then this sample does not exist in the database
            if response_data['count'] == 0:
                #logger.warning("Validation Warning: " + str(sample_values_unique) + " count == 0")
                logger.warning("Validation Warning: " + str(this_sample_id) + " count == 0")
                r = requests.get(REST_SERVICES_URL+'projects/', params={'id': row.get('project')})
                project_name = r.json()[0]['name']
                r = requests.get(REST_SERVICES_URL+'sites/', params={'id': row.get('site')})
                site_name = r.json()['results'][0]['name']
                message = "\"Error in row " + str(row_number) + ":"
                message += " Cannot save because this Sample does not exist in the database: "
                message += project_name + "|" + site_name + "|" + str(row.get('sample_date_time')) + "|"
                message += str(row.get('depth')) + "|" + str(row.get('replicate')) + "."
                message += " Please use the Sample Login tool to add it.\""
                logger.error(message)
                return HttpResponse(message, content_type='text/html')

            # if this is an existing and valid sample, create a sample object using the sample data within this row
            sample_values = [
                row.get('sample_bottle.sample.id'), row.get('project'), row.get('site'),
                row.get('sample_date_time'), row.get('depth'), row.get('length'), row.get('received_date'),
                row.get('comment'), row.get('replicate'), row.get('medium_type'), row.get('lab_processing')
            ]
            this_sample_keys = [
                "id", "project", "site",
                "sample_date_time", "depth", "length", "received_date",
                "comment", "replicate", "medium_type", "lab_processing"
            ]
            this_sample = dict(zip(this_sample_keys, sample_values))
            logger.info("Creating sample: " + str(this_sample))
            sample_data.append(this_sample)

        # create a sample bottle object using the sample bottle data within this row
        sample_bottle_values = [
            row.get('sample_bottle.id'), row.get('sample_bottle.sample.id'), row.get('bottle'),
            row.get('filter_type'), row.get('volume_filtered'), row.get('preservation_type'),
            row.get('preservation_volume'), row.get('preservation_acid'), row.get('preservation_comment')
        ]
        this_sample_bottle_keys = [
            "id", "sample", "bottle",
            "filter_type", "volume_filtered", "preservation_type",
            "preservation_volume", "preservation_acid", "preservation_comment"
        ]
        this_sample_bottle = dict(zip(this_sample_bottle_keys, sample_bottle_values))
        logger.info("Creating sample bottle: " + str(this_sample_bottle))
        # add this new sample bottle object to the list
        sample_bottle_data.append(this_sample_bottle)

        # create a result object using the result data within this row
        sample_analysis_values = [
            row.get('id'), row.get('sample_bottle.id'), row.get('constituent_type'), row.get('isotope_flag')]
        this_sample_analysis_keys = ["id", "sample_bottle", "constituent", "isotope_flag"]
        this_sample_analysis = dict(zip(this_sample_analysis_keys, sample_analysis_values))
        logger.info("Creating result: " + str(this_sample_analysis))
        # add this new sample bottle object to the list
        sample_analysis_data.append(this_sample_analysis)

    ## SAVING ##
    # save samples first and then get their database IDs, which are required for saving the sample bottles afterward

    ## SAVE SAMPLES ##
    # send the samples to the database
    logger.info("SAVE Samples in Search Save")
    #sample_data = json.dumps(sample_data)
    logger.info(str(sample_data))
    sample_response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    item_number = 0
    for item in sample_data:
        item_number += 1
        this_id = item.pop("id")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        url = REST_SERVICES_URL+'samples/'+str(this_id)+'/'
        r = requests.request(method='PUT', url=url, data=item, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        # if r.status_code != 200 or r.status_code != 201:
        #     message = "\"Error in row " + str(item_number) + ": Encountered an error while attempting to save sample "
        #     message += str(this_id) + ": " + str(r.status_code) + "\""
        #     logger.error(message)
        #     return HttpResponse(message, content_type='text/html')
        # else:
        #     this_response_data = r.json()
        #     logger.info(str(len(this_response_data)) + " samples saved")
        #     sample_response_data.append(this_response_data)
        this_response_data = r.json()
        logger.info("1 samples saved")
        sample_response_data.append(this_response_data)
    logger.info(sample_response_data)

    ## SAVE SAMPLE BOTTLES ##
    # update the sample bottles with the database IDs, rather than the combo IDs
    logger.info("SAVE Sample Bottles in Search Save")
    # send the sample bottles to the database
    #sample_bottle_data = json.dumps(sample_bottle_data)
    logger.info(str(sample_bottle_data))
    sample_bottle_response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    item_number = 0
    for item in sample_bottle_data:
        item_number += 1
        this_id = item.pop("id")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        url = REST_SERVICES_URL+'samplebottles/'+str(this_id)+'/'
        r = requests.request(method='PUT', url=url, data=item, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        # if r.status_code != 200 or r.status_code != 201:
        #     message = "\"Error in row " + str(item_number) + ": Encountered an error while attempting to save"
        #     message += " sample bottle in sample " + str(this_id) + ": " + str(r.status_code) + "\""
        #     logger.error(message)
        #     return HttpResponse(message, content_type='text/html')
        # else:
        #     this_response_data = r.json()
        #     logger.info(str(len(this_response_data)) + " sample bottles saved")
        #     sample_bottle_response_data.append(this_response_data)
        this_response_data = r.json()
        logger.info(r.request.body)
        logger.info(this_response_data)
        logger.info("1 sample bottles saved")
        sample_bottle_response_data.append(this_response_data)

    ## SAVE SAMPLE ANALYSES (placeholder records in Results table) ##
    # update the sample analyses with the sample bottle IDs, rather than the bottle IDs
    logger.info("SAVE Sample Analyses in Search Save")
    # send the sample analyses to the database
    #sample_analysis_data = json.dumps(sample_analysis_data)
    logger.info(str(sample_analysis_data))
    sample_analysis_response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    item_number = 0
    for item in sample_analysis_data:
        item_number += 1
        this_id = item.pop("id")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        url = REST_SERVICES_URL+'results/'+str(this_id)+'/'
        r = requests.request(method='PUT', url=url, data=item, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        # if r.status_code != 200 or r.status_code != 201:
        #     message = "\"Error in row " + str(item_number) + ": Encountered an error while attempting to save"
        #     message += " sample analysis " + str(this_id) + ": " + str(r.status_code) + "\""
        #     logger.error(message)
        #     return HttpResponse(message, content_type='text/html')
        # else:
        #     this_response_data = r.json()
        #     logger.info(str(len(this_response_data)) + " sample analyses saved")
        #     sample_analysis_response_data.append(this_response_data)
        this_response_data = r.json()
        logger.info("1 sample analyses saved")
        sample_analysis_response_data.append(this_response_data)
    sample_analysis_response_data = json.dumps(sample_analysis_response_data)
    # send the response (data & messages) back to the user interface
    return HttpResponse(sample_analysis_response_data, content_type='application/json')


def results_search(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
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
        if params['date_after_sample']:
            params_dict["date_after_sample"] = datetime.strptime(
                str(params['date_after_sample']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before_sample']:
            params_dict["date_before_sample"] = datetime.strptime(
                str(params['date_before_sample']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_after_entry']:
            params_dict["date_after_entry"] = datetime.strptime(
                str(params['date_after_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before_entry']:
            params_dict["date_before_entry"] = datetime.strptime(
                str(params['date_before_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['exclude_null_results']:
            params_dict["exclude_null_results"] = str(params['exclude_null_results']).strip('[]')
        if params['page_size']:
            params_dict["page_size"] = str(params['page_size']).strip('[]')
        if params['format']:
            params_dict["format"] = str(params['format']).strip('[]')
        if params['table']:
            params_dict["table"] = str(params['table']).strip('[]')

        r = requests.request(method='GET', url=REST_SERVICES_URL+'fullresults/', params=params_dict, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        if params['format'] == 'csv':
            response = HttpResponse(r, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="results.csv"'
            response.write(r.content)
            return response
        else:
            r_dict = r.json()
            logger.info("search results count: " + str(r_dict['count']))
            r_json = json.dumps(r_dict)
            return HttpResponse(r_json, content_type='application/json')

    else:  # request.method == 'GET'
        r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
        projects = json.dumps(r.json(), sort_keys=True)
        r = requests.request(method='GET', url=REST_SERVICES_URL+'constituents/', headers=headers_auth_token)
        constituents = json.dumps(r.json(), sort_keys=True)
        context_dict = {'projects': projects, 'constituents': constituents}

        return render_to_response('merlin/result_search.html', context_dict, context)


def results_count_nawqa(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    context = RequestContext(request)

    if request.method == 'POST':
        params_dict = {}
        params = json.loads(request.body.decode('utf-8'))
        if params['date_after_entry']:
            params_dict["date_after_entry"] = datetime.strptime(
                str(params['date_after_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before_entry']:
            params_dict["date_before_entry"] = datetime.strptime(
                str(params['date_before_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['page_size']:
            params_dict["page_size"] = str(params['page_size']).strip('[]')

        r = requests.request(
            method='GET', url=REST_SERVICES_URL+'resultcountnawqa/', params=params_dict, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search result count nawqa report count: " + str(r_dict['count']))
        r_json = json.dumps(r_dict)
        return HttpResponse(r_json, content_type='application/json')

    else:  # request.method == 'GET'
        r = requests.request(method='GET', url=REST_SERVICES_URL+'resultcountnawqa/', headers=headers_auth_token)
        data = json.dumps(r.json(), sort_keys=True)
        context_dict = {'data': data}

        return render_to_response('merlin/results_count_nawqa.html', context_dict, context)


def results_count_projects(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    context = RequestContext(request)

    if request.method == 'POST':
        params_dict = {}
        params = json.loads(request.body.decode('utf-8'))
        if params['date_after_entry']:
            params_dict["date_after_entry"] = datetime.strptime(
                str(params['date_after_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before_entry']:
            params_dict["date_before_entry"] = datetime.strptime(
                str(params['date_before_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['page_size']:
            params_dict["page_size"] = str(params['page_size']).strip('[]')

        r = requests.request(
            method='GET', url=REST_SERVICES_URL+'resultcountprojects/', params=params_dict, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search results count project report count: " + str(r_dict['count']))
        r_json = json.dumps(r_dict)
        return HttpResponse(r_json, content_type='application/json')

    else:  # request.method == 'GET'
        r = requests.request(method='GET', url=REST_SERVICES_URL+'resultcountprojects/', headers=headers_auth_token)
        data = json.dumps(r.json(), sort_keys=True)
        context_dict = {'data': data}

        return render_to_response('merlin/results_count_projects.html', context_dict, context)


def samples_nwis_report(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    context = RequestContext(request)

    if request.method == 'POST':
        params_dict = {}
        params = json.loads(request.body.decode('utf-8'))
        if params['project']:
            params_dict["project"] = str(params['project']).strip('[]').replace(', ', ',')
        if params['project_not']:
            params_dict["project_not"] = str(params['project_not']).strip('[]').replace(', ', ',')
        if params['date_after_entry']:
            params_dict["date_after_entry"] = datetime.strptime(
                str(params['date_after_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before_entry']:
            params_dict["date_before_entry"] = datetime.strptime(
                str(params['date_before_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['page_size']:
            params_dict["page_size"] = str(params['page_size']).strip('[]')

        r = requests.request(
            method='GET', url=REST_SERVICES_URL+'reportsamplesnwis/', params=params_dict, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search samples nwis report count: " + str(r_dict['count']))
        r_json = json.dumps(r_dict)
        return HttpResponse(r_json, content_type='application/json')

    else:  # request.method == 'GET'
        r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
        projects = json.dumps(r.json(), sort_keys=True)
        context_dict = {'projects': projects}

        return render_to_response('merlin/samples_nwis.html', context_dict, context)


def results_nwis_report(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    context = RequestContext(request)

    if request.method == 'POST':
        params_dict = {}
        params = json.loads(request.body.decode('utf-8'))
        if params['project']:
            params_dict["project"] = str(params['project']).strip('[]').replace(', ', ',')
        if params['project_not']:
            params_dict["project_not"] = str(params['project_not']).strip('[]').replace(', ', ',')
        if params['date_after_entry']:
            params_dict["date_after_entry"] = datetime.strptime(
                str(params['date_after_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before_entry']:
            params_dict["date_before_entry"] = datetime.strptime(
                str(params['date_before_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['page_size']:
            params_dict["page_size"] = str(params['page_size']).strip('[]')
        if params['exclude_ld']:
            params_dict["exclude_ld"] = str(params['exclude_ld']).strip('[]')

        r = requests.request(
            method='GET', url=REST_SERVICES_URL+'reportresultsnwis/', params=params_dict, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search results nwis report count: " + str(r_dict['count']))
        r_json = json.dumps(r_dict)
        return HttpResponse(r_json, content_type='application/json')

    else:  # request.method == 'GET'
        r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
        projects = json.dumps(r.json(), sort_keys=True)
        context_dict = {'projects': projects}

        return render_to_response('merlin/results_nwis.html', context_dict, context)


def results_cooperator_report(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
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
        if params['project_not']:
            params_dict["project_not"] = str(params['project_not']).strip('[]').replace(', ', ',')
        if params['date_after_entry']:
            params_dict["date_after_entry"] = datetime.strptime(
                str(params['date_after_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before_entry']:
            params_dict["date_before_entry"] = datetime.strptime(
                str(params['date_before_entry']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['page_size']:
            params_dict["page_size"] = str(params['page_size']).strip('[]')

        r = requests.request(
            method='GET', url=REST_SERVICES_URL+'reportresultscooperator/', params=params_dict, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search results cooperator report count: " + str(r_dict['count']))
        r_json = json.dumps(r_dict)
        return HttpResponse(r_json, content_type='application/json')

    else:  # request.method == 'GET'
        r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
        projects = json.dumps(r.json(), sort_keys=True)
        r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', headers=headers_auth_token)
        cooperators = json.dumps(r.json(), sort_keys=True)
        context_dict = {'projects': projects, 'cooperators': cooperators}
        return render_to_response('merlin/results_cooperator.html', context_dict, context)


def bottles(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    #headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'bottles/')  # , headers=headers_auth_token)
    bottles = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'bottleprefixes/')  # , headers=headers_auth_token)
    prefixes = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'bottletypes/')  # , headers=headers_auth_token)
    bottletypes = json.dumps(r.json(), sort_keys=True)
    context_dict = {'bottles': bottles, 'prefixes': prefixes, 'bottletypes': bottletypes}
    return render_to_response('merlin/bottles.html', context_dict, context)


def bottles_update(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    item_number = 0
    for item in data:
        item_number += 1
        this_id = item.pop("id")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        url = REST_SERVICES_URL+'bottles/'+str(this_id)+'/'
        r = requests.request(method='PUT', url=url, data=item, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        # if r.status_code != 200:# or r.status_code != 201:
        #     message = "\"Encountered an error while attempting to save bottle.\""
        #     logger.error(message)
        #     return HttpResponse(message, content_type='text/html')
        # else:
        #     this_response_data = r.json()
        #     logger.info(str(len(this_response_data)) + " bottles saved")
        #     response_data.append(this_response_data)
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def bottle_prefixes_update(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    item_number = 0
    for item in data:
        item_number += 1
        this_id = item.pop("id")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        url = REST_SERVICES_URL+'bottleprefixes/'+str(this_id)+'/'
        r = requests.request(method='PUT', url=url, data=item, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        # if r.status_code != 200:# or r.status_code != 201:
        #     message = "\"Encountered an error while attempting to save bottle prefix.\""
        #     logger.error(message)
        #     return HttpResponse(message, content_type='text/html')
        # else:
        #     this_response_data = r.json()
        #     logger.info(str(len(this_response_data)) + " bottle prefixes saved")
        #     response_data.append(this_response_data)
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def bottle_prefixes_create(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))

    # validate that the submitted bottle prefix doesn't already exist
    logger.info("VALIDATE Bottle Prefix Add")
    this_bottle_prefix = {'bottle_prefix': data.get('bottle_prefix')}
    r = requests.get(REST_SERVICES_URL+'bottleprefixes/', params=this_bottle_prefix)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    response_data = r.json()
    logger.info("bottle prefix count: " + str(response_data['count']))
    logger.info("bottle prefix count: " + str(response_data['count']))
    # if response count does not equal zero, then this sample already exists in the database
    if response_data['count'] != 0:
        logger.warning("Validation Warning: " + data.get('bottle_prefix') + " count != 0")
        message = "This Bottle Prefix already exists in the database: "
        return HttpResponse(message, content_type='text/html')

    ## SAVE Bottle Prefixes ##
    # send the bottle prefixes to the database
    data = json.dumps(data)
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkbottleprefixes/', data=data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    if r.status_code != 201:
        message = "\"Error " + str(r.status_code) + ": " + r.reason + ". Cannot save bottle prefix."
        message += " Please contact the administrator.\""
        logger.error(message)
        return HttpResponse(message, content_type='text/html')
    else:
        logger.info("1 bottle prefixes saved")
        return HttpResponse(r, content_type='application/json')


def bottle_prefixes_delete(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    url = REST_SERVICES_URL+'bottleprefixes/'+str(this_id)+'/'
    r = requests.request(method='DELETE', url=url, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def bottle_prefixes_range_create(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    params = json.loads(request.body.decode('utf-8'))
    all_unique_bottle_prefixes = True
    message_exist = "No new Bottle Prefixes were saved because these Bottle Prefixes already exist in the database: "

    digits = len(params['range_start'])
    start = int(params['range_start'])
    end = int(params['range_end'])
    new_bottle_prefixes = []
    for i in range(start, end+1, 1):
        new_prefix = params['prefix'] + str(i).rjust(digits, '0')
        new_bottle_prefix = {'bottle_prefix': new_prefix, 'description': params['description'],
                             'tare_weight': float(params['tare_weight']), 'bottle_type': int(params['bottle_type']),
                             'created_date': params['created_date']}
        logger.info(str(new_bottle_prefix))
        new_bottle_prefixes.append(new_bottle_prefix)

    # validate that the submitted bottle prefixes don't already exist
    logger.info("VALIDATE Bottle Prefix Range")
    for item in new_bottle_prefixes:
        this_bottle_prefix = item.get('bottle_prefix')
        r = requests.get(REST_SERVICES_URL+'bottleprefixes/', params={'bottle_prefix': this_bottle_prefix})
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        response_data = r.json()
        logger.info("bottles count: " + str(response_data['count']))
        # if response count does not equal zero, then this sample already exists in the database
        if response_data['count'] != 0:
            all_unique_bottle_prefixes = False
            logger.warning("Validation Warning: " + str(this_bottle_prefix) + " count == 0")
            this_message = str(this_bottle_prefix) + ","
            message_exist = message_exist + " " + this_message
    if not all_unique_bottle_prefixes:
        message = json.dumps(message_exist)
        logger.warning("Validation Warning: " + message)
        return HttpResponse(message, content_type='text/html')

    ## SAVE Bottle Prefixes ##
    # send the bottle prefixes to the database
    new_bottle_prefixes = json.dumps(new_bottle_prefixes)
    r = requests.request(
        method='POST', url=REST_SERVICES_URL+'bulkbottleprefixes/', data=new_bottle_prefixes, headers=headers)
    logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
    if r.status_code != 201:
        message = "\"Error " + str(r.status_code) + ": " + r.reason + ". Cannot save bottle prefixes."
        message += " Please contact the administrator.\""
        logger.error(message)
        return HttpResponse(message, content_type='text/html')
    else:
        logger.info("range of bottle prefixes saved")
        return HttpResponse(r, content_type='application/json')


def bottles_create(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    all_unique_bottle_names = True
    all_existing_bottle_prefixes = True
    message_exist = "No new Bottles were saved because these Bottles already exist in the database:   "
    message_not_exist = "No new Bottles were saved because these Bottle Prefixes do not exist in the database: "

    # validate that the submitted bottle names don't already exist
    logger.info("VALIDATE Bottles Add")
    item_number = 0
    for item in data:
        item_number += 1
        this_bottle_name = {'bottle_unique_name': item.get('bottle_unique_name')}
        r = requests.get(REST_SERVICES_URL+'bottles/', params=this_bottle_name)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        response_data = r.json()
        logger.info("bottles count: " + str(response_data['count']))
        # if response count does not equal zero, then this sample already exists in the database
        if response_data['count'] != 0:
            all_unique_bottle_names = False
            logger.warning("Validation Warning: " + item.get('bottle_unique_name') + " count != 0")
            this_message = "Row " + str(item_number) + ": " + item.get('bottle_unique_name') + ","
            message_exist = message_exist + " " + this_message
    if not all_unique_bottle_names:
        message = json.dumps(message_exist)
        logger.warning("Validation Warning: " + message)
        return HttpResponse(message, content_type='text/html')

    # validate that the submitted bottle prefixes already exist
    logger.info("VALIDATE Bottles Add Prefixes")
    item_number = 0
    for item in data:
        item_number += 1
        this_bottle_prefix = item.get('bottle_prefix')
        r = requests.get(REST_SERVICES_URL+'bottleprefixes/', params={'bottle_prefix': this_bottle_prefix})
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        response_data = r.json()
        logger.info("bottles count: " + str(response_data['count']))
        # if response count equals zero, then this sample does not exist in the database
        if response_data['count'] == 0:
            all_existing_bottle_prefixes = False
            logger.warning("Validation Warning: " + str(this_bottle_prefix) + " count == 0")
            this_message = "Row " + str(item_number) + ": " + str(this_bottle_prefix) + ","
            message_not_exist = message_not_exist + " " + this_message
    if not all_existing_bottle_prefixes:
        message = json.dumps(message_not_exist)
        logger.warning("Validation Warning: " + message)
        return HttpResponse(message, content_type='text/html')

    ## SAVE Bottles ##
    # send the bottles to the database
    logger.info("SAVE Bottles")
    table = json.loads(request.body.decode('utf-8'))
    bottle_data = []
    for row in table:
        bottle_values = [
            row.get('bottle_prefix'), row.get('bottle_unique_name'), row.get('created_date'), row.get('description')
        ]
        this_bottle = dict(zip(BOTTLE_KEYS, bottle_values))
        bottle_data.append(this_bottle)
    bottle_data = json.dumps(bottle_data)
    logger.info(bottle_data)
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkbottles/', data=bottle_data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    if r.status_code != 201:
        message = "\"Error " + str(r.status_code) + ": " + r.reason + ". Cannot save bottles."
        message += " Please contact the administrator.\""
        logger.error(message)
        return HttpResponse(message, content_type='text/html')
    else:
        logger.info("bottles saved")
        return HttpResponse(r, content_type='application/json')


def bottles_delete(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    url = REST_SERVICES_URL+'bottles/'+str(this_id)+'/'
    r = requests.request(method='DELETE', url=url, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def brominations(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'brominations/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'samplebottlebrominations/', headers=headers_auth_token)
    samples = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data, 'samples': samples}
    return render_to_response('merlin/brominations.html', context_dict, context)


def brominations_update(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(
    # method='PUT', url=REST_SERVICES_URL+'bulkbrominations/', data=data, headers=headers_auth_token)
    #return HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    # item_number = 0
    # for item in data:
    #     item_number += 1
    #     item_id = item["id"]
    #     item = json.dumps(item)
    #     logger.info("Item #" + str(item_number) + ": " + item)
    #     r = requests.request(method='PUT', url=REST_SERVICES_URL+'brominations/', data=item, headers=headers)
    #     logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    #     if r.status_code != 200 or r.status_code != 201:
    #         message = "\"Encountered an error while attempting to save bromination "
    #         message += str(item_id) + ": " + str(r.status_code) + "\""
    #         logger.error(message)
    #         return HttpResponse(message, content_type='text/html')
    #     else:
    #         this_response_data = r.json()
    #         logger.info(str(len(this_response_data)) + " brominations saved")
    #         response_data.append(this_response_data)
    item_number = 0
    for item in data:
        item_number += 1
        this_id = item.pop("id")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        url = REST_SERVICES_URL+'brominations/'+str(this_id)+'/'
        r = requests.request(method='PUT', url=url, data=item, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        # if r.status_code != 200:# or r.status_code != 201:
        #     message = "\"Encountered an error while attempting to save bromination.\""
        #     logger.error(message)
        #     return HttpResponse(message, content_type='text/html')
        # else:
        #     this_response_data = r.json()
        #     logger.info(str(len(this_response_data)) + " brominations saved")
        #     response_data.append(this_response_data)
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def brominations_create(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkbrominations/', data=data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def brominations_delete(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    url = REST_SERVICES_URL+'brominations/'+str(this_id)+'/'
    r = requests.request(method='DELETE', url=url, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def samplebottlebrominations_create(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    all_valid_sample_bottles = True
    message_not_valid = "These Sample Bottles are not for UTHG or FTHG: "

    # validate that the submitted sample bottles have samples with constituents of UTHG or FTHG
    logger.info("VALIDATE Sample Bottles Brominations")
    item_number = 0
    for item in data:
        item_number += 1
        params = {'id': item.get('sample_bottle'), 'constituent': '39,27'}
        r = requests.get(REST_SERVICES_URL+'samplebottles/', params=params)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        response_data = r.json()
        logger.info("bottles count: " + str(response_data['count']))
        # if response count does not equal one, then this sample bottle is not valid
        if response_data['count'] != 1:
            all_valid_sample_bottles = False
            logger.warning("Validation Warning: " + str(item.get('sample_bottle')) + " count != 1")
            this_message = "Row " + str(item_number) + ","
            message_not_valid = message_not_valid + " " + this_message
    if not all_valid_sample_bottles:
        message = json.dumps(message_not_valid)
        logger.warning("Validation Warning: " + message)
        return HttpResponse(message, content_type='text/html')

    ## SAVE Sample Bottle Brominations ##
    # send the sample bottle brominations to the database
    logger.info("SAVE Sample Bottle Brominations")
    table = json.loads(request.body.decode('utf-8'))
    brom_data = []
    for row in table:
        this_brom = {'bromination': row.get('bromination'), 'sample_bottle': row.get('sample_bottle'),
                     'bromination_event': row.get('bromination_event'),
                     'bromination_volume': row.get('bromination_volume'), 'created_date': row.get('created_date')}
        brom_data.append(this_brom)
    brom_data = json.dumps(brom_data)
    logger.info(brom_data)
    r = requests.request(
        method='POST', url=REST_SERVICES_URL+'bulksamplebottlebrominations/', data=brom_data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    if r.status_code != 201:
        message = "\"Error " + str(r.status_code) + ": " + r.reason + ". Cannot save sample bottle brominations."
        message += " Please contact the administrator.\""
        logger.error(message)
        return HttpResponse(message, content_type='text/html')
    else:
        logger.info("sample bottle brominations saved")
        return HttpResponse(r, content_type='application/json')


def samplebottlebrominations_search(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))

    if request.method == 'POST':
        params_dict = {}
        params = json.loads(request.body.decode('utf-8'))
        logger.info(params)
        if params['bottle']:
            params_dict["bottle"] = str(params['bottle']).strip('[]').replace(', ', ',')
        if params['date_after']:
            params_dict["date_after"] = datetime.strptime(
                str(params['date_after']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        if params['date_before']:
            params_dict["date_before"] = datetime.strptime(
                str(params['date_before']).strip('[]'), '%m/%d/%y').strftime('%Y-%m-%d')
        #logger.info(params_dict)

        r = requests.request(
            method='GET', url=REST_SERVICES_URL+'samplebottlebrominations/', params=params_dict, headers=headers)
        logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search sample bottles brominations count: " + str(r_dict['count']))
        r_json = json.dumps(r_dict)
        return HttpResponse(r_json, content_type='application/json')


def samplebottlebrominations_delete(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    url = REST_SERVICES_URL+'samplebottlebrominations/'+str(this_id)+'/'
    r = requests.request(method='DELETE', url=url, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def blankwaters(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'blankwaters/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('merlin/blankwaters.html', context_dict, context)


def blankwaters_update(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkblankwaters/', data=data, headers=headers_auth_token)
    #return HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    #
    item_number = 0
    for item in data:
        item_number += 1
        this_id = item.pop("id")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        url = REST_SERVICES_URL+'blankwaters/'+str(this_id)+'/'
        r = requests.request(method='PUT', url=url, data=item, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        # if r.status_code != 200:# or r.status_code != 201:
        #     message = "\"Encountered an error while attempting to save blankwater.\""
        #     logger.error(message)
        #     return HttpResponse(message, content_type='text/html')
        # else:
        #     this_response_data = r.json()
        #     logger.info(str(len(this_response_data)) + " blankwater saved")
        #     response_data.append(this_response_data)
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def blankwaters_create(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkblankwaters/', data=data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def blankwaters_delete(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    url = REST_SERVICES_URL+'blankwaters/'+str(this_id)+'/'
    r = requests.request(method='DELETE', url=url, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def acids(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'acids/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('merlin/acids.html', context_dict, context)


def acids_update(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkacids/', data=data, headers=headers_auth_token)
    #eturn HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    # item_number = 0
    # for item in data:
    #     item_number += 1
    #     item_id = item["id"]
    #     item = json.dumps(item)
    #     logger.info("Item #" + str(item_number) + ": " + item)
    #     r = requests.request(method='PUT', url=REST_SERVICES_URL+'acids/', data=item, headers=headers)
    #     logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    #     if r.status_code != 200 or r.status_code != 201:
    #         message = "\"Encountered an error while attempting to save acid "
    #         message += str(item_id) + ": " + str(r.status_code) + "\""
    #         logger.error(message)
    #         return HttpResponse(message, content_type='text/html')
    #     else:
    #         this_response_data = r.json()
    #         logger.info(str(len(this_response_data)) + " acids saved")
    #         response_data.append(this_response_data)
    item_number = 0
    for item in data:
        item_number += 1
        this_id = item.pop("id")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        url = REST_SERVICES_URL+'acids/'+str(this_id)+'/'
        r = requests.request(method='PUT', url=url, data=item, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        # if r.status_code != 200:# or r.status_code != 201:
        #     message = "\"Encountered an error while attempting to save acid.\""
        #     logger.error(message)
        #     return HttpResponse(message, content_type='text/html')
        # else:
        #     this_response_data = r.json()
        #     logger.info(str(len(this_response_data)) + " acids saved")
        #     response_data.append(this_response_data)
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def acids_create(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkacids/', data=data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def acids_delete(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    url = REST_SERVICES_URL+'acids/'+str(this_id)+'/'
    r = requests.request(method='DELETE', url=url, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def sites(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'sites/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
    projects = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data, 'projects': projects}
    return render_to_response('merlin/sites.html', context_dict, context)


def sites_update(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulksites/', data=data, headers=headers_auth_token)
    #return HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    # item_number = 0
    # for item in data:
    #     item_number += 1
    #     item_id = item["id"]
    #     item = json.dumps(item)
    #     logger.info("Item #" + str(item_number) + ": " + item)
    #     r = requests.request(method='PUT', url=REST_SERVICES_URL+'sites/', data=item, headers=headers)
    #     logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    #     if r.status_code != 200 or r.status_code != 201:
    #         message = "\"Encountered an error while attempting to save site "
    #         message += str(item_id) + ": " + str(r.status_code) + "\""
    #         logger.error(message)
    #         return HttpResponse(message, content_type='text/html')
    #     else:
    #         this_response_data = r.json()
    #         logger.info(str(len(this_response_data)) + " sites saved")
    #         response_data.append(this_response_data)
    item_number = 0
    for item in data:
        item_number += 1
        this_id = item.pop("id")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        url = REST_SERVICES_URL+'sites/'+str(this_id)+'/'
        r = requests.request(method='PUT', url=url, data=item, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        # if r.status_code != 200:# or r.status_code != 201:
        #     message = "\"Encountered an error while attempting to save site.\""
        #     logger.error(message)
        #     return HttpResponse(message, content_type='text/html')
        # else:
        #     this_response_data = r.json()
        #     logger.info(str(len(this_response_data)) + " sites saved")
        #     response_data.append(this_response_data)
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def sites_create(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulksites/', data=data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def sites_delete(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    url = REST_SERVICES_URL+'sites/'+str(this_id)+'/'
    r = requests.request(method='DELETE', url=url, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def projects(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', headers=headers_auth_token)
    cooperators = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data, 'cooperators': cooperators}
    return render_to_response('merlin/projects.html', context_dict, context)


def projects_update(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkprojects/', data=data, headers=headers_auth_token)
    #return HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    # item_number = 0
    # for item in data:
    #     item_number += 1
    #     item_id = item["id"]
    #     item = json.dumps(item)
    #     logger.info("Item #" + str(item_number) + ": " + item)
    #     r = requests.request(method='PUT', url=REST_SERVICES_URL+'projects/', data=item, headers=headers)
    #     logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    #     if r.status_code != 200 or r.status_code != 201:
    #         message = "\"Encountered an error while attempting to save project "
    #         message += str(item_id) + ": " + str(r.status_code) + "\""
    #         logger.error(message)
    #         return HttpResponse(message, content_type='text/html')
    #     else:
    #         this_response_data = r.json()
    #         logger.info(str(len(this_response_data)) + " projects saved")
    #         response_data.append(this_response_data)
    item_number = 0
    for item in data:
        item_number += 1
        this_id = item.pop("id")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        url = REST_SERVICES_URL+'projects/'+str(this_id)+'/'
        r = requests.request(method='PUT', url=url, data=item, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        # if r.status_code != 200:# or r.status_code != 201:
        #     message = "\"Encountered an error while attempting to save project.\""
        #     logger.error(message)
        #     return HttpResponse(message, content_type='text/html')
        # else:
        #     this_response_data = r.json()
        #     logger.info(str(len(this_response_data)) + " projects saved")
        #     response_data.append(this_response_data)
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def projects_create(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkprojects/', data=data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def projects_delete(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    url = REST_SERVICES_URL+'projects/'+str(this_id)+'/'
    r = requests.request(method='DELETE', url=url, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def projectssites(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projectssites/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'projects/', headers=headers_auth_token)
    projects = json.dumps(r.json(), sort_keys=True)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'sites/', headers=headers_auth_token)
    sites = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data, 'projects': projects, 'sites': sites}
    return render_to_response('merlin/projects_sites.html', context_dict, context)


def projectssites_create(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))

    # validate that the submitted project-site doesn't already exist
    logger.info("VALIDATE Project-Site Add")
    this_projectsite = {'project': data.get('project'), 'site': data.get('site')}
    r = requests.get(REST_SERVICES_URL+'projectssites/', params=this_projectsite)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    response_data = r.json()
    logger.info("projects-sites count: " + str(response_data['count']))
    # if response count does not equal zero, then this project-site already exists in the database
    if response_data['count'] != 0:
        logger_message = "Validation Warning: Projects-Sites relation "
        logger_message += str(data.get('project')) + '-' + str(data.get('site')) + " count != 0"
        logger.warning(logger_message)
        message = "Projects-Sites relation " + str(response_data['results'][0]['project_name']) + "-"
        message += str(response_data['results'][0]['site_name']) + " already exists."
        message = json.dumps(message)
        return HttpResponse(message, content_type='text/html')

    data = json.dumps(data)
    r = requests.request(method='POST', url=REST_SERVICES_URL+'projectssites/', data=data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def projectssites_delete(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    url = REST_SERVICES_URL+'projectssites/'+str(this_id)+'/'
    r = requests.request(method='DELETE', url=url, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def cooperators(request):
    if not request.session.get('token'):
        return HttpResponseRedirect('/merlin/')
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    context = RequestContext(request)
    r = requests.request(method='GET', url=REST_SERVICES_URL+'cooperators/', headers=headers_auth_token)
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('merlin/cooperators.html', context_dict, context)


def cooperators_update(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    #data = request.body
    #r = requests.request(method='PUT', url=REST_SERVICES_URL+'bulkcooperators/', data=data, headers=headers_auth_token)
    #return HttpResponse(r, content_type='application/json')
    data = json.loads(request.body.decode('utf-8'))
    response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    # item_number = 0
    # for item in data:
    #     item_number += 1
    #     item_id = item["id"]
    #     item = json.dumps(item)
    #     logger.info("Item #" + str(item_number) + ": " + item)
    #     r = requests.request(method='PUT', url=REST_SERVICES_URL+'cooperators/', data=item, headers=headers)
    #     logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    #     if r.status_code != 200 or r.status_code != 201:
    #         message = "\"Encountered an error while attempting to save cooperator "
    #         message += item_id + ": " + str(r.status_code) + "\""
    #         logger.error(message)
    #         return HttpResponse(message, content_type='text/html')
    #     else:
    #         this_response_data = r.json()
    #         response_data.append(this_response_data)
    #         logger.info(str(len(this_response_data)) + " cooperators saved")
    item_number = 0
    for item in data:
        item_number += 1
        this_id = item.pop("id")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        url = REST_SERVICES_URL+'cooperators/'+str(this_id)+'/'
        r = requests.request(method='PUT', url=url, data=item, headers=headers)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        # if r.status_code != 200:# or r.status_code != 201:
        #     message = "\"Encountered an error while attempting to save cooperator.\""
        #     logger.error(message)
        #     return HttpResponse(message, content_type='text/html')
        # else:
        #     this_response_data = r.json()
        #     logger.info(str(len(this_response_data)) + " cooperators saved")
        #     response_data.append(this_response_data)
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def cooperators_create(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = request.body
    r = requests.request(method='POST', url=REST_SERVICES_URL+'bulkcooperators/', data=data, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def cooperators_delete(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    headers = dict(chain(headers_auth_token.items(), HEADERS_CONTENT_JSON.items()))
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    url = REST_SERVICES_URL+'cooperators/'+str(this_id)+'/'
    r = requests.request(method='DELETE', url=url, headers=headers)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


#login using Session Authentication
#@ensure_csrf_cookie
# This may not be the right way to do this.
# We need to decouple the client from the database and log in through services instead.
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
#                 return HttpResponseRedirect('/merlin/')
#             else:
#                 return HttpResponse("Your account is disabled.")
#
#         else:
#             logger.info("Invalid login details: {0}, {1}".format(username, password))
#             return HttpResponse("Invalid login details supplied.")
#
#     else:
#         return render_to_response('merlin/login.html', {}, context)


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
#             # logger.info("User:")
#             # logger.info(user)
#             # login(request, user)
#             request.session['username'] = r_dict['username']
#             global USER_AUTH
#             USER_AUTH = (username, password)
#             return HttpResponseRedirect('/merlin/')
#
#         else:
#             r_dict = json.loads(r.json())
#             resp = "<h1>" + str(r.status_code) + "</h1>"
#             resp += "<h3>" + r_dict['status'] + "</h3><p>" + r_dict['message'] + "</p>"
#             return HttpResponse(resp)
#
#     else:
#         return render_to_response('merlin/login.html', {}, context)


#login using Token Authentication
def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if not username:
            r = {"bad_details": True}
            logger.error("Error: Username not submitted.")
            return render_to_response('merlin/login.html', r, context)

        if not password:
            r = {"bad_details": True}
            logger.error("Error: Password not submitted.")
            return render_to_response('merlin/login.html', r, context)

        data = {"username": username, "password": password}

        r = requests.request(method='POST', url=REST_AUTH_URL+'login/', data=data, headers=HEADERS_CONTENT_FORM)
        logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
        response_data = r.json()

        if r.status_code == 200:
            # global USER_TOKEN
            # USER_TOKEN = eval(r.content)['auth_token']
            # global USER_AUTH
            # USER_AUTH = (username, password)
            token = eval(r.content)['auth_token']
            #logger.info(token)
            request.session['token'] = token
            #request.session['username'] = username
            #request.session['password'] = password

            params_dict = {"username": username}
            headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
            r = requests.request(
                method='GET', url=REST_SERVICES_URL+'users/', params=params_dict, headers=headers_auth_token)
            logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))

            if r.status_code == 200:
                user = r.json()[0]
                if user['is_active']:
                    request.session['username'] = user['username']
                    request.session['first_name'] = user['first_name']
                    request.session['last_name'] = user['last_name']
                    request.session['email'] = user['email']
                    request.session['is_staff'] = user['is_staff']
                    request.session['is_active'] = user['is_active']
                    request.session['bad_details'] = False
                    return HttpResponseRedirect('/merlin/')

                else:
                    r = {"disabled_account": True}
                    return render_to_response('merlin/login.html', r, context)

            else:
                logger.error("Error: Could not retrieve details of " + username + " from Mercury Services")
                resp = "<h1>" + str(r.status_code) + ": " + r.reason + "</h1>"
                resp += "<p>Login could not be performed. User account lacks required attributes.</p>"
                resp += "<p>Please contact the administrator.</p>"
                return HttpResponse(resp)

        elif (response_data["non_field_errors"]
                and response_data["non_field_errors"][0] == "Unable to login with provided credentials."):
            r = {"bad_details": True}
            logger.error("Error: " + response_data["non_field_errors"][0] + " Username: " + username + ".")
            return render_to_response('merlin/login.html', r, context)

        else:
            logger.error("Error: Could not log in " + username + " with Mercury Services.")
            resp = "<h1>" + str(r.status_code) + ": " + r.reason + "</h1>"
            resp += "<p>Login could not be performed. " + r.text + ". Please contact the administrator.</p>"
            return HttpResponse(resp)

    else:
        return render_to_response('merlin/login.html', {}, context)


#logout using Session Authentication
# def user_logout(request):
#     logout(request)
#     return HttpResponseRedirect('/merlin/')


# #logout using Basic Authentication
# def user_logout(request):
#     r = requests.request(method='POST', url=REST_SERVICES_URL+'/logout/')
#     if r.status_code == 204:
#         del request.session['username']
#         request.session.modified = True
#         global USER_AUTH
#         USER_AUTH = ('guest', 'guest')
#         return HttpResponseRedirect('/merlin/')
#
#     else:
#         return HttpResponse("<h1>Logout wasn't performed. Please contact the administrator.</h1>")


#logout using Token Authentication
def user_logout(request):
    headers_auth_token = {'Authorization': 'Token ' + request.session['token']}
    r = requests.request(method='POST', url=REST_AUTH_URL+'logout/', headers=headers_auth_token)
    logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))

    if r.status_code == 200:
        logger.info("Success: Logged out " + request.session['username'])
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
        return HttpResponseRedirect('/merlin/')

    else:
        response_data = r.json()
        if response_data["detail"]:
            logger_message = "Error: " + response_data["detail"] + " Could not log out "
            logger_message += request.session['username'] + " from Mercury Services"
            logger.error(logger_message)
        else:
            logger.error("Error: Could not log out " + request.session['username'] + " from Mercury Services")
        resp = "<h1>" + str(r.status_code) + ": " + r.reason + "</h1>"
        resp += "<p>Logout could not be performed. Please contact the administrator.</p>"
        return HttpResponse(resp)

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
#     return HttpResponseRedirect('/merlin/')


# @login_required
# def profile(request):
#     context = RequestContext(request)
#
#     context_dict = {'username': request.user.username,
#                     'fname': request.user.first_name, 'lname': request.user.last_name,
#                     'initials': request.user.userprofile.initials, 'phone': request.user.userprofile.phone, }
#
#     return render_to_response('merlin/profile.html', context_dict, context)


def about(request):
    context = RequestContext(request)
    return render_to_response('merlin/about.html', {}, context)


def index(request):
    context = RequestContext(request)
    context_dict = nav()
    return render_to_response('merlin/index.html', context_dict, context)


def nav():
    return {'navlist': ('cooperators', 'projects', 'sites', 'samples', 'bottles', 'acids',
                        'brominations', 'blankwaters', 'batchuploads', 'results', )}
