import datetime
import random
from time import sleep

import ddddocr
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from CreateCrawl import CreateCrawl
from tool import GeneralTool
from tool import logger

tool = GeneralTool()
ocr = ddddocr.DdddOcr(beta=True, show_ad=False)

ip = "117.32.77.109"  # 到时候请自行更换
port = "64256"  # 到时候请自行更换

username = "ILIDO233"  # 港航的账号和密码
password = "A&Twsy9651"

getInfos = []
inputInfos = []
infos = []
processInfos = []

# 获取的链接
# getURL = 'https://uat-poms.smil.com/external-sys/api/v1/rpa/getWaybillInfo'

getURL = 'https://poms.smil.com/external-sys/api/v1/rpa/getWaybillInfo'
getHeader = {
    "x-app-id": 'POMS-RPA'
}

# 推送的链接
# postURL = 'https://uat-poms.smil.com/external-sys/api/v1/rpa/postShippingDate'

postURL = 'https://poms.smil.com/external-sys/api/v1/rpa/postShippingDate'
postHeader = {
    "x-app-id": 'POMS-RPA'
}

# Chrome浏览器
driver = webdriver.Chrome()
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)


def getImageInfo(imageName):
    with open(imageName, 'rb') as f:
        image = f.read()
    res = ocr.classification(image)
    logger.info(f'开始的验证码是 {res}')
    res = res.replace('-', '')
    res = res.replace('/', '')
    res = res.upper()
    logger.info(f'验证码是 {res}')
    return res


def getTheShipInfoByGet(URL):
    result = requests.get(URL, headers=getHeader).json()
    resultData = result['data']

    for data in resultData:
        logger.info('------------------------------------------------')
        id = data['id']
        vessel = data['vessel']
        voyage = data['voyage']
        carriers = data['carrier']
        bookingNo = data['bookingNo']
        blNo = data['blNo']

        getInfo = {"id": id, "vessel": vessel, "voyage": voyage, "carrier": carriers, "bookingNo": bookingNo,
                   'blNo': blNo}
        getInfos.append(getInfo)

        inputInfo = data
        logger.info(f'get拿到的数据 {inputInfo}')

        inputInfos.append(inputInfo)

        if (vessel == None):
            vessel = ''
        if (voyage == None):
            voyage = ''
        if (bookingNo == None):
            bookingNo = ''
        if (blNo == None):
            blNo = ''

        info = getInfoInHangGang(id, vessel, voyage)
        logger.info(f'港航拿到的数据 {info}')
        processInfos.append(info)
        writeItemData(info, 'process_output.txt')

        if (info['atd'] != None):
            info['etd'] = data['etd']
        else:
            info['atd'] = data['atd']
            if (info['etd'] == None):
                info['etd'] = data['etd']
        logger.info(f'港航最后处理的数据 {info}')
        infos.append(info)
        sleep(10)


