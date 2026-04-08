from CMA import CMA
from Cosco import COSCO
from EMC import EMC
from GOS import GOS
from HMM import HMM
from KMTC import KMTC
from MSC import MSC
from MSK import MSK
from ONE import ONE
from OOCL import OOCL
from RCL import RCL
from SLS import SLS
from SNL import SNL
from Sealand import SEALNAD
from WeiYun import WeiYun
from YML import YML
from ZIM import ZIM
from WHL import WHL


# 工厂角色
class CreateCrawl:
    @classmethod
    def create_crawl(cls, carrier, tracking_no):
        if carrier == "ZIM" and tracking_no.startswith('ZIM'):
            return ZIM()  # 较慢
        elif carrier == "ZIM" and tracking_no.startswith('GOS'):
            return GOS()
        elif carrier == "ZIM" and tracking_no.startswith("ONEY"):
            return ONE()
        elif carrier == "EMC":
            return EMC()
        elif carrier == 'MSK':
            return MSK()
        elif carrier == 'CMA':
            return CMA()  # 需要验证
        elif carrier == 'SNL':
            return SNL()
        elif carrier == 'COSCO':
            return COSCO()
        elif carrier == "OOCL":  # 没有数据 有拼图
            return OOCL()
        elif carrier == 'ONE':  # 较慢
            return ONE()
        elif carrier == 'MSC':
            return MSC()
        elif carrier == 'HMM':
            return HMM()
        elif carrier == 'YML':
            return YML()
        elif carrier == "KMTC":  # 较慢
            return KMTC()
        elif carrier == 'RCL':
            return RCL()
        elif carrier == 'SEALAND':  # 没有数据
            return SEALNAD()
        elif carrier == 'SLS':  # 没有数据
            return SLS()
        elif carrier == 'WHL':  # 反爬
            return WHL()
        elif carrier == 'WeiYun':
            return WeiYun()
        else:
            return None
