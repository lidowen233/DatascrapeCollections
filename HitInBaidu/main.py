
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from predict import SentimentAnalysis
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
import jieba
import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import datetime
from wordcloud import WordCloud
import matplotlib.ticker as ticker
from sklearn.feature_extraction.text import TfidfVectorizer
from predict import SentimentAnalysis
from sklearn.cluster import MiniBatchKMeans



path = '热搜.xlsx'
cols = ['日期','链接','标题']
months = ['12','1','2']
weibo_cols = ['关键词','发博时间','发博用户','博文内容','点赞','转发','评论','url']
#['关键词','发博时间','发博用户','博文内容','url']
font_path = 'SIMHEI.TTF'
# 词云的背景图片
bg_image_path = 'alice.png'
my_font = font_manager.FontProperties(fname=font_path)




# 获得情感分析
def getSentimentlist(filepath,type = 1):
    '''
    :param filepath:
    :param type: 百度=1，微博=0
    :return:
    '''
    types= ['微博','百度']
    SA = SentimentAnalysis()
    sentiments = []
    data = pd.read_excel(filepath, sheet_name=types[type])
    for i in range(len(data)):
        if(type == 1):
            str_row = data.iloc[i, 2]
        else:
            str_row = data.iloc[i, 3]
        sentiments.append(SA.predict(str_row))
    positive = 0
    negative = 0
    middle = 0
    for sen in sentiments:
        if(sen<0):
            negative = negative + 1
        elif (sen == 0):
            middle = middle + 1
        else:
            positive = positive + 1

    sentiments_copy = []
    sentiments_copy.append(positive)
    sentiments_copy.append(negative)
    sentiments_copy.append(middle)
    plt.rcParams['font.sans-serif'] = ["SimHei"]
    # 绘制饼状图
    plt.pie(sentiments_copy,
            labels=['积极', '消极', '中性'],  # 设置饼图标签
            autopct="(%1.1f%%)",  # 饼块内标签。
    )
    plt.title(f"{types[type]}情感分析饼状图")
    plt.savefig(f'{types[type]}情感分析饼状图.png')

    plt.show()  # 显示饼状图


def loadData(filepath,type):
    '''

    :param filepath:
    :param type: 微博 or 百度
    :return:
    '''
    data = pd.read_excel(filepath, sheet_name=type)
    text = []
    stop_list = getStopwordsList()
    for i in range(len(data)):
        if(type == '百度'):
            str_row = data.iloc[i, 2]
        else:
            str_row = data.iloc[i, 3]

        str_row = segDepart(str_row)
        line_without = moveStopwords(str_row, stop_list)

        stop_listBaidu = getStopwordsBaiduList()
        line_without = moveStopwords(line_without, stop_listBaidu)

        lineStr = ' '.join(line_without)
        text.append(lineStr)
    return text

def loadDataByKeyword(filepath,type,keyword):
    '''
    :param filepath:
    :param type: 微博
    :param keyword: 关键词
    :return:
    '''
    data = pd.read_excel(filepath, sheet_name=type)
    text = []
    stop_list = getStopwordsList()
    for i in range(len(data)):
        if(type == '百度'):
            str_row = data.iloc[i, 2]
        else:
            str_row = data.iloc[i, 3]

        str_row = segDepart(str_row)
        line_without = moveStopwords(str_row, stop_list)

        stop_listBaidu = getStopwordsBaiduList()
        line_without = moveStopwords(line_without, stop_listBaidu)

        lineStr = ' '.join(line_without)
        if(keyword == data.iloc[i,0]):
            text.append(lineStr)
    return text

# 创建停用词列表
def getStopwordsList():
    stopwords = [line.strip() for line in open('cn_stopwords.txt',encoding='UTF-8').readlines()]
    return stopwords
def getStopwordsBaiduList():
    stopwords = [line.strip() for line in open('baidu_stopwords.txt',encoding='UTF-8').readlines()]
    return stopwords

# 对句子进行中文分词
def segDepart(sentence):
    sentence_depart = jieba.lcut(str(sentence).strip())
    return sentence_depart
