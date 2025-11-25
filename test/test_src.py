from src import InfluxDBSDK
import os
if __name__ == "__main__":
    try:
        influxdbsdk = InfluxDBSDK(org='DFMC',token=os.getenv('INFLUXDB_TOKEN'))
    except Exception as e:
        print(f"客户端初始化失败：{str(e)}.")
    else:
        print(type(influxdbsdk))

    influxdbsdk.query("test","DFMC",
    filters={"_measurement":"temperatures in different rooms","location":["room1","room2"],"_field":"temperature"},
    aggregateWindow={"every":"3s","fn":"mean","createEmpty":"false"},
    pivot={"columnKey":"_field","rowKey":"_time","columnValues":["_value"]})