def LoginInHangGang():
    # 港航网页
    url = 'https://www.hb56.com'

    try:

        driver.get(url)
        driver.maximize_window()
    except:
        return {"error": '3. 网页超时，无法获取 --- 无法打开网页'}

    # 点击登录
    button = driver.find_element(By.XPATH, '//*[@id="apre"]/a')
    button.click()

    # 切换登录方式
    driver.implicitly_wait(30)
    button = driver.find_element(By.XPATH, '//*[@class="next_btn"]')
    button.click()

    # 自适应等待，输入用户名
    driver.implicitly_wait(30)
    driver.find_element(By.XPATH, '//*[@id="M_USER_NAME"]').send_keys(username)

    # 自适应等待，输入密码
    driver.implicitly_wait(30)
    driver.find_element(By.XPATH, '//*[@id="S_PASSWORD"]').send_keys(password)

    # 截图
    sleep(5)
    verifyImg = driver.find_element(By.XPATH, '//*[@class="reg"]/form/table/tbody/tr[5]/td/img')
    path = "verifyImg.png"
    verifyImg.screenshot(path)
    # 识别
    sleep(3)
    verificationCode = getImageInfo(path)
    # 填写验证码
    sleep(3)
    driver.find_element(By.XPATH, '//*[@class="easyui-textbox"]').send_keys(verificationCode)

    # 点击登录
    driver.implicitly_wait(30)
    button = driver.find_element(By.XPATH, '//*[@id="btnLogin"]')
    button.click()

    # in case 验证码错误：
    while True:
        try:
            errorTips = driver.find_element(By.XPATH, '//*[@id="errorMes"]').text
            logger.info('验证码错误')
            # continue
        except:
            logger.info('验证码正确')
            break
        # 自适应等待，输入密码
        driver.implicitly_wait(30)
        driver.find_element(By.XPATH, '//*[@id="S_PASSWORD"]').send_keys(password)
        # 截图
        sleep(5)
        verifyImg = driver.find_element(By.XPATH, '//*[@class="reg"]/form/table/tbody/tr[5]/td/img')
        path = "verifyImg.png"
        verifyImg.screenshot(path)
        # 识别
        sleep(3)
        verificationCode = getImageInfo(path)
        # 填写验证码
        sleep(3)
        driver.find_element(By.XPATH, '//*[@class="easyui-textbox"]').send_keys(verificationCode)

        # 点击登录
        driver.implicitly_wait(30)
        button = driver.find_element(By.XPATH, '//*[@id="btnLogin"]')
        button.click()

    # 直到获取到用户名才能确定是登录成功
    user_name = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'd_UserInfo')))
    # 输出用户名
    logger.info(user_name.text)

    # 开始查询
    driver.implicitly_wait(30)
    button = driver.find_element(By.XPATH, '//*[@class="nav"]/ul/li/a')
    button.click()

    # 船期查询
    driver.implicitly_wait(30)
    button = driver.find_element(By.XPATH, '//*[@class="main_grid"]/div/div/div[2]/h3/a')
    button.click()

    # 选择靠泊
    driver.implicitly_wait(30)
    button = driver.find_element(By.XPATH, '//*[@class="tabs-wrap"]/ul/li[2]')
    button.click()

    sleep(3)
    driver.implicitly_wait(30)

    getTheShipInfoByGet(getURL)
    logger.info(infos)


def getInfoInHangGang(id, vessel, voyage):
    # 输入船名
    driver.implicitly_wait(60)
    driver.find_element(By.XPATH, '//*[@class="c_search_div"]/table/tbody/tr/td[2]/input').clear()
    driver.find_element(By.XPATH, '//*[@class="c_search_div"]/table/tbody/tr/td[2]/input').send_keys(vessel)

    sleep(2)
    # 输入航次
    driver.implicitly_wait(30)
    driver.find_element(By.XPATH, '//*[@class="c_search_div"]/table/tbody/tr/td[4]/input').clear()
    driver.find_element(By.XPATH, '//*[@class="c_search_div"]/table/tbody/tr/td[4]/input').send_keys(voyage)

    # 查询
    driver.implicitly_wait(30)
    button = driver.find_element(By.XPATH, '//*[@class="c_search_div"]/table/tbody/tr/td[8]/div/a')
    button.click()

    # 刷新一下
    # button = driver.find_element(By.XPATH, '//*[@class="tabs-header tabs-header-plain"]')
    # button.click()

    # 获取时间
    sleep(3)
    driver.implicitly_wait(30)

    atd = None
    etd = None
    eta = None
    ata = None

    try:
        tableGrid = driver.find_element(By.XPATH,
                                        '//*[@class="tabs-panels"]/div[2]/div/div/div/div/div[2]/div[2]/div[2]/table/tbody/tr')
        # print('表格内容', tableGrid.text)
        # 计划靠泊时间 2023-03-14 01:30
        eta = tableGrid.find_element(By.XPATH, 'td[7]/div').text
        eta = None
        # 实际靠泊时间
        ata = tableGrid.find_element(By.XPATH, 'td[8]/div').text
        ata = None
        # 计划离港时间
        etd = tableGrid.find_element(By.XPATH, 'td[9]/div').text
        logger.info(f'etd是 {etd}')
        etd = tool.dealWithDate(etd)
        # 实际离港时间
        atd = tableGrid.find_element(By.XPATH, 'td[10]/div').text
        logger.info(f'atd是 {atd}')
        atd = tool.dealWithDate(atd)

        # print(eta, ata, etd, atd)
        if (eta == 0 and ata == 0 and etd == 0 and atd == 0):
            result = {"id": id, "etd": None, "atd": None, "eta": None, "ata": None, "error": '2. 网站本身没数据'}
        else:
            result = {"id": id, "etd": etd if etd != 0 else None, "atd": atd if atd != 0 else None, "eta": eta,
                      "ata": ata, "error": ''}
        return result

    except:
        result = {"id": id, "etd": None, "atd": None, "eta": None, "ata": None, "error": '2. 网站本身没数据'}
        return result
        pass


