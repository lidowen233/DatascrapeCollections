import jieba
import re
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from wordcloud import WordCloud
from matplotlib import font_manager
import random
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from predict import SentimentAnalysis

class TFID():


    def drawWordCloud(wordsDict,bg_image_path,font_path):
        """
        生成词云。
        1.配置WordCloud。2.plt进行显示
        :return:
        """
        # 设置背景图片
        back_coloring = np.array(Image.open(bg_image_path))

        # 设置词云属性
        wc = WordCloud(font_path=font_path, 
                       background_color="white", 
                       max_words= 200, 
                       mask= back_coloring,  
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
        wc.to_file("wordcloud.jpg")


    def getTfIdfRank(self,file_path=''):
        x = self.loadData(file_path)
        tfidf = TfidfVectorizer()  # 得到 TF-IDF 矩阵
        weight = tfidf.fit_transform(x)
        weight = weight.toarray()
        word = tfidf.get_feature_names_out() 
        word_fre = {}
        for i in range(len(weight)):
            for j in range(len(word)):
                if word[j] not in word_fre:
                    word_fre[word[j]] = weight[i][j]
                else:
                    word_fre[word[j]] = max(word_fre[word[j]], weight[i][j])

        print(sorted(word_fre.items(), key = lambda kv:(kv[1], kv[0])))

        return word_fre

    # 去除停用词
    def moveStopwords(self,sentence_list, stopwords_list):
       
        out_list = []
        for word in sentence_list:
            if word not in stopwords_list:
                if not self.removeDigits(word):
                    continue
                if word != '\t':
                    out_list.append(word)
        return out_list

    # 创建停用词列表
    def getStopwordsList(self):
        stopwords = [line.strip() for line in open('cn_stopwords.txt', encoding='UTF-8').readlines()]
        return stopwords

    # 对句子进行中文分词
    def segDepart(self, sentence):
        
        sentence_depart = jieba.lcut(sentence.strip())
        return sentence_depart

    def removeDigits(self, input_str):
        punc = u'0123456789.'
        output_str = re.sub(r'[{}]+'.format(punc), '', input_str)
        return output_str

    def loadData(self,filepath):
        data = pd.read_excel(filepath, sheet_name='Sheet1')
        text = []
        stop_list = self.getStopwordsList()
        for i in range(len(data)):
            str_row = data.iloc[i, 3]
            str_row = self.segDepart(str_row)
            line_without = self.moveStopwords(str_row, stop_list)
            lineStr = ' '.join(line_without)
            text.append(lineStr)
        return text
