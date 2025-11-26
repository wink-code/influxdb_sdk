from src.influxdb import InfluxDBSDK
import os
import sys
# print(sys.path)
print(__file__)
config_path = "influxdb-client.toml"
os.chdir(os.path.dirname(os.path.abspath((__file__))))
# print(os.getcwd())
# print(os.path.exists(config_path))
try:
    influxdbsdk = InfluxDBSDK.from_config_file(config_path)
except Exception as e:
    print(f"Exception, <{type(e).__name__}> {str(e)}")
else:
    print('客户端配置成功！')
    print(f'{influxdbsdk.org}')
finally:
    influxdbsdk.close()
# with InfluxDBSDK.from_config_file(config_path) as client:
#     if client.ping():
#         print('ping successfully.')
#     else:
#         print('ping 失败')


# from src import InfluxDBSDK
# import os
# import sys

# # 打印当前文件路径和目录
# current_file = os.path.abspath(__file__)
# current_dir = os.path.dirname(current_file)
# print(f"当前文件路径: {current_file}")
# print(f"当前文件所在目录: {current_dir}")

# config_path = "/workspace/influxdb-client.toml"
# # 拼接完整的配置文件路径
# full_config_path = os.path.join(current_dir, config_path)
# print(f"配置文件完整路径: {full_config_path}")

# # 检查文件是否存在
# print(f"文件是否存在: {os.path.exists(full_config_path)}")

# try:
#     # 使用完整路径加载配置
#     influxdbsdk = InfluxDBSDK.from_config_file(full_config_path)
# except Exception as e:
#     print(f"Exception, <{type(e).__name__}> {str(e)}")