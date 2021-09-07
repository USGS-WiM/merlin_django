import json
import time
import math
import decimal
from numbers import Number
from datetime import datetime as dt
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponse
from django.db.models.base import ObjectDoesNotExist
from rest_framework import views
from merlinservices.models import *


# batch_upload_save: validation
class BatchUpload(views.APIView):
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        status = []
        data = []
        try:
            data = json.loads(request.body.decode('utf-8'))
            for row in data:
                # validate sample id/bottle bar code
                is_valid, message, bottle_id, sample, volume_filtered = validate_bottle_bar_code(row)
                if not is_valid:
                    status.append({"message": message, "success": "false"})
                    continue

                # get bottle_unique_name
                bottle_unique_name = row["bottle_unique_name"]

                # validate constituent type
                is_valid, message, constituent_id = validate_constituent_type(row)
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue
                # validate analysis method type
                is_valid, message, analysis_method_id = validate_analysis_method(constituent_id, row)
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue
                is_valid, message, isotope_flag_id = validate_isotope_flag(row)
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue
                # validate quality assurance
                is_valid, message, quality_assurance_id_array = validate_quality_assurance(row)
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue
                is_valid, message = validate_analyzed_date(row)
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue
                # get sample_mass_processed and sediment_dry_weight if given
                try:
                    sample_mass_processed = row["sample_mass_processed"]
                except KeyError:
                    sample_mass_processed = None
                try:
                    sediment_dry_weight = row["sediment_dry_weight"]
                except KeyError:
                    sediment_dry_weight = None

                # validate result
                # get method id
                method_id = row["method_id"]
                is_valid, message, result_id = validate_result(
                    sample, constituent_id, method_id, row
                )
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue

                # calculate the result
                display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = eval_result(
                    row, result_id
                )
                raw_value = row["raw_value"]

                # SAVE THE RESULT #
                result_details = Result.objects.get(id=result_id)
                result_details.raw_value = float(raw_value)
                result_details.method_id = method_id

                # get and process the final_value
                result_details.final_value = float(raw_value)
                result_details.final_value = process_final_value(
                    result_details.final_value, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed,
                    result_id)

                # calculate the final_method_detection_limit and report value
                method_detection_limit, significant_figures, decimal_places = get_method_type(method_id)
                final_method_detection_limit = process_method_daily_detection_limit(
                    method_detection_limit, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed)
                result_details.final_method_detection_limit = final_method_detection_limit
                #                if (
                #                        method_detection_limit is not None
                #                        and result_details.final_value is not None
                #                        and result_details.final_value < method_detection_limit
                #                ):
                #                    result_details.report_value = final_method_detection_limit
                #                else:
                result_details.report_value = process_report_value(reported_value, method_id, volume_filtered,
                                                                   sediment_dry_weight, sample_mass_processed,
                                                                   result_id)
                # round by sigfigs
                if significant_figures is not None and decimal_places is not None:
                    result_details.report_value = eval_sigfigs_decimals(result_details.report_value,
                                                                        significant_figures, decimal_places)

                result_details.detection_flag = DetectionFlag.objects.get(detection_flag=detection_flag)

                # daily detection limit
                result_details.raw_daily_detection_limit = daily_detection_limit
                result_details.final_daily_detection_limit = process_daily_detection_limit(
                    daily_detection_limit, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed)

                result_details.entry_date = time.strftime("%Y-%m-%d")
                if row["analysis_comment"]:
                    result_details.analysis_comment = row["analysis_comment"]
                else:
                    result_details.analysis_comment = ""
                if row["analyzed_date"]:
                    analyzed_date = row["analyzed_date"]
                    analyzed_date = dt.strptime(analyzed_date, "%m/%d/%Y")
                    result_details.analyzed_date = analyzed_date
                else:
                    result_details.analyzed_date = ""
                if row["percent_matching"]:
                    result_details.percent_matching = row["percent_matching"]
                else:
                    result_details.percent_matching = None
                result_details.save()
                # save quality assurance
                quality_assurance_id_array = quality_assurance_id_array + qa_flags
                for quality_assurance_id in quality_assurance_id_array:
                    QualityAssurance.objects.create(result_id=result_id, quality_assurance_id=quality_assurance_id)
                status.append({"success": "true", "result_id": result_id, "bottle_unique_name": bottle_unique_name})
        except BaseException as e:
            if isinstance(data, list) is False:
                e = "Expecting an array of results"
            status.append({"success": "false", "message": str(e), "bottle_unique_name": bottle_unique_name})
            # traceback.print_exc()
        return HttpResponse(json.dumps(status), content_type='application/json')