def getInfoFromHangGang():
    start_time = datetime.datetime.now()
    LoginInHangGang()
    driver.quit()
    end_time = datetime.datetime.now()
    logger.info(f"港航用了 {end_time - start_time}")


def getInfoByCarrier():
    logger.info('----------------------------------------------------------------')
    start_time1 = datetime.datetime.now()
    for data in getInfos:
        start_time = datetime.datetime.now()
        id = data['id']
        vessel = data['vessel']
        voyage = data['voyage']
        carriers = data['carrier']

        realBookingNo = data['bookingNo']
        # 获取bookingNo
        # bookingNo = data['bookingNo']
        # 获取blNo
        blNo = data['blNo']

        if (realBookingNo == None):
            realBookingNo = blNo

        logger.info(str(data))
        # logger.info('读取到的','vessel', vessel, 'voyage', voyage, 'carriers', carriers, 'bookingNo', bookingNo)

        if (vessel == None):
            vessel = ''
        if (voyage == None):
            voyage = ''
        if (realBookingNo == None):
            realBookingNo = ''
        else:
            realBookingNo = realBookingNo.strip()

        info = {"id": id, "etd": 0, "atd": 0, "eta": 0, "ata": 0}
        crawl = CreateCrawl()
        if (carriers == 'WeiYun'):  # or carriers == 'CMA'
            iteminfo = crawl.create_crawl(carriers, vessel)
        else:
            iteminfo = crawl.create_crawl(carriers, realBookingNo)

        if (iteminfo != None):
            if (carriers == 'WeiYun'):
                infoWeb = iteminfo.crawl(carriers, vessel)
            else:
                infoWeb = iteminfo.crawl(carriers, realBookingNo)

            info["eta"] = infoWeb.get("eta")
            info["atd"] = infoWeb.get("atd")
            info["etd"] = infoWeb.get("etd")
            info["ata"] = infoWeb.get("ata")
            info["error"] = infoWeb.get("error")
            # print(infoWeb)
        else:
            logger.error('5. 船公司代码无效')
            info["error"] = '5. 船公司代码无效'

        '''
        # 如果由于反爬虫 没有得到的话
        if(info["error"] != None and'暂时无法获取2' in info["error"]):
            iteminfo = crawl.create_crawl('WeiYun', vessel)
            if (iteminfo != None):
                infoWeb = iteminfo.crawl('WeiYun', vessel)
                info["eta"] = infoWeb.get("eta")
                info["atd"] = infoWeb.get("atd")
                info["etd"] = infoWeb.get("etd")
                info["ata"] = infoWeb.get("ata")
                info["error"] = infoWeb.get("error")
                print(infoWeb)
        '''
        sleep(10)
        end_time = datetime.datetime.now()
        logger.info(f'这一轮用了 {end_time - start_time}')
        logger.info(info)
        # 每一条读取的
        processInfos.append(info)
        writeItemData(info, 'process_output.txt')
        updateList(infos, info)
        logger.info('.................................')

    end_time1 = datetime.datetime.now()
    logger.info(f'最后用了 {end_time1 - start_time1}')


