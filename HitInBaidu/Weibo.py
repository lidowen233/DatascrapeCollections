import datetime
import requests
from bs4 import BeautifulSoup as BS
from tool import ToolGeneral


tool = ToolGeneral()
def getInfoInWeibo():
    start_date = '2022-12-01'
    end_date = '2023-02-28'

    dates = []
    dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    date = start_date[:]
    while date <= end_date:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")

    keywords = ['阳了','抗疫日记','新冠','疫情','核酸','封控']
    for keyword in keywords:
        for date in dates:  # 循环这一年的每天
            for i in range(1, 51):
                url = f'https://s.weibo.com/weibo?q={keyword}&typeall=1&suball=1&timescope=custom%3A{date}-0%3A{date}-23&Refer=g&page={i}'
                headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'zh-CN,zh;q=0.9',
                    'cache-control': 'max-age=0',
                    # 这里需要输入自己登陆的时候的cookie
                    'cookie': 'SINAGLOBAL=4810247458846.588.1680700069320; _s_tentry=login.sina.com.cn; UOR=,,login.sina.com.cn; Apache=727227822124.6942.1680960755195; ULV=1680960755262:3:3:3:727227822124.6942.1680960755195:1680948511332; XSRF-TOKEN=6LISGMZV6TQBFCvatPn0J5ku; SCF=AmIO9P4-CT4E32xpg-Pezm3FekshkYyGDs69I1YD09xLseOi_zCPXOBOAv9MIodfjUMTfLNkg4d3HvXDEDJsVcU.; SUB=_2A25JNQBsDeRhGeFN4loS9ynOyjyIHXVqQ3akrDV8PUNbmtANLXatkW9NQ7hLSxhT21oRgaqGahOzKf_q7Y9oDDrU; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Whdy5ceXwTvYqa___S8JwmI5JpX5KzhUgL.FoM01Kn0S0MEeK52dJLoIXnLxKBLB.2L1-2LxK-L1h-LBo.LxKqL12zL1h.LxKqL1KqL1K5LxK-LBo5L1KBLxKqLBozLBK2LxKqL1-eL1h.LxKML12zL1KMt; ALF=1712497595; SSOLoginState=1680961596; WBPSESS=Dt2hbAUaXfkVprjyrAZT_PxOZOnJ2uiDiXjg_FU8rLw40HG7HFRJE5I79srilo2BmF-xVVb9kW-alg0jtz9tgvobO5YINPb5mN3mRysujB_ooFasZYmfhKGsy_kz5mktELRqsKWd5nybR0iHcVYnWAboplBdNImb5NELpW1bNkHbeywo7OLMT3lUq8Jhz_rps_yjr1_lxaG3SERTph2g4w==',
                    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
                }
                ss = requests.session()
                ss.keep_alive = False
                while 1:
                    try:
                        html0 = ss.get(url=url, headers=headers, timeout=(3, 3)).text
                        break
                    except:
                        pass

                t = BS(html0, 'lxml')
                try:
                    pdd = t.find('div', class_="card card-no-result s-pt20b40")  # 如果找没有信息到直接跳出程序
                    if pdd != None:
                        break
                except:
                    pdd = ''
                card = t.find_all('div', class_="card-wrap")

                for p in card:

                    try:
                        txt = str(p.find_all('p', class_="txt")[-1].text).replace('\n', '').replace('\u200b',
                                                                                                    '').replace('收起d',
                                                                                                                '').replace(
                            ' ', '')
                        pl = str(p.find_all('a', class_="woo-box-flex woo-box-alignCenter woo-box-justifyCenter")[
                                     -2].text).replace(' ', '')
                        name = p.find('a', class_="name").text
                        time = str(p.find('div', class_="from").text).replace(' ', '').replace('\n', '').replace('\xa0',
                                                                                                                 '')
                        urls = 'https:' + p.find('div', class_="from").a['href']
                        ti = time.split('来自')[0]
                        dz = str(p.find_all('span', class_="woo-like-count")[-1].text).replace(' ', '')
                        zf = str(p.find_all('a', class_="woo-box-flex woo-box-alignCenter woo-box-justifyCenter")[
                                     -3].text).replace(' ', '')
                        infos = []
                        # ['关键词','发博时间','发博用户','博文内容','点赞','转发','评论','url']
                        infos.append(keyword)
                        infos.append(ti)
                        infos.append(name)
                        infos.append(txt)
                        infos.append(dz)
                        infos.add(zf)
                        infos.add(pl)
                        infos.append(urls)
                        print(infos)
                        tool.writeNewDataToSheetWeibo(infos)

                    except:
                        pass

if __name__ == '__main__':
    getInfoInWeibo()