######
#
# Batch Upload Validations
#
######


def validate_bottle_bar_code(row):
    is_valid = False
    bottle_id = -1
    volume_filtered = None
    message = ""
    sample = {}

    try:
        bottle_name = row["bottle_unique_name"]
    except KeyError:
        message = "'bottle_unique_name' is required"
        return is_valid, message, bottle_id, sample, volume_filtered

    try:
        bottle_details = Bottle.objects.get(bottle_unique_name=bottle_name)
    except ObjectDoesNotExist:
        message = "The bottle '" + bottle_name + "' does not exist"
        return is_valid, message, bottle_id, sample, volume_filtered

    # get bottle id
    bottle_id = bottle_details.id

    # find the sample bottle id
    try:
        sample_bottle_details = SampleBottle.objects.get(bottle=bottle_id)
    except ObjectDoesNotExist:
        message = "The bottle " + bottle_name + " exists but was not found in the results table"
        return is_valid, message, bottle_id, sample, volume_filtered

    is_valid = True
    sample_bottle_id = sample_bottle_details.id
    volume_filtered = sample_bottle_details.volume_filtered

    return is_valid, message, bottle_id, sample_bottle_id, volume_filtered


def validate_constituent_type(row):
    is_valid = False
    constituent_id = -1
    message = ""
    try:
        constituent_type = row["constituent"]
    except KeyError:
        message = "'constituent' is required"
        return is_valid, message, constituent_id

    # get constituent id
    try:
        constituent_type_details = ConstituentType.objects.get(constituent=constituent_type)
    except ObjectDoesNotExist:
        message = "The constituent type '" + constituent_type + "' does not exist"
        return is_valid, message, constituent_id

    constituent_id = constituent_type_details.id
    is_valid = True
    return is_valid, message, constituent_id


def validate_isotope_flag(row):
    is_valid = False
    message = ""
    isotope_flag_id = -1

    # get isotope flag
    try:
        isotope_flag_id = row["isotope_flag_id"]
        # make sure that it is numeric
        if isinstance(isotope_flag_id, Number) is False:
            message = "Expecting a numeric value for isotope_flag_id"
            return is_valid, message, isotope_flag_id
    except KeyError:
        message = "'isotope_flag_id' is required"
        return is_valid, message, isotope_flag_id

    # get isotope flag id
    try:
        isotope_flag_details = IsotopeFlag.objects.get(id=isotope_flag_id)
    except ObjectDoesNotExist:
        message = "The isotope flag '" + str(isotope_flag_id) + "' does not exist"
        return is_valid, message, isotope_flag_id

    isotope_flag_id = isotope_flag_details.id
    is_valid = True
    return is_valid, message, isotope_flag_id


def validate_analysis_method(constituent_id, row):
    is_valid = False
    analysis_method_id = -1
    message = ""
    constituent_type = row["constituent"]
    try:
        method = row["method_id"]
    except KeyError:
        message = "'method_id' is required"
        return is_valid, message, analysis_method_id

    if isinstance(method, int) is False:
        message = "Expecting an int for method_id"
        return is_valid, message, analysis_method_id

    analysis_types = AnalysisConstituent.objects.filter(constituent_id=constituent_id).values_list('analysis_id',
                                                                                                   flat=True)
    try:
        analysis_type_details = AnalysisMethod.objects.filter(analysis_type__in=analysis_types,
                                                              method_type__exact=method)
        # analysis_type_details = AnalysisMethod.objects.get(analysis_type=str(analysis_type),method_type=str(method))
    except ObjectDoesNotExist:
        message = "The method code '" + str(method) + "' is not allowed for the constituent '" + constituent_type + "'"
        return is_valid, message, analysis_method_id

    if len(analysis_type_details) != 1:
        message = "More than one analysis type was found for method code '" + str(method) + "'"
        message += ", please contact the database administrator."
        return is_valid, message, analysis_method_id
    else:
        is_valid = True
        analysis_method_id = analysis_type_details[0].id
        return is_valid, message, analysis_method_id