def updateList(preJson, curItem):
    for item in preJson:
        if (item["id"] == curItem["id"]):

            if (curItem["eta"] == None or curItem["eta"] == 0):
                item["eta"] = None
            else:
                item["eta"] = curItem["eta"]

            if (curItem["ata"] == None or curItem["ata"] == 0):
                item["ata"] = None
            else:
                item["ata"] = curItem["ata"]

            if (curItem["error"] == None):
                item["error"] = None
            else:
                # if(item["etd"] == None and item["atd"] == None and item["ata"] == None and item["eta"] == None):
                item["error"] = curItem["error"]

    logger.info(f'更新后的数据 {preJson}')


def getInputData(inputData, item):
    for input in inputData:
        if (item["id"] == input["id"]):
            return input


def getDateFromSeconds(seconds):
    if (seconds != None):
        return datetime.datetime.fromtimestamp(seconds / 1000.0)
    else:
        return None


def dealOutputDate(output):
    _output = {}
    _output["id"] = output["id"]
    _output["etd"] = str(getDateFromSeconds(output["etd"]))
    _output["atd"] = str(getDateFromSeconds(output["atd"]))
    _output["eta"] = str(getDateFromSeconds(output["eta"]))
    _output["ata"] = str(getDateFromSeconds(output["ata"]))
    _output["error"] = output["error"]
    return _output


def dealInputDate(output):
    _output = {}
    _output["id"] = output["id"]
    _output["vessel"] = output["vessel"]
    _output["voyage"] = output["voyage"]
    _output["carrier"] = output["carrier"]
    _output["bookingNo"] = output["bookingNo"]
    _output["etd"] = str(getDateFromSeconds(output["etd"]))
    _output["atd"] = str(getDateFromSeconds(output["atd"]))

    return _output


def writeData(jsonData, savepath):
    with open(savepath, mode="a", encoding="utf-8") as file:
        file.write('>>>>>>>>>>>>>>>>>')
        file.write('\n')
        for data in jsonData:
            file.write(str(datetime.datetime.now()))
            file.write(' >>> ')
            input = getInputData(inputInfos, data)
            file.write("INPUT: ")
            file.write(str(dealInputDate(input)))
            file.write("  >>>>>>>>  OUTPUT: ")
            file.write(str(dealOutputDate(data)))
            file.write('\n')

        file.close()


def writeItemData(jsonItem, savepath):
    with open(savepath, mode="a", encoding="utf-8") as file:
        file.write(str(datetime.datetime.now()))
        file.write(' >>> ')
        input = getInputData(inputInfos, jsonItem)
        file.write("INPUT: ")
        file.write(str(dealInputDate(input)))
        file.write("  >>>>>>>>  OUTPUT: ")
        file.write(str(dealOutputDate(jsonItem)))
        file.write('\n')
        file.close()


def writeStartLog(startLog, savepath):
    with open(savepath, mode="a", encoding="utf-8") as file:
        file.write(startLog)
        file.write('\n')
        file.close()


if __name__ == '__main__':
    start_time1st = datetime.datetime.now()
    writeStartLog('>>>>>>>>>>>>>', 'process_output.txt')
    getInfoFromHangGang()
    sleep(10)

    # getInfos = [{"id": 2000178, "vessel": 'MAERSK EVORA', "voyage": '327S', "carrier": 'MSK', "bookingNo": None,'blNo':'228818941 '}]
    # infos = [{'id': 2000178, 'vessel': 'MAERSK EVORA', 'voyage': '327S', 'carrier': 'MSK', 'bookingNo': '228818941','etd': '', 'atd': 'None'}]
    # 获取链接
    getInfoByCarrier()
    end_time1st = datetime.datetime.now()
    logger.info(f"总共用了 {end_time1st - start_time1st}")
    logger.info(infos)
    logger.info(123)

    sleep(10)
    writeData(infos, 'post_output.txt')
    result = requests.post(postURL, headers=postHeader, json=infos)
    logger.info(result.content)
