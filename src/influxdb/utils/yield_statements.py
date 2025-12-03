from influxdb.models.flux_obj import Filter



def yield_measurements_statement(bucket:str, **args):
    return f'schema.measurements(bucket:"{bucket}")'

def yield_tag_key_statement(bucket:str, measurement:str=None, **args):
    if measurement:
        m = f'schema.tagKeys(bucket:"{bucket}", predicate: (r)=>r._measurement == "{measurement}")'
                
    else:
        m = f'schema.tagKeys(bucket:"{bucket}")'
    return m

def yield_tag_value_statement(bucket:str, tag_key:str, **args):
    if not filters:
        raise RuntimeError('missing parameter: filters')
    filters.joint = ' and '
    filters.inner_joint = ' or '
    filters.template = '({})'
    if not filters.tag:
        raise RuntimeError(f'tag is required.')
    tag = filters.tag
    del filters.tag
    predicate = f'predicate: (r)=> {repr(filters)}'
    return f'schema.tagValues(bucket:"{bucket}",tag:{tag_key}"){predicate}'

def yield_fields_statement(bucket:str, filters: Filter=None, **args):
    if filters:
        filters.joint = ' and '
        filters.inner_joint = ' or '
        filters.template = '({})'
        return f'schema.fieldKeys(bucket:"{bucket}", predicate: (r)=>{repr(filters)})'
    return f'schema.fieldKeys(bucket:"{bucket}")'