def validate_quality_assurance(row):
    is_valid = False
    message = ""
    quality_assurance_id_array = []
    quality_assurance_array = []
    try:
        quality_assurance_array = row["quality_assurance"]
        #  check if it's an array
        if isinstance(quality_assurance_array, list) is False:
            message = "'quality_assurance' needs to be a list of values"
            return is_valid, message, quality_assurance_id_array
    except KeyError:
        is_valid = True

    # check that the given quality assurance exists
    for quality_assurance in quality_assurance_array:
        try:
            quality_assurance_type_details = QualityAssuranceType.objects.get(quality_assurance=quality_assurance)
        except ObjectDoesNotExist:
            message = "The quality assurance type '" + quality_assurance + "' does not exist"
            return is_valid, message, quality_assurance_id_array

        quality_assurance_id = quality_assurance_type_details.id
        quality_assurance_id_array.append(quality_assurance_id)

    is_valid = True
    return is_valid, message, quality_assurance_id_array


def validate_analyzed_date(row):
    # get the date
    if row["analyzed_date"]:
        analyzed_date = row["analyzed_date"]
    else:
        analyzed_date = None

    if analyzed_date is None:
        is_valid = True
        return is_valid, ""
    else:
        try:
            analyzed_date = dt.strptime(analyzed_date, "%m/%d/%Y")
            is_valid = True
            return is_valid, ""
        except ValueError:
            is_valid = False
            message = "The analyzed_date '" + str(
                analyzed_date) + "' does not match the format mm/dd/YYYY. eg. 2/02/2014."
            return is_valid, message


def validate_result(sample_bottle_id, constituent_id, method_id, row):
    is_valid = False
    result_id = -1
    message = ""
    bottle_name = row["bottle_unique_name"]
    constituent_type = row["constituent"]
    isotope_flag_id = row["isotope_flag_id"]

    # make sure that a result is given
    try:
        raw_value = row["raw_value"]
        # make sure that it is numeric
        if isinstance(raw_value, Number) is False:
            message = "Expecting a numeric value for result"
            return is_valid, message, result_id
    except KeyError:
        message = "'raw_value' is required"
        return is_valid, message, result_id

    # Find the matching record in the Results table, using the unique combination of barcode + constituent { + isotope}
    try:
        result_details = Result.objects.get(
            constituent=constituent_id, sample_bottle=sample_bottle_id, isotope_flag=isotope_flag_id)
    except ObjectDoesNotExist:
        message = "There is no matching record in the result table for bottle '"
        message += str(bottle_name) + "', constituent type '" + str(constituent_type) + "' and isotope flag '"
        message += str(isotope_flag_id)
        return is_valid, message, result_id
    except MultipleObjectsReturned:
        message = "There are more than one matching records in the result table for bottle '"
        message += str(bottle_name) + "', constituent type '" + str(constituent_type) + "' and isotope flag '"
        message += str(isotope_flag_id)
        return is_valid, message, result_id
    # check if final value already exists
    final_value = result_details.final_value
    if final_value is not None:
        # print(result_details.id)
        message = "This result row cannot be updated as a final value already exists"
        return is_valid, message, result_id

    is_valid = True
    result_id = result_details.id
    return is_valid, message, result_id


######
#
# Batch Upload Calculations
#
######


