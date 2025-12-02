from influxdb.models.flux_obj import Filter



def yield_measurements_statement(bucket:str):
    return f'schema.measurements(bucket:"{bucket}")'

def yield_tag_key_statement(bucket:str, measurement:str=None):
    if measurement:
        return f'schema.tagKeys(bucket:"{bucket}", predicate: (r)=>r._measurement == "{measurement}")'
    else:
        return f'schema.tagKeys(bucket:"{bucket}")'

def yield_tag_value_statement(bucket:str, tag_key:str):
    return f'schema.tagValues(bucket:"{bucket}",tag:"{tag_key}")'

def yield_fields_statement(bucket:str, filters: Filter=None):
    if filters:
        filters.joint = ' and '
        filters.inner_joint = ' or '
        filters.template = '({})'
        return f'schema.fieldKeys(bucket:"{bucket}", predicate: (r)=>{repr(filters)})'