def removeDigits(input_str):
    punc = u'0123456789.'
    output_str = re.sub(r'[{}]+'.format(punc), '', input_str)
    return output_str

# 去除停用词
def moveStopwords(sentence_list, stopwords_list):
    out_list = []
    for word in sentence_list:
        if word not in stopwords_list:
            if not removeDigits(word):
                continue
            if word != '\t':
                out_list.append(word)
    return out_list

def getTfIdfRank(file_path,type):
    '''
    :param file_path: 热搜.xlsx
    :param type: 微博 or 百度
    :return:
    '''
    start = datetime.datetime.now()
    x = loadData(file_path,type)
    tfidf = TfidfVectorizer()  # 得到 TF-IDF 矩阵
    weight = tfidf.fit_transform(x)
    weight = weight.toarray()
    word = tfidf.get_feature_names_out()
    word_fre = {}
    maxweight = np.max(weight, axis=0)
    for j in range(len(word)):
        if word[j] not in word_fre:
            word_fre[word[j]] = maxweight[j]
        else:
            word_fre[word[j]] = word_fre[word[j]] + maxweight[j]

    print(sorted(word_fre.items(), key=lambda kv: (kv[1], kv[0])))
    end = datetime.datetime.now()
    print('用了',end - start)
    return word_fre

def getTfIdfRankByKeyword(file_path,type,keyword,word_fre):
    '''
    :param file_path: 热搜.xlsx
    :param type: 微博
    :param word_fre: 字典
    :param keyword: 关键词
    :return:
    '''
    start = datetime.datetime.now()
    x = loadDataByKeyword(file_path,type,keyword)
    tfidf = TfidfVectorizer()  # 得到 TF-IDF 矩阵
    weight = tfidf.fit_transform(x)
    maxweight = np.max(weight, axis=0)
    maxweight = maxweight.toarray()[0]

    word = tfidf.get_feature_names_out() # 得到不重复的关键词
    for j in range(len(word)):
        if word[j] not in word_fre:
            word_fre[word[j]] = maxweight[j]
        else:
            word_fre[word[j]] = word_fre[word[j]] + maxweight[j]

    #print(sorted(word_fre.items(), key=lambda kv: (kv[1], kv[0])))
    end = datetime.datetime.now()
    print('-------', keyword,'用了',end - start)


def loadDataByMonth(file_path,type,monthIndexx):
    '''
    :param file_path: 热搜.xlsx
    :param type: 微博 or 百度
    :return:
    '''
    data = pd.read_excel(file_path, sheet_name=type)
    text = []
    stop_list = getStopwordsList()
    for i in range(len(data)):

        if (type == '百度'):
            month = data.iloc[i, 0]
            monthstr = str(month)[4:6]
            str_row = data.iloc[i, 2]
        else:
            month = data.iloc[i, 1]
            if('年' in month):
                indexY = month.index('年')
                indexM = month.index('月')
                monthstr = month[indexY+1:indexM]
            else:
                indexM = month.index('月')
                monthstr = month[0:indexM]

            str_row = data.iloc[i, 3]

        if(months[monthIndexx] in monthstr):
            str_row = segDepart(str_row)
            line_without = moveStopwords(str_row, stop_list)

            stop_listBaidu = getStopwordsBaiduList()
            line_without = moveStopwords(line_without, stop_listBaidu)

            lineStr = ' '.join(line_without)
            text.append(lineStr)
    return text

def loadDataByMonthAndKeyword(file_path,type,monthIndex,keyword):
    '''
    :param file_path: 热搜.xlsx
    :param type: 微博 or 百度
    :param monthIndex: 月份
    :keyword: 关键词
    :return:
    '''
    data = pd.read_excel(file_path, sheet_name=type)
    text = []
    stop_list = getStopwordsList()
    for i in range(len(data)):

        if (type == '百度'):
            month = data.iloc[i, 0]
            monthstr = str(month)[4:6]
            str_row = data.iloc[i, 2]
        else:
            month = data.iloc[i, 1]
            if('年' in month):
                indexY = month.index('年')
                indexM = month.index('月')
                monthstr = month[indexY+1:indexM]
            else:
                indexM = month.index('月')
                monthstr = month[0:indexM]

            str_row = data.iloc[i, 3]

        if(months[monthIndex] in monthstr):
            str_row = segDepart(str_row)
            line_without = moveStopwords(str_row, stop_list)

            stop_listBaidu = getStopwordsBaiduList()
            line_without = moveStopwords(line_without, stop_listBaidu)

            lineStr = ' '.join(line_without)
            if(data.iloc[i, 0] == keyword):
                text.append(lineStr)
    return text

