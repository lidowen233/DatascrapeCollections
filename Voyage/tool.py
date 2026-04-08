import datetime
import logging
import random

import colorlog
import cv2
import xlrd
from PIL import Image
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

log_colors_config = {
    'DEBUG': 'white',  # cyan white
    'INFO': 'white',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

logger = logging.getLogger('logger_name')

# 输出到控制台
console_handler = logging.StreamHandler()
# 输出到文件
file_handler = logging.FileHandler(filename='output.log', mode='a', encoding='utf8')

# 日志级别，logger 和 handler以最高级别为准，不同handler之间可以不一样，不相互影响
logger.setLevel(logging.INFO)
file_handler.setLevel(logging.INFO)

# 日志输出格式
file_formatter = logging.Formatter(
    fmt='[%(asctime)s.%(msecs)03d] [%(levelname)s] : %(message)s',
    datefmt='%Y-%m-%d  %H:%M:%S'
)

console_formatter = colorlog.ColoredFormatter(
    fmt='%(log_color)s[%(asctime)s.%(msecs)03d] [%(levelname)s] : %(message)s',
    datefmt='%Y-%m-%d  %H:%M:%S',
    log_colors=log_colors_config
)
console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)

# 重复日志问题：
# 1、防止多次addHandler；
# 2、loggername 保证每次添加的时候不一样；
# 3、显示完log之后调用removeHandler
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

console_handler.close()
file_handler.close()


