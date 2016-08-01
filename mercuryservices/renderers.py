from rest_framework_csv.renderers import CSVRenderer

# these custom renderers have hard-coded field name headers that match the their respective serialzers
# from when this code was originally written, so if the serializer fields change, these renderer field name headers
# won't match the serializer data, until the renderer code is manually updated to match the serializer fields


class PaginatedResultSampleCSVRenderer(CSVRenderer):
    results_field = 'results'

    def render(self, data, media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        self.headers = ['sample_id', 'project_name', 'project_id', 'site_name', 'site_id', 'date', 'time', 'depth',
                        'length', 'replicate', 'sample_comments', 'received', 'lab_processing', 'container_id',
                        'medium', 'analysis', 'constituent', 'isotope', 'filter', 'filter_vol', 'preservation', 'acid',
                        'acid_vol', 'pres_comments', 'sample_bottle_id', 'result_id']
        return super(PaginatedResultSampleCSVRenderer, self).render(data, media_type, renderer_context)


class PaginatedResultCSVRenderer(CSVRenderer):
    results_field = 'results'

    def render(self, data, media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        self.headers = ['result_id', 'bottle', 'tare_weight', 'project_name', 'site_name', 'site_id', 'sample_date',
                        'sample_time', 'depth', 'medium', 'constituent', 'isotope', 'received_date', 'comments',
                        'result_value', 'unit', 'detection_flag', 'ddl', 'qa_flags', 'analysis_comments',
                        'analyzed_date']
        return super(PaginatedResultCSVRenderer, self).render(data, media_type, renderer_context)