def getTfIdfRankByMonth(file_path,type,monthIndex):
    '''
    :param file_path: 热搜.xlsx
    :param type: 微博 or 百度
    :param monthIndex: 几月
    :return:
    '''

    x= loadDataByMonth(file_path,type,monthIndex)
    tfidf = TfidfVectorizer()  # 得到 TF-IDF 矩阵
    weight = tfidf.fit_transform(x)
    weight = weight.toarray()
    word = tfidf.get_feature_names_out() # 得到不重复的关键词
    print(word)
    print("大小是 ",len(word)," ",len(weight))
    word_fre = {}
    maxweight = np.max(weight,axis = 0)
    for j in range(len(word)):
        if word[j] not in word_fre:
            word_fre[word[j]] = maxweight[j]
        else:
            word_fre[word[j]] = word_fre[word[j]] + maxweight[j]
    print(sorted(word_fre.items(), key = lambda kv:(kv[1], kv[0])))
    return word_fre

def getTfIdfRankByMonthAndKeyword(file_path,type,monthIndex,keyword,word_fre):
    '''
    :param file_path: 热搜.xlsx
    :param type: 微博 or 百度
    :param monthIndex: 几月
    :param keyword: 关键词
    :param word_fre: 返回的字典
    :return:
    '''
    start = datetime.datetime.now()
    x= loadDataByMonthAndKeyword(file_path,type,monthIndex,keyword)
    tfidf = TfidfVectorizer()  # 得到 TF-IDF 矩阵
    weight = tfidf.fit_transform(x)
    weight = weight.toarray()
    word = tfidf.get_feature_names_out() # 得到不重复的关键词
    print(word)
    print("大小是 ",len(word)," ",len(weight))
    maxweight = np.max(weight,axis = 0)
    for j in range(len(word)):
        if word[j] not in word_fre:
            word_fre[word[j]] = maxweight[j]
        else:
            word_fre[word[j]] = word_fre[word[j]] + maxweight[j]
    end = datetime.datetime.now()
    print('-------', keyword, '用了', end - start)
    #print(sorted(word_fre.items(), key = lambda kv:(kv[1], kv[0])))



def drawWordCloud(wordsDict,type):
    """
    生成词云。
    1.配置WordCloud。2.plt进行显示
    :return:
    """
    # 设置背景图片
    #back_coloring = np.array(Image.open(bg_image_path))
    # 设置词云属性
    wc = WordCloud(font_path=font_path,  
                   background_color="white",  
                   max_words= 100, 
                   #mask= back_coloring,  
                   random_state=30, 
                   width= 800, 
                   height= 600, 
                   )

    # 根据频率生成词云
    wc.generate_from_frequencies(wordsDict)
    plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
    wc.to_file(f'{type}词云.jpg')

def drawWordCloudByMonth(wordsDict,type,monthIndex):
    """
    生成词云。
    1.配置WordCloud。2.plt进行显示
    :return:
    """

    # 设置词云属性
    wc = WordCloud(font_path=font_path,  # 设置字体,若是有中文的话，这句代码必须添加，不然会出现方框，不出现汉字
                   background_color="white",  
                   max_words= 100,  
                   #mask= back_coloring, 
                   random_state=30, 
                   width= 800, 
                   height= 600, 
                   )

    # 根据频率生成词云
    wc.generate_from_frequencies(wordsDict)
    # 显示图片
    plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
    # 保存到本地
    month = months[monthIndex]
    wc.to_file(f'{type}_{month}月词云.jpg')