def eval_result(row, result_id):
    qa_flags = []
    # check if it is an archived sample
    raw_value = row["raw_value"]
    try:
        daily_detection_limit = row["daily_detection_limit"]
    except KeyError:
        daily_detection_limit = None
    if raw_value == -888:
        display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = get_archived_sample_result()
    # check if lost sample
    elif raw_value == -999:
        display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = get_lost_sample_result(
            raw_value, daily_detection_limit
        )
    else:
        # get isotope flag
        result_details = Result.objects.get(id=result_id)
        isotope_flag = str(result_details.isotope_flag)
        try:
            analysis_date = dt.strptime(row["analyzed_date"], "%m/%d/%Y")
        except ValueError:
            analysis_date = None
        constituent_type = row["constituent"]
        method_code = row["method_id"]
        if (isotope_flag == 'NA' or isotope_flag == 'A') and (
                (constituent_type in ['FMHG', 'FTHG', 'UMHG', 'UTHG']) or
                ((constituent_type in ['PTHG', 'PMHG']) and (analysis_date >= dt.strptime("01/01/2003", "%m/%d/%Y"))) or
                ((constituent_type in ['SMHG', 'STHG']) and (
                        analysis_date >= dt.strptime("01/01/2004", "%m/%d/%Y"))) and
                method_code != 165 or (constituent_type in ['BMHG'] and method_code in [108, 184])
        ):
            # evaluate according to MDL
            method_detection_limit, significant_figures, decimal_places = get_method_type(method_code)
            if raw_value < method_detection_limit:
                display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = eval_mdl(
                    daily_detection_limit, method_detection_limit
                )
            else:
                # evaluate according to significant_figures & decimal_places
                display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = eval_detection(
                    raw_value, daily_detection_limit, method_detection_limit, significant_figures, decimal_places
                )
        elif (isotope_flag in ['X-198', 'X-199', 'X-200', 'X-201', 'X-202']) or (
                (isotope_flag == 'NA' or isotope_flag == 'A') and (
                (constituent_type in ['BMHG'] and method_code != 108) or
                (constituent_type in ['BTHG']) or
                (constituent_type in ['DMHG', 'DTHG', 'STHG', 'PMHG', 'PTHG', 'SMHG', 'SRHG'])
                )
        ):
            # set DDL to -999 for DTHG because it does not have a DDL
            if constituent_type == 'DTHG':
                daily_detection_limit = -999
            # set MDL to DDL
            method_detection_limit, significant_figures, decimal_places = get_method_type(method_code)
            method_detection_limit = daily_detection_limit
            if raw_value < method_detection_limit:
                # evaluate according to MDL
                display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = eval_mdl(
                    daily_detection_limit, method_detection_limit
                )
            else:
                # all isotopes should use a decplaces of 3 despite what is in the
                if isotope_flag in ['X-198', 'X-199', 'X-200', 'X-201', 'X-202']:
                    decimal_places = 3
                # evaluate according to significant_figures & decimal_places
                display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = eval_detection(
                    raw_value, daily_detection_limit, method_detection_limit, significant_figures, decimal_places
                )
        else:
            # if raw_value < 1:
            # display_value = '0'+ str(raw_value)
            # else:
            display_value = str(raw_value)
            detection_flag = 'NONE'
            reported_value = raw_value
    return display_value, reported_value, detection_flag, daily_detection_limit, qa_flags


# Archived Sample
# A value of -888 indicates an archived sample
# an archived sample is one for which no near-term analysis is expected
# in order to not leave a "hole", a value of -888 is used
# VALUE should remain -888
# REPORTED_VALUE and DISPLAY_VALUE should be -888
# DETECTION_FLAG should be 'A'
# DAILY_DETECTION_LIMIT should be set to -888
# No QA flag for the result
def get_archived_sample_result():
    qa_flags = []
    reported_value = -888
    display_value = str(-888)
    detection_flag = 'A'
    daily_detection_limit = -888
    return display_value, reported_value, detection_flag, daily_detection_limit, qa_flags


