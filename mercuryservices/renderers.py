from rest_framework_csv.renderers import CSVRenderer


class PaginatedResultSampleCSVRenderer(CSVRenderer):
    results_field = 'results'

    def render(self, data, media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        self.headers = ['sample_id', 'project_name', 'project_id', 'site_name', 'site_id', 'date', 'time', 'depth',
                        'length', 'replicate', 'sample_comments', 'received', 'lab_processing', 'container_id',
                        'medium', 'analysis', 'isotope', 'filter', 'filter_vol', 'preservation', 'acid', 'acid_vol',
                        'pres_comments', 'sample_bottle_id', 'result_id']
        return super(PaginatedResultSampleCSVRenderer, self).render(data, media_type, renderer_context)


class PaginatedResultCSVRenderer(CSVRenderer):
    results_field = 'results'

    def render(self, data, media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        self.headers = ['result_id', 'bottle', 'tare_weight', 'project_name', 'site_name', 'sample_date', 'sample_time',
                        'depth', 'constituent', 'isotope_flag', 'received_date', 'comments', 'final_value',
                        'report_value', 'unit', 'detection_flag', 'analyzed_date']
        return super(PaginatedResultCSVRenderer, self).render(data, media_type, renderer_context)