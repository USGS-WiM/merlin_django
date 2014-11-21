from django.http import HttpResponseRedirect
from django.views.generic import *
from django.template import RequestContext
from django.shortcuts import render, render_to_response
from mercurylab.forms import *
from django.forms.formsets import formset_factory
import requests

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