# Lost Sample
# A value of -999 indicates a lost sample
# VALUE should remain -999
# REPORTED_VALUE and DISPLAY_VALUE should be -999
# DETECTION_FLAG should be 'L'
# DAILY_DETECTION_LIMIT should be set to -999 if not otherwise provided
# Separately, a QA flag of LS should be added for the result
# but that should be accomplished by the batch load process, not this trigger
def get_lost_sample_result(raw_value, daily_detection_limit):
    if daily_detection_limit is None:
        daily_detection_limit = -999
    elif daily_detection_limit == -888:
        daily_detection_limit = -999
    reported_value = raw_value
    detection_flag = 'L'
    display_value = str(raw_value)
    qa_flags = []
    # qa = QualityAssuranceType.objects.get(quality_assurance='LS')
    # qa_flag_id = qa.id
    # qa_flags.append(qa_flag_id)
    return display_value, reported_value, detection_flag, daily_detection_limit, qa_flags


def eval_mdl(daily_detection_limit, method_detection_limit):
    # if method_detection_limit < 1:
    # add leading zero
    #    display_value = '0'+ str(method_detection_limit)
    # else:
    display_value = str(method_detection_limit)
    reported_value = method_detection_limit
    detection_flag = '<'
    return display_value, reported_value, detection_flag, daily_detection_limit, []


# def eval_sigfigs_decimals(
#         raw_value, daily_detection_limit, method_detection_limit, significant_figures, decimal_places):
#     num_infront, num_behind, is_decimal_exists = get_decimal_info(raw_value)

#     if num_infront >= significant_figures+1:
#         sigfig_value = truncate_float(raw_value, significant_figures+1-num_infront)
#     elif num_behind == 0:
#         sigfig_value = raw_value
#     elif num_infront == 0:
#         sigfig_value = truncate_float(raw_value, decimal_places+1)
#     elif (num_infront+num_behind) == significant_figures+1:
#         sigfig_value = truncate_float(raw_value, num_behind)
#     elif (num_infront+num_behind) != significant_figures+1:
#         sigfig_value = truncate_float(
#             raw_value, (num_behind - ((num_infront + num_behind) - (significant_figures + 1))))
#     else:
#         sigfig_value = raw_value

#     #pad sigfig_value with zeroes
#     sigfig_value_str = pad_value(sigfig_value, significant_figures+1, decimal_places+1)
#     rounded_val = round_by_rule_of_five(sigfig_value, sigfig_value_str, significant_figures, decimal_places)
#     #if the daily_detection_limit is null, assign the MDL
#     if daily_detection_limit is None:
#         daily_detection_limit = method_detection_limit
#     #set the reported value to the value
#     reported_value = rounded_val
#     #determine the reported value and detection flag according to the DDL
#     #if the value is greater than the MDL and less than the DDL (MDL < VALUE < DDL),
#     #set the reported value to the value and the flag to E
#     if method_detection_limit <= rounded_val < daily_detection_limit:
#         detection_flag = 'E'
#     #if the value is greater than the MDL and greater than the DDL (MDL < VALUE > DDL),
#     #set the reported value to the value and the flag to NONE
#     elif method_detection_limit <= rounded_val >= daily_detection_limit:
#         detection_flag = 'NONE'
#     else:
#         detection_flag = 'NONE'
#     #Determine the display value by padding with trailing zeros if necessary
#     #Pad the reported_value with trailing zeros if length < sigfigs + 1 (and decimal point)
#     display_value_str = pad_value(reported_value, significant_figures, decimal_places)
#     #pad a leading zero if the value is less than 1
#     #if reported_value < 1 and reported_value > 0:
#     #    display_value_str = '0'+display_value_str
#     return display_value_str, reported_value, detection_flag, daily_detection_limit, []

