from influxdb import InfluxDBSDK
from influxdb.models.flux_obj import Filter
from influxdb.query import FluxQuery


with InfluxDBSDK.from_config_file(r'test/influxdb-client.toml') as sdk:
    query_sdk = sdk.query_sdk()
    
    ''' build flux scripts '''
    filters = Filter('test').set_field('旋流器沉砂干矿量')
    flux_query = FluxQuery(bucket='write-test',filters=filters)
    def with_elapsed():
        flux_query = repr(flux_query)+'\n|> elapsed()'
        # print(flux_query)
        result = query_sdk.query(flux_script=flux_query,columns=['_time','_field','elapsed'])
        # print(result)
        import pandas as pd
        df = pd.DataFrame(columns=['time','field','elapsed'],data=result)
        df_elapsed = df.filter(regex='^elapsed')
        print(df_elapsed.diff())
    def without_elapsed():
        result = query_sdk.query(query=flux_query,columns=['_time','_field'])
        import pandas as pd
        df = pd.DataFrame(columns=['_time','_field'],data=result)
        print(df['_time'].diff())
    without_elapsed()