def find_optimal_clusters(data, max_k):
    '''
    :param data: 输入文本
    :param max_k:
    :return: 最合适的cluster 数目 ： 目前是15
    '''
    iters = range(5, max_k + 1, 2)
    tfidf = TfidfVectorizer()  # 得到 TF-IDF 矩阵
    X_tfidf_lsa = tfidf.fit_transform(data)

    sse = []
    for k in iters:
        sse.append(
            MiniBatchKMeans(n_clusters=k, init="k-means++", init_size=1024, batch_size=2048, random_state=20).fit(
                X_tfidf_lsa).inertia_)


    plt.plot(iters, sse, marker='o')
    plt.savefig('sse.png')

def getKmeans(filepath,type):
    data = loadData(filepath,type)
    vectorizer_tfidf = TfidfVectorizer(max_df=0.5, min_df=2, use_idf=True)
    X_tfidf = vectorizer_tfidf.fit_transform(data)
    svd = TruncatedSVD(100)
    normalizer = Normalizer(copy=False)
    lsa = make_pipeline(svd, normalizer)
    X_tfidf_lsa = lsa.fit_transform(X_tfidf)

    # 由optimal计算获得
    km = KMeans(n_clusters=5, init='k-means++', max_iter=100, n_init=1, verbose=False)
    km_X_tfidf_lsa = km.fit(X_tfidf_lsa)

    labels = km_X_tfidf_lsa .predict(X_tfidf_lsa)
    print(labels)
    clusters = []
    for i in range(0,5):
        clusters.append([j for j, x in enumerate(labels) if x == i])
    clusterItems = []
    for cluster in clusters:
        clusterItems.append(len(cluster))
    print(clusterItems)

    print("Top terms per cluster:")
    original_space_centroids = svd.inverse_transform(km_X_tfidf_lsa.cluster_centers_)
    order_centroids = original_space_centroids.argsort()[:, ::-1]
    terms = vectorizer_tfidf.get_feature_names_out()
    tips = []
    # 每个聚类的高频词
    for i in range(5):
        print("Cluster %d:" % i, end='')
        print(len(original_space_centroids))
        tip = ''
        for ind in order_centroids[i, :3]:
            print(' %s' % terms[ind], end='')
            tip = tip + ' ' + terms[ind]
        tips.append(tip)


    plt.rcParams['font.sans-serif'] = ["SimHei"]
    # 绘制饼状图
    plt.pie(clusterItems,
            labels= tips,  # 设置饼图标签
            autopct="(%1.1f%%)",  # 饼块内标签。
            )
    plt.title(f"{type}聚类饼状图")
    plt.savefig(f'{type}聚类分析饼状图.png')
    plt.show()  # 显示饼状图


# 字符串-》数字
def atoi(s):
    s = s[::-1]
    num = 0
    for i, v in enumerate(s):
        t = '%s * 1' % v
        n = eval(t)
        num += n * (10 ** i)
    return num

# 微博点赞前十
def getTop10Kudos(filepath):
    data = pd.read_excel(filepath, sheet_name='微博')
    kudos = []
    kudos_copy = []
    details = []
    dates = []
    for i in range(len(data)):
        date = data.iloc[i, 1]
        kudo = 0
        if('赞' in data.iloc[i, 4]):
            kudo = 0
        else:
            kudo = atoi(data.iloc[i, 4])

        kudos.append(kudo)
        dates.append(date)
        kudos_copy.append(kudo)

    kudos.sort(reverse=True)
    top10Kudos = []
    top10Date = []

    for i in range(0,10):
        item = kudos[i]
        index = kudos_copy.index(item)
        date = dates[index]
        top10Kudos.append(item)
        top10Date.append(date)

    
    for i in range(len(top10Kudos)):
        plt.bar(top10Date[i], top10Kudos[i],width = 0.5,color = 'blue')
   
    plt.title("点赞top10微博柱状图",fontproperties= my_font)
    plt.xticks(top10Date, top10Date,rotation=10, fontproperties= my_font)
    plt.xlabel("微博发布时间",fontproperties= my_font)
    
    plt.ylabel("点赞量",fontproperties=my_font)
    plt.tick_params(labelsize=7)
    # 显示
    for a, b in zip(top10Date, top10Kudos):
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=6)  # fontsize表示柱坐标上显示字体的大小
    plt.savefig('柱状图.png')
    plt.show()