def eval_sigfigs_decimals(
        value, significant_figures, decimal_places):
    num_infront, num_behind, is_decimal_exists = get_decimal_info(value)

    if num_infront >= significant_figures + 1:
        sigfig_value = truncate_float(value, significant_figures + 1 - num_infront)
    elif num_behind == 0:
        sigfig_value = value
    elif num_infront == 0:
        sigfig_value = truncate_float(value, decimal_places + 1)
    elif (num_infront + num_behind) == significant_figures + 1:
        sigfig_value = truncate_float(value, num_behind)
    elif (num_infront + num_behind) != significant_figures + 1:
        sigfig_value = truncate_float(
            value, (num_behind - ((num_infront + num_behind) - (significant_figures + 1))))
    else:
        sigfig_value = value

    # pad sigfig_value with zeroes
    sigfig_value_str = pad_value(sigfig_value, significant_figures + 1, decimal_places + 1)
    rounded_val = round_by_rule_of_five(sigfig_value, sigfig_value_str, significant_figures, decimal_places)

    # set the reported value to the value
    reported_value = rounded_val

    return reported_value


def eval_detection(
        raw_value, daily_detection_limit, method_detection_limit, significant_figures, decimal_places):
    # if the daily_detection_limit is null, assign the MDL
    if daily_detection_limit is None:
        daily_detection_limit = method_detection_limit
    # set the reported value to the value
    reported_value = raw_value
    # determine the reported value and detection flag according to the DDL
    # if the value is greater than the MDL and less than the DDL (MDL < VALUE < DDL),
    # set the reported value to the value and the flag to E
    if method_detection_limit <= raw_value < daily_detection_limit:
        detection_flag = 'E'
    # if the value is greater than the MDL and greater than the DDL (MDL < VALUE > DDL),
    # set the reported value to the value and the flag to NONE
    elif method_detection_limit <= raw_value >= daily_detection_limit:
        detection_flag = 'NONE'
    else:
        detection_flag = 'NONE'
    # Determine the display value by padding with trailing zeros if necessary
    # Pad the reported_value with trailing zeros if length < sigfigs + 1 (and decimal point)
    display_value_str = pad_value(reported_value, significant_figures, decimal_places)
    # pad a leading zero if the value is less than 1
    if 0 < reported_value < 1:
        display_value_str = '0' + display_value_str

    return display_value_str, reported_value, detection_flag, daily_detection_limit, []


def pad_value(value, significant_figures, decimal_places):
    num_infront, num_behind, is_decimal_exists = get_decimal_info(value)
    value_str = str(value)
    counter = len(value_str)
    # if decimal exists
    if num_behind > 0:
        if value >= 1:
            num_padding = significant_figures + 1 - counter
            if len(value_str) != significant_figures + 1:
                value_str = add_padding(num_padding, value_str)
        else:
            num_padding = decimal_places + 1 - counter
            if len(value_str) != decimal_places + 1:
                value_str = add_padding(num_padding, value_str)
    return value_str


def add_padding(num_padding, value_str):
    if num_padding > 0:
        for x in range(1, num_padding):
            value_str += "0"
    return value_str


def round_by_rule_of_five(sigfig_value, sigfig_value_str, significant_figures, decimal_places):
    if sigfig_value >= 1:
        rounded_val = get_rounded_value(sigfig_value, sigfig_value_str, significant_figures)
    else:
        rounded_val = get_rounded_value(sigfig_value, sigfig_value_str, decimal_places)
    return rounded_val


def get_rounded_value(sigfig_value, sigfig_value_str, value):
    num_infront, num_behind, is_decimal_exists = get_decimal_info(sigfig_value)
    is_last_digit_five, is_last_digit_zero = get_sigfig_info(sigfig_value_str)
    ndigits = num_behind - (num_infront + num_behind - value)
    # confirm that this is ok
    # if last digit is a (trailing) zero, do not do anything if no decimal place
    if is_last_digit_zero and is_decimal_exists:
        rounded_val = sigfig_value
    # if last digit is a (trailing) zero, round if there is a decimal place
    # Or if last digit is not a 5 and there isn't a decimal place, round,-1
    # Or if last digit is not a 5 and there is a decimal place, round,-1
    elif (
            (is_last_digit_zero and not is_decimal_exists) or
            (not is_last_digit_five and not is_decimal_exists) or
            (not is_last_digit_five and is_decimal_exists)
    ):
        rounded_val = round(sigfig_value, ndigits)
    # if last digit is a 5 round off or up based on 2nd last digit
    elif is_last_digit_five:
        digit_before_last = get_digit_before_last(sigfig_value_str, num_behind)
        # if last digit is a 5 and second to last digit is even, trunc
        if digit_before_last % 2 == 0:
            rounded_val = truncate_float(sigfig_value, ndigits)
        # if last digit is a 5 and second to last digit is odd, round
        else:
            rounded_val = math.ceil(sigfig_value * pow(10, ndigits)) / pow(10, ndigits)
    else:
        rounded_val = sigfig_value
    return rounded_val


