import logging
import json
import requests
from datetime import datetime
from collections import Counter
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse


########################################################################################################################
#
# copyright: 2015 WiM - USGS
# authors: Aaron Stephenson USGS WiM (Wisconsin Internet Mapping)
#
# In Django, a view is what takes a Web request and returns a Web response. The response can be many things, but most
# of the time it will be a Web page, a redirect, or a document.
#
# All these views are written as Function-Based Views (https://docs.djangoproject.com/en/1.8/topics/http/views/)
# because that is the paradigm used by most Django projects, especially tutorials for learning Django.
#
#
########################################################################################################################


logger = logging.getLogger(__name__)

# localhost dev
REST_SERVICES_URL = 'http://localhost:8000/mercuryservices/'
REST_AUTH_URL = 'http://localhost:8000/mercuryauth/'
# WIM5
# REST_SERVICES_URL = 'http://130.11.161.159/mercuryservices/'
# REST_AUTH_URL = 'http://130.11.161.159/mercuryauth/'
# WIM2
# REST_SERVICES_URL = 'http://130.11.161.247/mercuryservices/'
# REST_AUTH_URL = 'http://130.11.161.247/mercuryauth/'

HEAD_CONTENT_JSON = {'content-type': 'application/json'}
HEAD_CONTENT_FORM = {'content-type': 'application/x-www-form-urlencoded'}


SAMPLE_KEYS_UNIQUE = ["project", "site", "sample_date_time", "depth", "replicate", "medium_type"]
SAMPLE_KEYS = ["project", "site", "sample_date_time", "depth", "length", "received_date", "comment",
               "replicate", "medium_type", "lab_processing"]
SAMPLE_BOTTLE_KEYS = ["sample", "bottle", "filter_type", "volume_filtered",
                      "preservation_type", "preservation_volume", "preservation_acid", "preservation_comment"]
SAMPLE_ANALYSIS_KEYS = ["sample_bottle", "analysis", "constituent", "isotope_flag"]
BOTTLE_KEYS = ["bottle_prefix", "bottle_unique_name", "created_date", "description"]


##########
#
# Helper Functions
#
##########


def http_get(request, endpoint, params=None):
    if params:
        return requests.request(method='GET', url=REST_SERVICES_URL + endpoint + '/', params=params,
                                auth=(request.session['username'], request.session['password']))
    else:
        return requests.request(method='GET', url=REST_SERVICES_URL + endpoint + '/',
                                auth=(request.session['username'], request.session['password']))


def http_post(request, endpoint, data):
    return requests.request(method='POST', url=REST_SERVICES_URL + endpoint + '/', data=data, headers=HEAD_CONTENT_JSON,
                            auth=(request.session['username'], request.session['password']))


def http_put(request, endpoint, data):
    return requests.request(method='PUT', url=REST_SERVICES_URL + endpoint + '/', data=data, headers=HEAD_CONTENT_JSON,
                            auth=(request.session['username'], request.session['password']))


def http_delete(request, endpoint):
    return requests.request(method='DELETE', url=REST_SERVICES_URL + endpoint + '/',
                            auth=(request.session['username'], request.session['password']))


##########
#
# View Functions
#
##########