class GeneralTool():
    def trimNumber(self, str):
        result = ''
        for s in str:
            if (s.isdigit()):
                result += s
        # print(result)
        return result

    def trimStrWithStr(self, str, str1):
        result = ''
        length = len(str)
        pos = str.find(str1, 0, length)
        result = str[pos + len(str1):length]
        # print(result)
        return result

    def getContent(self, str, str1):
        strs = str.split(str1)
        return strs[1]

    # 获取船公司的网站
    def getWebsiteByCarrier(self, carrier, tracking_no):
        carrierPath = '副本船公司.xls'
        wb = xlrd.open_workbook(carrierPath)
        sheet = wb.sheet_by_index(0)
        rows = sheet.nrows
        for i in range(1, rows):
            carrierName = sheet.cell(i, 1).value
            if (carrier == carrierName):
                web = sheet.cell(i, 3).value
                if (carrier == 'ZIM'):
                    strs = web.split('\n')
                    zimStr = strs[1]
                    gosStr = strs[3]
                    if (tracking_no.startswith('ZIM')):
                        web = zimStr
                    else:
                        web = gosStr

                if (web.find('\n')):
                    strs = web.split('\n')
                    web = strs[0]
                # logger.info(web)
                return web

    def getMonth(self, str):
        str = str.upper()
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        return months.index(str) + 1

    def getTime(self, str):
        strs = str.split(':')
        hour = strs[0]
        minute = strs[1]
        if (len(strs) > 2):
            second = strs[2]
        else:
            second = '00'
        time = hour + minute + second
        return time

    def deleteTheFirstBlank(self, str):
        pos = 0
        for i in range(0, len(str)):
            if (str[i] == ' '):
                pos += 1

            else:
                break
        return str[pos:len(str)]

    def dealWithDateWithChinese(self, dateStr):
        yearIndex = dateStr.find('年')
        monthIndex = dateStr.find('月')
        dayIndex = dateStr.find('日')
        if (yearIndex != -1):
            year = dateStr[0:yearIndex]
            month = dateStr[yearIndex + 1:monthIndex]
            day = dateStr[monthIndex + 1:dayIndex]
            if (dateStr.find(' ') != -1):
                time = dateStr.split(' ')[1]
                if (time.find(':') != -1):
                    hour = time.split(':')[0]
                    minute = time.split(':')[1]
                    time = hour + minute
                    date = year + month + day + time
                    dt = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
                    dt_date = milliseconds = int(round(dt.timestamp() * 1000))
                    return dt_date
            else:
                return 0
        else:
            return 0

    def dealWithDate(self, datestr):
        datestr = self.deleteTheFirstBlank(datestr)
        date = ''
        if (datestr == ''):
            return 0
        if (datestr.isdigit()):
            dt = datetime.datetime.strptime(datestr, '%Y%m%d%H%M%S')
            dt_date = int(round(dt.timestamp() * 1000))
            return dt_date
        if (datestr.find('-') != -1):
            strs = datestr.split('-')
            if (strs[0].isalpha()):
                # APR-14-2023
                day = strs[1]
                year = strs[2]
                month = self.getMonth(strs[0])
                if (month < 10):
                    monthStr = '0' + str(month)
                else:
                    monthStr = str(month)

                date = year + monthStr + day
                time = '000000'
                date = date + time
                dt = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
                dt_date = int(round(dt.timestamp() * 1000))
                return dt_date
            elif (strs[1].isalpha()):
                # 14-APR-23
                if (strs[0].find('.') != -1):
                    # Tue.18-APR-2023
                    dayStr = strs[0]
                    dayStrs = dayStr.split('.')
                    day = dayStrs[1]
                else:
                    day = strs[0]
                if (len(day) == 1):
                    day = '0' + day
                if (len(strs[2]) == 2):
                    year = '20' + strs[2]
                else:
                    year = strs[2]
                month = self.getMonth(strs[1])
                if (month < 10):
                    monthStr = '0' + str(month)
                else:
                    monthStr = str(month)
                date = year + monthStr + day + '000000'
                dt = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
                dt_date = int(round(dt.timestamp() * 1000))
                return dt_date
            else:
                # 03-03-2023
                if (datestr.find(':') == -1):
                    day = strs[0]
                    year = strs[2]
                    month = strs[1]
                    date = year + month + day + '000000'
                    dt = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
                    dt_date = int(round(dt.timestamp() * 1000))
                    return dt_date
                else:
                    # 2023-03-14 01:30
                    year = strs[0]
                    month = strs[1]
                    dayStr = strs[2]
                    if (dayStr.find(' ') != -1):
                        day = dayStr.split(' ')[0]
                        timeStr = dayStr.split(' ')[1]
                        hour = timeStr.split(':')[0]
                        minute = timeStr.split(':')[1]
                        second = '00'
                        time = hour + minute + second
                        date = year + month + day + time
                        dt = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
                        dt_date = int(round(dt.timestamp() * 1000))
                        return dt_date
        else:
            if (datestr.find('/') != -1):
                if (datestr.find(' ') != -1):
                    # 2023/1/23 13:52:00
                    dateStr = datestr.split(' ')[0]
                    dateStrs = dateStr.split('/')
                    year = dateStrs[0]
                    month = dateStrs[1]
                    day = dateStrs[2]

                    if (len(month) == 1):
                        month = '0' + month
                    if (len(day) == 1):
                        day = '0' + day

                    time = self.getTime(datestr.split(' ')[1])
                    date = year + month + day + time
                    dt = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
                    dt_date = int(round(dt.timestamp() * 1000))
                    return dt_date
                else:
                    dateStrs = datestr.split('/')
                    year = dateStrs[2]
                    month = dateStrs[1]
                    day = dateStrs[0]
                    time = '000000'
                    date = year + month + day + time
                    dt = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
                    dt_date = int(round(dt.timestamp() * 1000))
                    return dt_date
            else:
                # 17 APR 2023 15:30
                if (datestr.find(' ') != -1):
                    dateStrs = datestr.split(' ')
                    year = dateStrs[2]
                    if (year.find(',') != -1):
                        # 23 Mar 2023, 04:04 CCT
                        comaIndex = year.find(',')
                        year = year[0:comaIndex]
                    month = self.getMonth(dateStrs[1])
                    day = dateStrs[0]
                    time = dateStrs[3]
                    if (time.find(':') != -1):
                        hour = time.split(':')[0]
                        minute = time.split(':')[1]
                        if (minute.find(' ') != -1):
                            # 23 Mar 2023, 04:04 CCT
                            minute = minute.split(' ')[0]
                        time = hour + minute
                    if (month < 10):
                        monthStr = '0' + str(month)
                    else:
                        monthStr = str(month)
                    if (len(day) == 1):
                        day = '0' + day
                    date = year + monthStr + day + time
                    dt = datetime.datetime.strptime(date, '%Y%m%d%H%M')
                    dt_date = int(round(dt.timestamp() * 1000))
                    return dt_date

    def get_sliceX(self, slice_imgpath):
        "获取滑块的位置，滑块左边缘X坐标"
        slice_img = Image.open(slice_imgpath)
        w, h = slice_img.size
        # 滑块为彩色，其余地方为白色
        for x in range(w):
            for y in range(h):
                rgb = slice_img.getpixel((x, y))
                value = rgb[0] + rgb[1] + rgb[2]  # 740
                # print((x,y),value)
                if value < 570:
                    return x

    def get_track(self, distance):
        '''
        获得移动轨迹，模仿人的滑动行为，先匀加速后匀减速匀变速运动基本公式:
        ①v=v0+at
        ②s=v0t+0.5at^2
        :param distance: 需要移动的距离
        :return: 每0.2s移动的距离
        '''
        # 初速度
        v0 = 0
        # 单位时间0.2s
        t = 0.2
        # 轨迹列表，每个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 达到mid开始减速
        mid = distance * 5 / 8
        # 先滑过一点，最后再反着滑动回来
        # distance += 10
        while current < distance:
            # 增加运动随机性
            t = random.randint(1, 4) / 10
            if (current < mid):
                # 加速度越小，单位时间的位移越小，模拟的轨迹就越多越详细
                a = random.randint(2, 7)  # 加速运动
            else:
                a = -random.randint(2, 6)  # 减速运动
            # 0.2s时间的位移
            s = v0 * t + 0.5 * a * (t ** 2)

            # 当前位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))
            # 当前速度，作为下次的初速度
            v0 = v0 + a * t

        return tracks

    def move_slice(self, path, distance, driver):
        elem = driver.find_element(By.XPATH, path)
        ActionChains(driver).click_and_hold(elem).perform()
        tracks = self.get_track(distance)
        for track in tracks:
            ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()
        ActionChains(driver).release(elem).perform()

    def identify_gap(self, bg, tp, out):

        # 读取背景图片和缺口图片
        bg_img = cv2.imread(bg)  # 背景图片
        tp_img = cv2.imread(tp)  # 缺口图片

        # 识别图片边缘
        bg_edge = cv2.Canny(bg_img, 100, 200)
        tp_edge = cv2.Canny(tp_img, 100, 200)

        # 转换图片格式
        bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
        tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)

        # 缺口匹配
        res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配

        # 绘制方框
        th, tw = tp_pic.shape[:2]
        tl = max_loc  # 左上角点的坐标
        br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
        cv2.rectangle(bg_img, tl, br, (0, 0, 255), 2)  # 绘制矩形
        cv2.imwrite(out, bg_img)  # 保存在本地
        print(tl)
        # 返回缺口的X坐标
        return tl[0]

    def find_pic(target='background.png', template='slice.png'):
        try:
            # 比较图片以找出距离
            # 读取背景图片
            target_rgb = cv2.imread(target)
            # 灰度处理
            target_gray = cv2.cvtColor(target_rgb, cv2.COLOR_BGR2GRAY)

            # 读取滑块图片
            template_rgb = cv2.imread(template, 0)
            # 比较位置
            res = cv2.matchTemplate(target_gray, template_rgb, cv2.TM_CCOEFF_NORMED)
            # 获得结果
            distance = cv2.minMaxLoc(res)
            print('方法2', distance)
            return distance[2][0]
        except Exception as error:
            print('破解函数出错')
            print(error)

    def show(self, name):
        '''展示圈出来的位置'''
        cv2.imshow('Show', name)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def _tran_canny(self, image):
        """消除噪声"""
        image = cv2.GaussianBlur(image, (3, 3), 0)
        return cv2.Canny(image, 50, 150)

    def detect_displacement(self, img_slider_path, image_background_path):
        """detect displacement"""
        # # 参数0是灰度模式
        image = cv2.imread(img_slider_path, 0)
        template = cv2.imread(image_background_path, 0)

        # 寻找最佳匹配
        res = cv2.matchTemplate(self._tran_canny(image), self._tran_canny(template), cv2.TM_CCOEFF_NORMED)
        # 最小值，最大值，并得到最小值, 最大值的索引
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        top_left = max_loc[0]  # 横坐标
        # 展示圈出来的区域
        x, y = max_loc  # 获取x,y位置坐标

        w, h = image.shape[::-1]  # 宽高
        cv2.rectangle(template, (x, y), (x + w, y + h), (7, 249, 151), 2)
        # show(template)
        return top_left

    def header_x(self):
        # 随机获取一个headers
        user_agents = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0'
        ]

        headers = {
            "User-Agent": random.choice(user_agents)
        }
        logger.info(f'使用的header{random.choice(user_agents)}')
        return random.choice(user_agents)