def get_digit_before_last(value_str, num_behind):
    length = len(value_str)
    if (num_behind > 0) and num_behind == 1:
        # if decimal exists and the decimal point is in the second to last position,
        # take the number just before the decimal point
        digit_before_last = value_str[length - 3:length - 2]
    else:
        # else take the second to last digit
        digit_before_last = value_str[length - 2:length - 1]
    return int(digit_before_last)


def get_sigfig_info(val):
    is_last_digit_five = False
    is_last_digit_zero = False
    val_str = str(val)
    length = len(val_str)
    last_digit = val_str[length - 1:length]
    if last_digit == '5':
        is_last_digit_five = True
    elif last_digit == '0':
        is_last_digit_zero = True
    return is_last_digit_five, is_last_digit_zero


def get_decimal_info(val):
    str_val = str(val)
    val_arr = str_val.split(".")
    num_infront = len(val_arr[0])
    if len(val_arr) > 1:
        num_behind = len(val_arr[1])
        is_decimal_exists = True
    else:
        num_behind = 0
        is_decimal_exists = False
    if num_infront == 1 and val_arr[0] == '0':
        num_infront = 0

    return num_infront, num_behind, is_decimal_exists


def truncate_float(float_value, decimal_places):
    return round(int(float_value * pow(10, decimal_places)) * pow(10, -decimal_places), decimal_places)


def get_method_type(method_code):
    method_type_details = MethodType.objects.get(id=str(method_code))
    significant_figures = method_type_details.significant_figures
    decimal_places = method_type_details.decimal_places
    if method_type_details.method_detection_limit is None or method_type_details.method_detection_limit == '':
        method_detection_limit = 0
    else:
        method_detection_limit = float(method_type_details.method_detection_limit)
    return method_detection_limit, significant_figures, decimal_places


def process_final_value(final_value, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed, result_id):
    value = final_value
    if method_id is None or final_value is None:
        value = final_value
    elif final_value == -999 or final_value == -888:
        value = final_value
    elif method_id in (86, 92, 103, 104):
        value = final_value * 100
    elif method_id == 42:
        value = final_value / 1000
    elif method_id in (48, 49, 83, 84, 85, 233, 211):
        if volume_filtered is None:
            return -900
        else:
            value = final_value * 1000 / volume_filtered
    elif method_id == 52 or method_id == 71:
        if sediment_dry_weight is not None and sediment_dry_weight != -999:
            if sample_mass_processed is not None and sample_mass_processed != -999:
                value = final_value / sediment_dry_weight / sample_mass_processed
    elif method_id in (73, 127, 157):
        if sample_mass_processed is not None and sample_mass_processed != -999:
            value = final_value / sample_mass_processed
    elif method_id in (50, 74, 82):
        if sediment_dry_weight is not None and sediment_dry_weight != -999:
            value = final_value / sediment_dry_weight
    elif method_id == 228:
        if sample_mass_processed is not None and sample_mass_processed != -999:
            value = final_value / sample_mass_processed
    elif method_id == 77:
        if volume_filtered is None:
            return -900
        result = Result.objects.get(pk=result_id)
        tare_weight = Bottle.objects.filter(id=result.sample_bottle.bottle_id)[0].tare_weight
        value = (float(decimal.Decimal(str(final_value)) - tare_weight) * 1000) / (volume_filtered / 1000)
    return value


