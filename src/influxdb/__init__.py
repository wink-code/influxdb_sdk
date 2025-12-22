import logging

from influxdb_client import InfluxDBClient

from influxdb.config import InfluxDBConfig
from influxdb.query import QuerySDK
from src.influxdb.exceptions import InfluxDBError, AuthenticationError, EssentialElementsMissingError



logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('influxdb_sdk.log',encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)



__all__ = ["InfluxDBClient", "InfluxDBConfig","InfluxDBCursor"]



class InfluDBCursor:
    ''' InfluxDB Cursor class '''

    def __init__(self, config: InfluxDBConfig=None, **kwargs):
        '''
        :param config: InfluxDBConfig, the influxdb config client instance.
        :param url:str, the influxdb service host url
        :param org:str, represent the org of the influxdb client
        :param token:str, authorize to the influxdb client
        :param config_file: str, the config file path of influxdb client, default key is `influx2`.
        '''
        if config:
            self._config = config._config
        else:
            self._config = InfluxDBConfig(**kwargs)

        self.is_connected = False


    def connect(self):
        ''' connect to influxdb service, and validate the token. '''

        logger.debug("尝试连接 InfluxDB 服务, 地址：%s", self.url)

        self._client = InfluxDBClient(
                           url=self._config.url,
                           org=self._config.org,
                           token=self._config.token,
                           **self._config.kwargs
                        )

        # 这一步我的本意是验证 token 格式正确， 但是 如果采用这种方式， 虽然能证明格式正确， 但是会对token权限额外要求有user读取权限。我觉得重心不应该在token权限验证上。
        try:
            self._validate_auth()
            logger.info("\u2713 客户端初始化成功 - [url: %s, org: %s]", self.url,self.org)
        except:
            logger.error("\u274C 客户端初始化失败 - [url: %s, org: %s]", self.url,self.org)
            raise InfluxDBError("Client initialization failed!")
        self.is_connected = True



    def _validate_auth(self):
        try:
            me = self._client.users_api().me()
            logger.info("\u2713 认证成功 - [current username: %s, id: %s]", me.name, me.id)
            self.me = me
        except ApiException as e:
            self.close()
            logger.error("\u274C 认证失败 - 状态码：%s 响应：%s", e.status, e.body)
            if e.status == 401:
                raise AuthenticationError(f"\u274C Token无效！响应：{e.body}") from e
            if e.status == 403:
                raise AuthenticationError(f"\u274C Token对 org[{self.org}] 无权限") from e
            if e.status == 404:
                raise EssentialElementsMissingError(f"\u274C Org [{self.org}] 不存在") from e
            raise InfluxDBError(f"\u274C 认证失败！状态码：{e.status} 响应：{e.body}") from e

        # 捕获连接拒接，超时等网络错误
        except (ConnectionRefusedError, TimeoutError) as e:
            logger.error("\u274C 连接失败：无法连接到 Influx DB服务，请检查url和服务状态。错误：{}".format(str(e)))
            self.close()
            raise RuntimeError(f"\u274C 连接失败：无法连接到 Influx DB服务，请检查url和服务状态。错误：{str(e)}") from e

        except requests.exceptions.RequestException as e:
            logger.error("\u274C 网络请求错误：{}".format(str(e)))
            self.close()
            raise RuntimeError(f"\u274C 网络请求错误：{str(e)}") from e

    def write(self, data, write_options=None):
        ''' return the write api client '''
        return self._client.write_api(write_options=write_options).write(data=data)
    
    def query(self, mode: Literal['raw','dataframe']='dataframe',**kwargs):
        ''' return the query sdk client '''
        return QuerySDK(self._client.query_api())




if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    config = create_influxdb_client(
        url="http://influxdb-dev:8086",
        token="{env:INFLUXDB_TOKEN}",
        org="DFMC"
    )
    ping = config().ping()
    print(ping)