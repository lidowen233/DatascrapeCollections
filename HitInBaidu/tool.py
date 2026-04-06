import re
import datetime
from selenium.webdriver.chrome.options import Options
import xlrd
from xlutils.copy import copy
#from main import weibo_cols,cols,path

path = '热搜.xlsx'
cols = ['日期','链接','标题']
months = ['12','1','2']
weibo_cols = ['关键词','发博时间','发博用户','博文内容','点赞','转发','评论','url']

class ToolGeneral():

    """
    Tool function
    """

    def is_odd(self, num):
        if num % 2 == 0:
            return 'even'
        else:
            return 'odd'

    def load_dict(self, file):
        """
        Load dictionary
        """
        with  open(file, encoding='utf-8', errors='ignore') as fp:
            lines = fp.readlines()
            lines = [l.strip() for l in lines]
            print("Load data from file (%s) finished !" % file)
            dictionary = [word.strip() for word in lines]
        return set(dictionary)

    def sentence_split_regex(self, sentence):
        """
        Segmentation of sentence
        """
        if sentence is not None:
            sentence = re.sub(r"&ndash;+|&mdash;+", "-", str(sentence))
            sub_sentence = re.split(r"[。,，！!？?;；\s…~～]+|\.{2,}|&hellip;+|&nbsp+|_n|_t", sentence)
            sub_sentence = [s for s in sub_sentence if s != '']
            if sub_sentence != []:
                return sub_sentence
            else:
                return [sentence]
        return []

    def hasNumerAtHead(self,strs):

        if (strs[0].isdigit()):
            return True
        else:
            return False

    def deleteNumerAtHead(self,strs):
        strs_new = ''
        if ('.' in strs):
            index = strs.index('.')
            strs_new = strs[index + 1:]
        else:
            if ('：' in strs):
                index = strs.index('：')
                strs_new = strs[index + 1:]
        return strs_new



    def dealDateFormat(self,date_str):
        date_strs = date_str.split('-')
        date_str = date_strs[0] + '年'  # + date_strs[1] + '月'

        if (date_strs[1].startswith('0')):
            date_str = date_str + date_strs[1][1] + '月'
        else:
            date_str = date_str + date_strs[1] + '月'

        if (date_strs[2].startswith('0')):
            date_str = date_str + date_strs[2][1] + '日'
        else:
            date_str = date_str + date_strs[2] + '日'

        return date_str

    def dealUrlFormat(self,url):

        if (url == ''):
            return ''
        else:
            if ('/' in url):
                urls = url.split('/')
                return urls[3]

    def getDateFromUrl(self,url):
        # https://www.xianlewang.cn/article/details/20230103200001700726
        urls = url.split('/')
        return urls[5][0:8]

    def getDates(self,str1, str2):
        str1 = '2022-12-1'
        str2 = '2023-02-28'

        start_date = datetime.datetime.strptime(str1, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(str2, '%Y-%m-%d')

        date_list = []
        while start_date <= end_date:
            date_str = start_date.strftime("%Y-%m-%d")

            date_list.append(self.dealDateFormat(date_str))

            start_date += datetime.timedelta(days=1)

        print(date_list)
        return date_list  # 2022-12-02

    def writeNewDataToSheetBaidu(self,value):
        """
        插入数据到表格里面
        :param value : 具体的数据

        """
        workbook = xlrd.open_workbook(path)
        sheets = workbook.sheet_names() 
        worksheet = workbook.sheet_by_name(sheets[0])  
        rows_old = worksheet.nrows  

        new_workbook = copy(workbook) 
        new_worksheet = new_workbook.get_sheet(0)  

        length = len(cols)
        for i in range(1, rows_old):
            if (value[0] == worksheet[i][0]):
                return

        for j in range(0, length):
            new_worksheet.write(rows_old, j, value[j]) 

        new_workbook.save(path)  # 保存工作簿

    def writeNewDataToSheetWeibo(self,value):
        """
        插入数据到表格里面
        :param value : 具体的数据

        """
        workbook = xlrd.open_workbook(path)  
        sheets = workbook.sheet_names()  
        worksheet = workbook.sheet_by_name(sheets[1])  
        rows_old = worksheet.nrows  

        new_workbook = copy(workbook)  
        new_worksheet = new_workbook.get_sheet(1)  

        length = len(weibo_cols)
        for i in range(1, rows_old):
            if (value[1] == worksheet[i][1] and value[2] == worksheet[i][2]):
                return

        for j in range(0, length):
            new_worksheet.write(rows_old, j, value[j])  

        new_workbook.save(path)  
