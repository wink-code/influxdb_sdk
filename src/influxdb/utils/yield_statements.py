from influxdb.models.flux_obj import Filter,QueryPredicateFilter



def yield_measurements_statement(bucket:str, **args):
    return f'schema.measurements(bucket:"{bucket}")'

def yield_tag_key_statement(bucket:str, measurement:str=None, **args):
    if measurement:
        m = f'schema.tagKeys(bucket:"{bucket}", predicate: (r)=>r._measurement == "{measurement}")'
                
    else:
        m = f'schema.tagKeys(bucket:"{bucket}")'
    return m

def yield_tag_value_statement(bucket:str, tag_key:str, **kwargs):
    filters = [item for item in kwargs.values() if isinstance(item, QueryPredicateFilter)]
    predicate = f',predicate:(r)=>({repr(filters[0])})' if len(filters) > 0 else ''
    return f'schema.tagValues(bucket:"{bucket}",tag:"{tag_key}"{predicate})'

def yield_fields_statement(bucket:str, filters: QueryPredicateFilter=None, **args):
    if filters:
        return f'schema.fieldKeys(bucket:"{bucket}", predicate: (r)=>{repr(filters)})'
    return f'schema.fieldKeys(bucket:"{bucket}")'