def sample_login(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
    context = RequestContext(request)
    projects = json.dumps(http_get(request, 'projects').json(), sort_keys=True)
    processings = json.dumps(http_get(request, 'processings').json(), sort_keys=True)
    mediums = json.dumps(http_get(request, 'mediums').json(), sort_keys=True)
    analyses = json.dumps(http_get(request, 'analyses').json(), sort_keys=True)
    filters = json.dumps(http_get(request, 'filters').json(), sort_keys=True)
    preservations = json.dumps(http_get(request, 'preservations').json(), sort_keys=True)
    isotope_flags = json.dumps(http_get(request, 'isotopeflags').json(), sort_keys=True)
    context_dict = {'projects': projects, 'processings': processings, 'mediums': mediums,
                    'analyses': analyses, 'filters': filters, 'preservations': preservations,
                    'isotope_flags': isotope_flags}
    return render_to_response('merlin/sample_login.html', context_dict, context)


def samples_create(request):
    logger.info("SAMPLE LOGIN CREATE")
    table = json.loads(request.body.decode('utf-8'))
    table_rows = len(table)
    logger.info("submitted table contains " + str(table_rows) + " rows")
    row_number = 0
    unique_sample_ids = []
    unique_sample_bottle_ids = []
    unique_bottles = []
    bottle_filter_volumes = []
    unique_sample_bottles = []
    unique_sample_analyses = []
    sample_data = []
    sample_bottle_data = []
    sample_analysis_data = []

    # PARSE ROWS AND VALIDATE #
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
        this_sample_id += str(row.get('sample_date_time'))+"|"+this_depth+"|"+str(row.get('replicate'))+"|"
        this_sample_id += str(row.get('medium_type'))
        logger.info("this sample id: " + this_sample_id)
        # if this sample ID is not already in the unique list, add it, otherwise skip the sample data for this row
        if this_sample_id not in unique_sample_ids:
            unique_sample_ids.append(this_sample_id)

            # validate this sample doesn't exist in the database, otherwise notify the user
            logger.info("VALIDATE Sample")
            sample_values_unique = [
                row.get('project'), row.get('site'), row.get('sample_date_time'),
                row.get('depth'), row.get('replicate'), row.get('medium_type')
            ]
            this_sample_unique = dict(zip(SAMPLE_KEYS_UNIQUE, sample_values_unique))
            logger.info(str(this_sample_unique))
            # could not get requests.request() to work properly here, so using requests.get() instead
            # r = http_get(request, 'samples', this_sample_unique)
            r = requests.get(REST_SERVICES_URL+'samples/', params=this_sample_unique,
                            auth=(request.session['username'], request.session['password']))
            logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
            response_data = r.json()
            logger.info("count: " + str(response_data['count']))
            # if response count does not equal zero, then this sample already exists in the database
            if response_data['count'] != 0:
                logger.warning("Validation Warning: " + str(sample_values_unique) + " count != 0")
                project_name = http_get(request, 'projects/'+str(row.get('project'))).json()['results'][0]['name']
                site_name = http_get(request, 'sites/' + row.get('site')).json()['results'][0]['name']
                message = "\"Error in row " + str(row_number) + ": This Sample already exists in the database: "
                message += project_name + "|" + site_name + "|" + str(row.get('sample_date_time')) + "|"
                message += str(row.get('depth')) + "|" + str(row.get('replicate')) + "|"
                message += str(row.get('medium_type')) + "\""
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
        r = http_get(request, 'samplebottles', {"bottle": this_bottle})
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        response_data = r.json()
        logger.info("count: " + str(response_data['count']))
        # if response count does not equal zero, then this bottle is already used by a sample in the database
        if response_data['count'] != 0:
            logger.warning("Validation Warning: " + str(this_bottle) + " count != 0")
            bottle_name = response_data['results'][0]['bottle_string']
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
        this_analysis = this_sample_id+"|"+str(row.get('analysis_type'))+"|"+str(row.get('isotope_flag'))
        logger.info(this_analysis)
        if this_analysis not in unique_sample_analyses:
            logger.info(this_analysis + " is unique")
            unique_sample_analyses.append(this_analysis)
        else:
            logger.warning("Validation Warning: " + this_analysis + " is not unique")
            project_name = http_get(request, 'projects', {'id': row.get('project')}).json()['results'][0]['name']
            site_name = http_get(request, 'sites', {'id': row.get('site')}).json()['results'][0]['name']
            analysis_name = http_get(request, 'analyses', {'id': row.get('analysis_type')}).json()[0]['analysis']
            isotope_flag = http_get(request, 'isotopeflags', {'id': row.get('isotope_flag')}).json()[0]['isotope_flag']
            message = "\"Error in row " + str(row_number) + ": This Analysis (" + analysis_name + ")"
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
                    r = http_get(request, 'bottles', {"id": this_bottle_filter_volume[0]})
                    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
                    response_data = r.json()
                    bottle_unique_name = response_data['results'][0]['bottle_unique_name']
                    message = "\"Error in row " + str(row_number)
                    message += ": This Filter Vol (" + str(this_bottle_filter_volume[1]) + ")"
                    message += " does not match a previous Filter Vol (" + str(bottle_filter_volume[1]) + ")"
                    message += " for this Container: " + str(bottle_unique_name) + "\""
                    logger.error(message)
                    return HttpResponse(message, content_type='text/html')

        # grab the data that uniquely identifies each sample bottle
        this_sample_bottle_id = this_sample_id+"|"+str(row.get('bottle'))
        logger.info("this sample bottle id: " + this_sample_bottle_id)

        # if this sample bottle ID is not already in the unique list, add it,
        # otherwise skip the sample bottle data for this row
        if this_sample_bottle_id not in unique_sample_bottle_ids:
            unique_sample_bottle_ids.append(this_sample_bottle_id)

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

        # look up constituents that are related to this analysis
        r = http_get(request, 'constituents', {"analysis": row.get('analysis_type')})
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        constituents = r.json()
        # create result objects (one for each constituent) for the analysis type within this row
        for constituent in constituents:
            sample_analysis_values = [
                str(row.get('bottle')), row.get('analysis_type'), constituent['id'], row.get('isotope_flag')]
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
            r = http_get(request, 'bottles', {"id": unique_bottle})
            logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
            response_data = r.json()
            bottle_unique_name = response_data['results'][0]['bottle_unique_name']
            message = "\"Error in row " + str(row_number) + ": This Container appears in more than one sample: "
            message += bottle_unique_name + "\""
            logger.error(message)
            return HttpResponse(message, content_type='text/html')
        else:
            logger.info(str(unique_bottle) + " is only used in one sample")

    # SAVING #
    # save samples first and then get their database IDs, which are required for saving the sample bottles afterward

    # SAVE SAMPLES #
    # send the samples to the database
    logger.info("SAVE Samples")
    sample_data = json.dumps(sample_data)
    logger.info(sample_data)
    r = http_post(request, 'bulksamples', sample_data)
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
        combo_id += str(item.get('depth')) + "|" +str(item.get('replicate')) + "|" +str(item.get('medium_type'))
        sample_id = {'combo_id': combo_id, 'db_id': item.get('id')}
        logger.info("item " + str(item_number) + ": " + str(sample_id))
        sample_ids.append(sample_id)

    # SAVE SAMPLE BOTTLES #
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
                r = http_delete(request, 'samples/'+str(sample_id['db_id']))
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
    r = http_post(request, 'bulksamplebottles', sample_bottle_data)
    logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
    if r.status_code != 201:
        failed_create_status_code = r.status_code
        logger.warning("Could not save sample bottles!")
        logger.warning("Deleting samples that were just saved.")
        for sample_id in sample_ids:
            r = http_delete(request, 'samples/'+str(sample_id['db_id']))
            if r.status_code != 204:
                message = "\"Error: Can save samples, but cannot save sample bottles."
                message += " Encountered problem reversing saved samples"
                message += " (specifically sample ID " + str(sample_id['db_id']) + ")."
                message += " Please contact the administrator.\""
                logger.error(message)
                return HttpResponse(message, content_type='text/html')
        message = "\"Error " + str(failed_create_status_code) + ": " + r.reason + "."
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

    # SAVE SAMPLE ANALYSES (placeholder records in Results table) #
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
                r = http_delete(request, 'samplebottles/'+this_id)
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
                r = http_delete(request, 'samples/'+this_id)
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
    r = http_post(request, 'bulkresults', sample_analysis_data)
    logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
    if r.status_code != 201:
        failed_create_status_code = r.status_code
        logger.warning("Could not save sample analyses!")
        logger.warning("Deleting sample bottles that were just saved.")
        for sample_bottle_id in sample_bottle_ids:
            this_id = str(sample_bottle_id['db_id'])
            r = http_delete(request, 'samplebottles/'+this_id)
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
            r = http_delete(request, 'samples/'+this_id)
            if r.status_code != 204:
                message = "\"Error: Can save samples and sample bottles, but cannot save analyses."
                message += " Encountered problem reversing saved samples"
                message += " (specifically sample ID " + str(sample_id['db_id']) + ")."
                message += " Please contact the administrator.\""
                logger.error(message)
                return HttpResponse(message, content_type='text/html')
        message = "\"Error " + str(failed_create_status_code) + ": " + r.reason + "."
        message += "\"Can save samples and sample bottles, but cannot save analyses."
        message += " Please contact the administrator.\""
        logger.error(message)
        return HttpResponse(message, content_type='text/html')
    logger.info(str(len(r.json())) + " sample analyses saved")
    # send the response (data & messages) back to the user interface
    return HttpResponse(r, content_type='application/json')


def samples_search(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
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
        if params['analysis']:
            params_dict["analysis"] = str(params['analysis']).strip('[]')
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

        r = http_get(request, 'fullresults', params_dict)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        if params['format'] == 'csv':
            response = HttpResponse(r, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="samples.csv"'
            response.write(r.content)
            return response
        else:
            r_dict = r.json()
            logger.info("search results count: " + str(r_dict['count']))
            return HttpResponse(json.dumps(r_dict), content_type='application/json')

    else:  # request.method == 'GET'
        projects = json.dumps(http_get(request, 'projects').json(), sort_keys=True)
        processings = json.dumps(http_get(request, 'processings').json(), sort_keys=True)
        analyses = json.dumps(http_get(request, 'analyses').json(), sort_keys=True)
        constituents = json.dumps(http_get(request, 'constituents').json(), sort_keys=True)
        mediums = json.dumps(http_get(request, 'mediums').json(), sort_keys=True)
        filters = json.dumps(http_get(request, 'filters').json(), sort_keys=True)
        preservations = json.dumps(http_get(request, 'preservations').json(), sort_keys=True)
        isotope_flags = json.dumps(http_get(request, 'isotopeflags').json(), sort_keys=True)
        context_dict = {'projects': projects, 'processings': processings,
                        'analyses': analyses, 'constituents': constituents, 'mediums': mediums, 'filters': filters,
                        'preservations': preservations, 'isotope_flags': isotope_flags}
        return render_to_response('merlin/sample_search.html', context_dict, context)


def samples_update(request):
    logger.info("SAMPLE LOGIN UPDATE")
    table = json.loads(request.body.decode('utf-8'))
    table_rows = len(table)
    logger.info("submitted table contains " + str(table_rows) + " rows")
    row_number = 0
    unique_sample_ids = []
    unique_sample_bottle_ids = []
    sample_data = []
    sample_bottle_data = []
    sample_analysis_data = []

    # PARSE ROWS AND VALIDATE #
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
            r = http_get(request, 'samples', {'id': this_sample_id})
            logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
            response_data = r.json()
            logger.info("count: " + str(response_data['count']))
            # if response count equals zero, then this sample does not exist in the database
            if response_data['count'] == 0:
                # logger.warning("Validation Warning: " + str(sample_values_unique) + " count == 0")
                logger.warning("Validation Warning: " + str(this_sample_id) + " count == 0")
                project_name = http_get(request, 'projects/'+str(row.get('project'))).json()['results'][0]['name']
                site_name = http_get(request, 'sites/'+str(row.get('site'))).json()['results'][0]['name']
                message = "\"Error in row " + str(row_number) + ":"
                message += " Cannot save because this Sample does not exist in the database: "
                message += project_name + "|" + site_name + "|" + str(row.get('sample_date_time')) + "|"
                message += str(row.get('depth')) + "|" + str(row.get('replicate')) + "|"
                message += str(row.get('medium_type')) + "."
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

        # grab the data that uniquely identifies each sample bottle
        this_sample_bottle_id = str(this_sample_id)+"|"+str(row.get('sample_bottle.id'))+"|"+str(row.get('bottle'))
        logger.info("this sample bottle id: " + this_sample_bottle_id)

        # if this sample bottle ID is not already in the unique list, add it,
        # otherwise skip the sample bottle data for this row
        if this_sample_bottle_id not in unique_sample_bottle_ids:
            unique_sample_bottle_ids.append(this_sample_bottle_id)

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
            row.get('id'), row.get('sample_bottle.id'), row.get('analysis_type'), row.get('constituent_type'),
            row.get('isotope_flag'), row.get('sample_bottle.sample.id'), row.get('bottle')]
        this_sample_analysis_keys = ["id", "sample_bottle", "analysis", "constituent", "isotope_flag",
                                     "temp_sample", "temp_bottle"]
        this_sample_analysis = dict(zip(this_sample_analysis_keys, sample_analysis_values))
        logger.info("Creating result: " + str(this_sample_analysis))
        # add this new sample bottle object to the list
        sample_analysis_data.append(this_sample_analysis)

    # SAVING
    # save samples first and then get their database IDs, which are required for saving the sample bottles afterward

    # SAVE SAMPLES #
    # send the samples to the database
    logger.info("SAVE Samples in Search Save")
    # sample_data = json.dumps(sample_data)
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
        r = http_put(request, 'samples/'+str(this_id), item)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        logger.info("1 samples saved")
        sample_response_data.append(r.json())
    logger.info(sample_response_data)

    # SAVE SAMPLE BOTTLES #
    # update the sample bottles with the database IDs, rather than the combo IDs
    logger.info("SAVE Sample Bottles in Search Save")
    # send the sample bottles to the database
    # sample_bottle_data = json.dumps(sample_bottle_data)
    logger.info(str(sample_bottle_data))
    sample_bottle_response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    item_number = 0
    for item in sample_bottle_data:
        item_number += 1
        this_id = item.pop("id")
        this_bottle = item.get("bottle")
        this_sample = item.get("sample")
        item = json.dumps(item)
        logger.info("Item #" + str(item_number) + ": " + item)
        # if id is null, that means it might be a new record, otherwise it is an update to an existing record
        if not this_id:
            # this is might be a new record
            logger.info("VALIDATE Sample Bottle in Search Save")
            # validate if this bottle + sample combo exists, if not, it might be a new record, or it is invalid,
            # otherwise this is an update to an existing record, but the sample bottle id is null
            # because there is a new related sample analysis being submitted
            r = http_get(request, 'samplebottles', {"bottle": this_bottle, "sample_id": this_sample})
            logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
            response_data = r.json()
            logger.info("count: " + str(response_data['count']))
            # if response count equals zero, then this sample bottle does not exist in the database,
            # so check if the bottle has been used before; if not, create a new sample bottle, otherwise error
            if response_data['count'] == 0:
                # validate that this bottle has not been used in any sample before
                r = http_get(request, 'samplebottles', {"bottle": this_bottle})
                logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
                response_data = r.json()
                logger.info("count: " + str(response_data['count']))
                # if response count equals zero, then this bottle has not been used in any sample bottle before
                if response_data['count'] == 0:
                    # this bottle has not been used in another sample, so we can use it for this sample
                    r = http_post(request, 'samplebottles', item)
                    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
                    logger.info("1 sample bottles created")
                    sample_bottle_response_data.append(r.json())
                else:
                    # this bottle has been used in another sample, so it cannot be used for this sample
                    message = "\"Error."
                    r = http_get(request, 'bottles/'+str(this_bottle))
                    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
                    response_data = r.json()
                    message += " Unable to save sample bottle."
                    message += " Bottle Code " + response_data["results"][0]["bottle_unique_name"]
                    message += " is used in an existing sample bottle.\""
                    logger.error(message)
                    return HttpResponse(message, content_type='text/html')
            else:
                # the sample bottle does exist, so grab the id and update the record with the submitted data
                this_id = response_data["results"][0]["id"]
                r = http_put(request, 'samplebottles/'+str(this_id), item)
                logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
                logger.info("1 sample bottles saved")
                sample_bottle_response_data.append(r.json())

        else:
            # this is an update to an existing record
            r = http_put(request, 'samplebottles/' + str(this_id), item)
            logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
            logger.info("1 sample bottles saved")
            sample_bottle_response_data.append(r.json())
    logger.info(sample_bottle_response_data)

    # SAVE SAMPLE ANALYSES (placeholder records in Results table) #
    # update the sample analyses with the sample bottle IDs, rather than the bottle IDs
    logger.info("SAVE Sample Analyses in Search Save")
    # send the sample analyses to the database
    # sample_analysis_data = json.dumps(sample_analysis_data)
    logger.info(str(sample_analysis_data))
    sample_analysis_response_data = []
    # using a loop to send data to the single PUT endpoint instead of just using the bulk PUT endpoint
    # because the bulk PUT response time has been over 30 seconds, sometimes several minutes
    item_number = 0
    for item in sample_analysis_data:
        item_number += 1
        this_id = item.pop("id")
        # also pop the temp sample and temp bottle, which removes those values from the object
        this_sample = item.pop("temp_sample")
        this_bottle = item.pop("temp_bottle")
        logger.info("Item #" + str(item_number) + ": " + str(item))
        # if id is null, that means it might be a new record, otherwise it is an update to an existing record
        if not this_id:
            # validate if this bottle + sample combo exists, which means this is an update to an existing record,
            # but the sample bottle id is null because there is a new related sample analysis being submitted
            logger.info("VALIDATE Sample Analysis in Search Save")
            # first grab the sample bottle id
            r = http_get(request, 'samplebottles', {"bottle": this_bottle, "sample_id": this_sample})
            logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
            response_data = r.json()
            logger.info("count: " + str(response_data['count']))
            # if there is at least one record in the response, the sample bottle already exists, so grab the id,
            # otherwise,  matching sample bottle doesn't exist, which is a problem.
            if not response_data['count'] == 0:
                # a sample bottle was found
                this_sample_bottle = response_data["results"][0]["id"]
                logger.info("found this sample bottle: " + str(this_sample_bottle))
                item['sample_bottle'] = this_sample_bottle
                param_dict = {"sample_bottle": item.get("sample_bottle"), "analysis": item.get("analysis"),
                              "constituent": item.get("constituent"), "isotope_flag": item.get("isotope_flag")}
                r = http_get(request, 'results', param_dict)
                logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
                response_data = r.json()
                logger.info("count: " + str(response_data['count']))
                # if response count equals zero, then this sample analysis does not exist in the database, so create one
                item = json.dumps(item)
                if response_data['count'] == 0:
                    r = http_post(request, 'results', item)
                    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
                    this_response_data = r.json()
                    logger.info("1 sample analyses created")
                    sample_analysis_response_data.append(this_response_data)
                # otherwise the sample analysis does exist, so grab the id and update the record with the submitted data
                else:
                    this_id = response_data["results"][0]["id"]
                    r = http_put(request, 'results/'+str(this_id), item)
                    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
                    this_response_data = r.json()
                    logger.info("1 sample analyses saved")
                    sample_analysis_response_data.append(this_response_data)
            else:
                message = "\"Error."
                r = http_get(request, 'bottles/'+str(this_bottle))
                logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
                response_data = r.json()
                message += " Unable to save sample analysis; could not find a sample bottle for this sample analysis."
                message += " Tried finding a sample bottle with Sample ID " + str(this_sample)
                message += " and Bottle Code " + response_data["results"][0]["bottle_unique_name"] + "."
                message += " Please contact the administrator.\""
                logger.error(message)
                return HttpResponse(message, content_type='text/html')
        else:
            item = json.dumps(item)
            r = http_put(request, 'results/'+str(this_id), item)
            logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
            this_response_data = r.json()
            logger.info("1 sample analyses saved")
            sample_analysis_response_data.append(this_response_data)
    sample_analysis_response_data = json.dumps(sample_analysis_response_data)
    # send the response (data & messages) back to the user interface
    return HttpResponse(sample_analysis_response_data, content_type='application/json')


def results_search(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
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

        r = http_get(request, 'fullresults', params_dict)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        if params['format'] == 'csv':
            response = HttpResponse(r, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="results.csv"'
            response.write(r.content)
            return response
        else:
            r_dict = r.json()
            logger.info("search results count: " + str(r_dict['count']))
            return HttpResponse(json.dumps(r_dict), content_type='application/json')

    else:  # request.method == 'GET'
        projects = json.dumps(http_get(request, 'projects').json(), sort_keys=True)
        constituents = json.dumps(http_get(request, 'constituents').json(), sort_keys=True)
        context_dict = {'projects': projects, 'constituents': constituents}
        return render_to_response('merlin/result_search.html', context_dict, context)


def results_count_nawqa(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
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

        r = http_get(request, 'resultcountnawqa', params_dict)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search result count nawqa report count: " + str(r_dict['count']))
        return HttpResponse(json.dumps(r_dict), content_type='application/json')

    else:  # request.method == 'GET'
        data = json.dumps(http_get(request, 'resultcountnawqa').json(), sort_keys=True)
        context_dict = {'data': data}
        return render_to_response('merlin/results_count_nawqa.html', context_dict, context)


def results_count_projects(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
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

        r = http_get(request, 'resultcountprojects', params_dict)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search results count project report count: " + str(r_dict['count']))
        return HttpResponse(json.dumps(r_dict), content_type='application/json')

    else:  # request.method == 'GET'
        data = json.dumps(http_get(request, 'resultcountprojects').json(), sort_keys=True)
        context_dict = {'data': data}
        return render_to_response('merlin/results_count_projects.html', context_dict, context)


def samples_nwis_report(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
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

        r = http_get(request, 'reportsamplesnwis', params_dict)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search samples nwis report count: " + str(r_dict['count']))
        return HttpResponse(json.dumps(r_dict), content_type='application/json')

    else:  # request.method == 'GET'
        projects = json.dumps(http_get(request, 'projects').json(), sort_keys=True)
        context_dict = {'projects': projects}

        return render_to_response('merlin/samples_nwis.html', context_dict, context)


def results_nwis_report(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
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

        r = http_get(request, 'reportresultsnwis', params_dict)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search results nwis report count: " + str(r_dict['count']))
        return HttpResponse(json.dumps(r_dict), content_type='application/json')

    else:  # request.method == 'GET'
        projects = json.dumps(http_get(request, 'projects').json(), sort_keys=True)
        context_dict = {'projects': projects}
        return render_to_response('merlin/results_nwis.html', context_dict, context)


def results_cooperator_report(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
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

        r = http_get(request, 'reportresultscooperator', params_dict)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search results cooperator report count: " + str(r_dict['count']))
        return HttpResponse(json.dumps(r_dict), content_type='application/json')

    else:  # request.method == 'GET'
        projects = json.dumps(http_get(request, 'projects').json(), sort_keys=True)
        cooperators = json.dumps(http_get(request, 'cooperators').json(), sort_keys=True)
        context_dict = {'projects': projects, 'cooperators': cooperators}
        return render_to_response('merlin/results_cooperator.html', context_dict, context)


def bottles(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
    context = RequestContext(request)
    bottles = json.dumps(http_get(request, 'bottles').json(), sort_keys=True)
    prefixes = json.dumps(http_get(request, 'bottleprefixes').json(), sort_keys=True)
    bottletypes = json.dumps(http_get(request, 'bottletypes').json(), sort_keys=True)
    context_dict = {'bottles': bottles, 'prefixes': prefixes, 'bottletypes': bottletypes}
    return render_to_response('merlin/bottles.html', context_dict, context)


def bottles_update(request):
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
        r = http_put(request, 'bottles/'+str(this_id), item)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def bottle_prefixes_update(request):
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
        r = http_put(request, 'bottleprefixes/' + str(this_id), item)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def bottle_prefixes_create(request):
    data = json.loads(request.body.decode('utf-8'))

    # validate that the submitted bottle prefix doesn't already exist
    logger.info("VALIDATE Bottle Prefix Add")
    r = http_get(request, 'bottleprefixes', {'bottle_prefix': data.get('bottle_prefix')})
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    response_data = r.json()
    logger.info("bottle prefix count: " + str(response_data['count']))
    # if response count does not equal zero, then this sample already exists in the database
    if response_data['count'] != 0:
        logger.warning("Validation Warning: " + data.get('bottle_prefix') + " count != 0")
        message = "This Bottle Prefix already exists in the database: "
        return HttpResponse(message, content_type='text/html')

    # SAVE Bottle Prefixes #
    # send the bottle prefixes to the database
    r = http_post(request, 'bulkbottleprefixes', json.dumps(data))
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
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    r = http_delete(request, 'bottleprefixes/'+str(this_id))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def bottle_prefixes_range_create(request):
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
        r = http_get(request, 'bottleprefixes', {'bottle_prefix': this_bottle_prefix})
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

    # SAVE Bottle Prefixes #
    # send the bottle prefixes to the database
    r = http_post(request, 'bulkbottleprefixes', json.dumps(new_bottle_prefixes))
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
        this_bottle_unique_name = item.get('bottle_unique_name')
        r = http_get(request, 'bottles', {'bottle_unique_name': this_bottle_unique_name})
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        response_data = r.json()
        logger.info("bottles count: " + str(response_data['count']))
        # if response count does not equal zero, then this sample already exists in the database
        if response_data['count'] != 0:
            all_unique_bottle_names = False
            logger.warning("Validation Warning: " + this_bottle_unique_name + " count != 0")
            this_message = "Row " + str(item_number) + ": " + this_bottle_unique_name + ","
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
        r = http_get(request, 'bottleprefixes', {'bottle_prefix': this_bottle_prefix})
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

    # SAVE Bottles #
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
    r = http_post(request, 'bulkbottles', bottle_data)
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
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    r = http_delete(request, 'bottles/'+str(this_id))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def brominations(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
    context = RequestContext(request)
    data = json.dumps(http_get(request, 'brominations').json(), sort_keys=True)
    samples = json.dumps(http_get(request, 'samplebottlebrominations').json(), sort_keys=True)
    context_dict = {'data': data, 'samples': samples}
    return render_to_response('merlin/brominations.html', context_dict, context)


def brominations_update(request):
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
        r = http_put(request, 'brominations/'+str(this_id), item)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def brominations_create(request):
    data = request.body
    r = http_post(request, 'bulkbrominations', data)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def brominations_delete(request):
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    r = http_delete(request, 'brominations/'+str(this_id))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def samplebottlebrominations_create(request):
    data = json.loads(request.body.decode('utf-8'))
    unique_sample_bottles = []
    all_valid_sample_bottles_thg = True
    all_valid_sample_bottles_unique = True
    message_not_thg = "These Sample Bottles are not for UTHG or FTHG: "
    message_not_unique = "These Sample Bottles are not unique within this list: "

    # validate that the submitted sample bottles have samples with constituents of UTHG or FTHG
    logger.info("VALIDATE Sample Bottles Brominations Constituents")
    item_number = 0
    for item in data:
        item_number += 1
        r = http_get(request, 'samplebottles', {'id': item.get('sample_bottle'), 'constituent': '39,27'})
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        response_data = r.json()
        logger.info("bottles count: " + str(response_data['count']))
        # if response count does not equal one, then this sample bottle is not valid
        if response_data['count'] != 1:
            all_valid_sample_bottles_thg = False
            logger.warning("Validation Warning: " + str(item.get('sample_bottle')) + " count != 1")
            this_message = "Row " + str(item_number) + ","
            message_not_thg = message_not_thg + " " + this_message
    if not all_valid_sample_bottles_thg:
        message = json.dumps(message_not_thg)
        logger.warning("Validation Warning: " + message)
        return HttpResponse(message, content_type='text/html')

    # validate that there are no duplicates in the submission
    logger.info("VALIDATE Sample Bottles Brominations Uniqueness")
    item_number = 0
    for item in data:
        item_number += 1
        sample_bottle = item.get('sample_bottle')
        if sample_bottle not in unique_sample_bottles:
            unique_sample_bottles.append(sample_bottle)
        else:
            all_valid_sample_bottles_unique = False
            logger.warning("Validation Warning: " + str(sample_bottle) + " not unique in list")
            this_message = "Row " + str(item_number) + ","
            message_not_unique = message_not_unique + " " + this_message
    if not all_valid_sample_bottles_unique:
        message = json.dumps(message_not_unique)
        logger.warning("Validation Warning: " + message)
        return HttpResponse(message, content_type='text/html')

    # SAVE Sample Bottle Brominations #
    # send the sample bottle brominations to the database
    logger.info("SAVE Sample Bottle Brominations")
    table = json.loads(request.body.decode('utf-8'))
    brom_data = []
    for row in table:
        this_brom = {'bromination': row.get('bromination'), 'sample_bottle': row.get('sample_bottle'),
                     'bromination_event': row.get('bromination_event'),
                     'bromination_volume': row.get('bromination_volume'), 'created_date': row.get('created_date')}
        brom_data.append(this_brom)
    logger.info(brom_data)
    logger.info(json.dumps(brom_data))
    r = http_post(request, 'bulksamplebottlebrominations', json.dumps(brom_data))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    if r.status_code != 201:
        if r.status_code == 400:
            message = "\"Error " + str(r.status_code) + ": " + r.reason + ". Cannot save sample bottle brominations."
            message += " Please remove duplicate records before submitting.\""
            logger.error(message)
            return HttpResponse(message, content_type='text/html')
        else:
            message = "\"Error " + str(r.status_code) + ": " + r.reason + ". Cannot save sample bottle brominations."
            message += " Please contact the administrator.\""
            logger.error(message)
            return HttpResponse(message, content_type='text/html')
    else:
        logger.info("sample bottle brominations saved")
        return HttpResponse(r, content_type='application/json')


def samplebottlebrominations_search(request):

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

        r = http_get(request, 'samplebottlebrominations', params_dict)
        logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
        r_dict = r.json()
        logger.info("search sample bottles brominations count: " + str(r_dict['count']))
        return HttpResponse(json.dumps(r_dict), content_type='application/json')


def samplebottlebrominations_delete(request):
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    r = http_delete(request, 'samplebottlebrominations/'+str(this_id))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def blankwaters(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
    context = RequestContext(request)
    r = http_get(request, 'blankwaters')
    data = json.dumps(r.json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('merlin/blankwaters.html', context_dict, context)


def blankwaters_update(request):
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
        r = http_put(request, 'blankwaters/'+str(this_id), item)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def blankwaters_create(request):
    data = request.body
    r = http_post(request, 'bulkblankwaters', data)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def blankwaters_delete(request):
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    r = http_delete(request, 'blankwaters/' + str(this_id))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def acids(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
    context = RequestContext(request)
    data = json.dumps(http_get(request, 'acids').json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('merlin/acids.html', context_dict, context)


def acids_update(request):
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
        r = http_put(request, 'acids/'+str(this_id), item)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def acids_create(request):
    data = request.body
    r = http_post(request, 'bulkacids', data)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def acids_delete(request):
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    r = http_delete(request, 'acids/'+str(this_id))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def sites(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
    context = RequestContext(request)
    data = json.dumps(http_get(request, 'sites').json(), sort_keys=True)
    projects = json.dumps(http_get(request, 'projects').json(), sort_keys=True)
    context_dict = {'data': data, 'projects': projects}
    return render_to_response('merlin/sites.html', context_dict, context)


def sites_update(request):
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
        r = http_put(request, 'sites/'+str(this_id), item)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def sites_create(request):
    data = request.body
    r = http_post(request, 'bulksites', data)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def sites_delete(request):
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    r = http_delete(request, 'sites/'+str(this_id))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def projects(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
    context = RequestContext(request)
    data = json.dumps(http_get(request, 'projects').json(), sort_keys=True)
    cooperators = json.dumps(http_get(request, 'cooperators').json(), sort_keys=True)
    context_dict = {'data': data, 'cooperators': cooperators}
    return render_to_response('merlin/projects.html', context_dict, context)


def projects_update(request):
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
        r = http_put(request, 'projects/'+str(this_id), item)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def projects_create(request):
    data = request.body
    r = http_post(request, 'bulkprojects', data)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def projects_delete(request):
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    r = http_delete(request, 'projects/'+str(this_id))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def projectssites(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
    context = RequestContext(request)
    data = json.dumps(http_get(request, 'projectssites').json(), sort_keys=True)
    projects = json.dumps(http_get(request, 'projects').json(), sort_keys=True)
    sites = json.dumps(http_get(request, 'sites').json(), sort_keys=True)
    context_dict = {'data': data, 'projects': projects, 'sites': sites}
    return render_to_response('merlin/projects_sites.html', context_dict, context)


def projectssites_create(request):
    data = json.loads(request.body.decode('utf-8'))
    # validate that the submitted project-site doesn't already exist
    logger.info("VALIDATE Project-Site Add")
    r = http_get(request, 'projectssites', {'project': data.get('project'), 'site': data.get('site')})
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
    r = http_post(request, 'projectssites', json.dumps(data))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def projectssites_delete(request):
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    r = http_delete(request, 'projectssites/'+str(this_id))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


def cooperators(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
    context = RequestContext(request)
    data = json.dumps(http_get(request, 'cooperators').json(), sort_keys=True)
    context_dict = {'data': data}
    return render_to_response('merlin/cooperators.html', context_dict, context)


def cooperators_update(request):
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
        r = http_put(request, 'cooperators/'+str(this_id), item)
        logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
        this_response_data = r.json()
        response_data.append(this_response_data)
    response_data = json.dumps(response_data)
    return HttpResponse(response_data, content_type='application/json')


def cooperators_create(request):
    data = request.body
    r = http_post(request, 'bulkcooperators', data)
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r, content_type='application/json')


def cooperators_delete(request):
    data = json.loads(request.body.decode('utf-8'))
    this_id = data.pop("id")
    r = http_delete(request, 'cooperators/'+str(this_id))
    logger.info(r.request.method + " " + r.request.url + "  " + r.reason + " " + str(r.status_code))
    return HttpResponse(r)


# login using Basic Authentication
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

        r = requests.request(method='POST', url=REST_SERVICES_URL + 'auth/', auth=(username, password))
        logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
        response_data = r.json()

        if r.status_code == 200:
            r = requests.request(method='GET', url=REST_SERVICES_URL + 'users/', params={'username': username},
                                 auth=(username, password))
            logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
            if r.status_code == 200:
                user = r.json()[0]
                if user['is_active']:
                    request.session['username'] = username
                    request.session['password'] = password
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

        elif (response_data["detail"] == "Invalid username/password."):
            r = {"bad_details": True}
            logger.error("Error: " + response_data["detail"] + " Username: " + username + ".")
            return render_to_response('merlin/login.html', r, context)

        elif (response_data["non_field_errors"]):
            if (response_data["non_field_errors"][0] == "Unable to login with provided credentials."):
                r = {"bad_details": True}
                logger.error("Error: " + response_data["non_field_errors"][0] + " Username: " + username + ".")
                return render_to_response('merlin/login.html', r, context)
            else:
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


# logout using Basic Authentication
def user_logout(request):
    if not request.session.get('username'):
        return HttpResponseRedirect('/merlin/')
    logger.info("Success: Logged out " + request.session['username'])
    del request.session['username']
    del request.session['password']
    del request.session['first_name']
    del request.session['last_name']
    del request.session['email']
    del request.session['is_staff']
    del request.session['is_active']
    request.session.modified = True
    return HttpResponseRedirect('/merlin/')

    # r = requests.request(method='POST', url=REST_AUTH_URL+'logout/',
    #                      auth=(request.session['username'], request.session['password']))
    # logger.info(r.request.method + " " + r.request.url + " " + r.reason + " " + str(r.status_code))
    #
    # if r.status_code == 200:
    #     logger.info("Success: Logged out " + request.session['username'])
    #     del request.session['username']
    #     del request.session['password']
    #     del request.session['first_name']
    #     del request.session['last_name']
    #     del request.session['email']
    #     del request.session['is_staff']
    #     del request.session['is_active']
    #     request.session.modified = True
    #     return HttpResponseRedirect('/merlin/')
    # else:
    #     response_data = r.json()
    #     if response_data["detail"]:
    #         logger_message = "Error: " + response_data["detail"] + " Could not log out "
    #         logger_message += request.session['username'] + " from Mercury Services"
    #         logger.error(logger_message)
    #     else:
    #         logger.error("Error: Could not log out " + request.session['username'] + " from Mercury Services")
    #     resp = "<h1>" + str(r.status_code) + ": " + r.reason + "</h1>"
    #     resp += "<p>Logout could not be performed. Please contact the administrator.</p>"
    #     return HttpResponse(resp)


def about(request):
    context = RequestContext(request)
    return render_to_response('merlin/about.html', {}, context)


def index(request):
    context = RequestContext(request)
    return render_to_response('merlin/index.html', {}, context)
