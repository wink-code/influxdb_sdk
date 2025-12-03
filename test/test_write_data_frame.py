from influxdb_client.extras import pd
# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from src.influxdb import InfluxDBSDK
from influxdb_client.client.write_api import PointSettings

raw_data_frame = pd.read_excel(r'test/test_data/4号球6月-7月数据.xlsx',sheet_name=3,header=0,index_col=1,parse_dates=[1])

needed_data_frame = raw_data_frame.drop(columns=['ID'])

# needed_data_frame.index = pd.to_datetime(needed_data_frame.index,unit='s')
needed_data_frame.index = needed_data_frame.index.round('s')

needed_data_frame['location'] = 'London'

print(needed_data_frame.head())

print(needed_data_frame['location'])

# print(needed_data_frame.iloc[:,2])

def plot_data():
    plt.figure(figsize=(8,4))
    plt.plot(needed_data_frame.index,needed_data_frame.iloc[:,0])
    # plt.show(block=True)
    try:
        plt.savefig(f'out-put-{needed_data_frame.columns[0]}.png',dpi=150)
    except Excetption as e:
        print('fail to save figure.')
    else:
        print('successfully ')

    # plt.plot(needed_data_frame.index, needed_data_frame.iloc[:,0])
    # plt.show()

    
# pointsettings = PointSettings(**{'location':'London'})

# pointsettings = PointSettings(default_key='defautl_value')
# pointsettings.add_default_tag('location','London')


with InfluxDBSDK.from_config_file(r'/workspace/test/influxdb-client.toml',debug=True) as sdk:
    write_sdk = sdk.write_sdk(point_settings=PointSettings())
    write_sdk.write_data_frame(bucket='write-test',data_frame=needed_data_frame, data_frame_measurement_name='4号球6月-7月数据', data_frame_tag_columns=['location'])
    