def process_report_value(report_value, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed,
                         result_id):
    value = report_value
    if method_id is None or report_value is None:
        value = report_value
    elif report_value == -999 or report_value == -888:
        value = report_value
    elif method_id in (86, 92, 103, 104):
        value = round(report_value * 100, 2)
    elif method_id == 42:
        value = round(report_value / 1000, 4)
    elif method_id in (48, 49, 83, 84, 85, 233, 211):
        if volume_filtered is None:
            return -900
        else:
            value = round(report_value * 1000 / volume_filtered, 3)
    elif method_id == 52 or method_id == 71:
        if sediment_dry_weight is not None and sediment_dry_weight != -999:
            if sample_mass_processed is not None and sample_mass_processed != -999:
                value = round(report_value / sediment_dry_weight / sample_mass_processed, 2)
    elif method_id in (73, 127, 157, 228):
        if sample_mass_processed is not None and sample_mass_processed != -999:
            value = round(report_value / sample_mass_processed, 2)
    elif method_id in (50, 74, 82):
        if sediment_dry_weight is not None and sediment_dry_weight != -999:
            value = round(report_value / sediment_dry_weight, 2)
    elif method_id == 77:
        if volume_filtered is None:
            return -900
        result = Result.objects.get(pk=result_id)
        tare_weight = Bottle.objects.filter(id=result.sample_bottle.bottle_id)[0].tare_weight
        value = round((float(decimal.Decimal(str(report_value)) - tare_weight) * 1000) / (volume_filtered / 1000), 4)
    return value


def process_daily_detection_limit(
        daily_detection_limit, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed):
    value = daily_detection_limit
    if method_id is None or daily_detection_limit is None or daily_detection_limit == 0:
        value = daily_detection_limit
    elif daily_detection_limit == -999:
        value = daily_detection_limit
    elif method_id == 42:
        value = daily_detection_limit / 1000
    elif method_id in (48, 49, 83, 84, 85, 233):
        if volume_filtered is None:
            return -900
        else:
            value = daily_detection_limit * 1000 / volume_filtered
    elif method_id == 71 or method_id == 211:
        if sediment_dry_weight is None or sediment_dry_weight == -999:
            value = -999
        else:
            if sample_mass_processed is None or sample_mass_processed == -999:
                value = -999
            else:
                value = daily_detection_limit / sediment_dry_weight / sample_mass_processed
    elif method_id in (50, 74, 82):
        if sediment_dry_weight is None or sediment_dry_weight == -999:
            value = -999
        else:
            value = daily_detection_limit / sediment_dry_weight
    elif method_id in (73, 127, 157, 228):
        if sample_mass_processed is None or sample_mass_processed == -999:
            value = -999
        else:
            value = daily_detection_limit / sample_mass_processed
    return value


def process_method_daily_detection_limit(
        method_daily_detection_limit, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed):
    value = method_daily_detection_limit
    if method_id is None or method_daily_detection_limit is None or method_daily_detection_limit == 0:
        value = method_daily_detection_limit
    elif method_daily_detection_limit == -999:
        value = -999
    elif method_id == 42:
        value = method_daily_detection_limit / 1000
    elif method_id in (48, 49, 83, 84, 85, 233, 211):
        if volume_filtered is None:
            return -900
        else:
            value = method_daily_detection_limit * 1000 / volume_filtered
    elif method_id == 52 or method_id == 71:
        if sediment_dry_weight is None or sediment_dry_weight == -999:
            value = -999
        else:
            if sample_mass_processed is None or sample_mass_processed == -999:
                value = -999
            else:
                value = method_daily_detection_limit / sediment_dry_weight / sample_mass_processed
    elif method_id in (50, 74, 82):
        if sediment_dry_weight is None or sediment_dry_weight == -999:
            value = -999
        else:
            value = method_daily_detection_limit / sediment_dry_weight
    elif method_id in (73, 127, 157, 228):
        if sample_mass_processed is None or sample_mass_processed == -999:
            value = -999
        else:
            value = method_daily_detection_limit / sample_mass_processed
    if value is not None:
        value = round(value, 4)
    return value