# 微博热度折线图
def getHitChange(filepath):
    data = pd.read_excel(filepath, sheet_name='微博')
    dailyHits = {}
    days = []
    for i in range(len(data)):
        date = data.iloc[i, 1]
        index = date.index('日')
        if ('年' not in date):
            day =  '2023年' + date[0: index + 1]
        else:
            day = date[0: index + 1]
        days.append(day)
    dailyHits = dict.fromkeys(days, 0)

    for i in range(len(data)):
        date = data.iloc[i, 1]

        index = date.index('日')
        if('年' not in date):
            day =  '2023年' + date[0: index + 1]
        else:
            day = date[0: index + 1]
        kudo = 0
        zhuanfa = 0
        pinglun = 0
        if(data.iloc[i, 4] != '赞'):
            kudo = atoi(data.iloc[i, 4])
        if (data.iloc[i, 5] != '转发'):
            zhuanfa = atoi(data.iloc[i, 5])
        if (data.iloc[i, 6] != '评论'):
            pinglun = atoi(data.iloc[i, 6])

        dailyHits[day] = dailyHits[day] + kudo + zhuanfa + pinglun

    print(dailyHits)
    dates = []
    for key in dailyHits.keys():
        date = datetime.datetime.strptime(key, '%Y年%m月%d日').date()
        dates.append(date)
    hits = []
    for value in dailyHits.values():
        hits.append(value)

    print(dates)
    plt.figure(figsize=(20, 8), dpi=80)
    plt.plot(dates, hits)
    ax = plt.gca()
    tick_spacing = 10
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    plt.title("话题热度变化折线图", fontproperties=my_font)
    plt.xticks(pd.date_range('2022-12-1', '2023-2-28', freq='5d'),rotation= 40,fontsize = 3)
    #plt.xticks(dates, dates, rotation= 90, fontproperties=my_font, fontsize = 3)
    plt.xlabel("微博发布时间", fontproperties=my_font)
    plt.ylabel("热度", fontproperties=my_font) # 热度 = 点赞 + 评论 + 转发
    plt.tick_params(labelsize=7)
    plt.savefig('热度变化折线图.png')
    plt.show()

def getBaiduWordCloudByMonth():
    # 百度
    for i in range(0, 3):
        type = '百度'
        word_fre = getTfIdfRankByMonth(path, type, i)
        drawWordCloudByMonth(word_fre, type, i)

def getWeiboWordCloudByMonth():
    # 微博
    for i in range(0, 3):
        type = '微博'
        keywords = ['阳了', '抗疫日记', '新冠', '疫情', '核酸', '封控']
        dics = {}
        for keyword in keywords:
            getTfIdfRankByMonthAndKeyword(path,type,i,keyword,dics)
        drawWordCloudByMonth(dics, type, i)

def getWeiboWordCloud():
    keywords = ['阳了', '抗疫日记', '新冠', '疫情', '核酸', '封控']
    dics = {}
    for keyword in keywords:
        getTfIdfRankByKeyword(path, '微博', keyword, dics)
    drawWordCloud(dics, '微博')

if __name__ == '__main__':

    # 用于获取拐点-》最佳cluster
    #data = loadData(path,'微博')
    #find_optimal_clusters(data,20)

    # kmeans 聚类
    #getKmeans(path,'百度')
    #getKmeans(path,'微博')

    # 热度变化
    #getHitChange(path)
    # top10点赞
    #getTop10Kudos(path)

    # 情感分析
    # 百度
    #getSentimentlist(path,1)
    # 微博
    getSentimentlist(path,0)

    # 总的词云图
    # 百度词云
    #dics = getTfIdfRank(path,'百度')
    #drawWordCloud(dics,'百度')
    # 微博词云
    #getWeiboWordCloud()


    # 获取每个月的词云
    #getBaiduWordCloudByMonth()
    #getWeiboWordCloudByMonth()



