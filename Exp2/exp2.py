# -*- coding: utf-8 -*-

# 导入相关库
import sys
from collections import defaultdict
from nltk.featstruct import Feature
from textblob import TextBlob  # 导入文本处理工具
from textblob import Word
import json
import math
from functools import reduce

postingsList = defaultdict(dict)  # 在posting list中存储term在每个doc中的TF with pairs (docID, tf)
Dictionary = defaultdict(dict)  # 在Dictionary中存储每个term的DF
numDocument = 0  # 总的文档数
# 对每个文档的评分
score_document = defaultdict(dict)


# 处理整个文本的函数
def get_postings():
    global Dictionary, numDocument, postingsList
    # 读入数据

    with open("data.txt", "r") as f:  # 打开文件
        data = f.readlines()  # 读取文件

    numDocument = len(data)
    usefulness = [",", "'", "‘", "“", "’", "-", "”", "——"]

    # 一行一行处理,其实就是处理一个文档，那么此处就要记录tf
    for line in data:
        # 大写转小写
        line = line.lower()
        line = json.loads(line)

        # 处理当前行得到tweetid和text文本
        tweetid = Word(line['tweetid'])
        text = TextBlob(line['text'] + " " + line['username']).words.singularize()
        texts = []  # 最终获得的文档
        for word in text:
            if word in usefulness:
                continue
            temp = Word(word)
            # temp = temp.lemmatize()  # 词形还原
            texts.append(temp)

        # 构建Dictionnary,统计term出现的文档数目
        tempset = set(texts)  # document中的单词
        for term in tempset:
            if term in Dictionary.keys():  # 若该term未出现在任何document中
                Dictionary[term].append(tweetid)
            else:
                Dictionary[term] = [tweetid]
            # 构建postingsList,统计每个term的tf
            if term not in postingsList:  # 还未统计文档中term的tf
                postingsList[term] = []
                postingsList[term].append(
                    [tweetid, texts.count(term)])
            else:
                postingsList[term].append(
                    [tweetid, texts.count(term)])


def input_query(query):
    # 处理输入数据，与terms中的term匹配
    query = query.lower()
    terms = TextBlob(query).words.singularize()
    res = []
    for term in terms:
        term = Word(term)
        # term = term.lemmatize()  # 词形还原
        res.append(term)
    return res


def doSearch():  # 查询
    global Dictionary, postingsList, score_document
    n = int(input("How many times do you want to check?"))
    for i in range(n):
        query = input_query(input("please input query： "))
        if not query:
            sys.exit()
        else:
            unique_query = set(query)
            temp = []
            for term in unique_query:
                if len(Dictionary[term]) == 0:  # 这个term未出现在出现在文档中
                    temp.append(term)
            for term in temp:
                unique_query.remove(term)

            # 所有term都未出现
            if len(unique_query) == 0:
                print("no relevant document!")
                return
            # 相关文档
            relevant_tweetids = []
            for term in unique_query:
                for i in Dictionary[term]:
                    relevant_tweetids.append(i)
            relevant_tweetids = set(relevant_tweetids)

            print("A total of " + str(len(relevant_tweetids)) + " related tweetid!")
            if not relevant_tweetids:
                print("No tweets matched any query terms for")

            query_tf = defaultdict(dict)
            query_df = defaultdict(dict)
            query_idf = defaultdict(dict)
            query_wtq = defaultdict(dict)

            for term in unique_query:
                # query中每个term的tf
                tf_raw = query.count(term)
                query_tf[term] = 1 + math.log10(tf_raw)
                # query中term的df
                query_df[term] = len(Dictionary[term])
                # query中term的idf
                query_idf[term] = math.log10(numDocument / query_df[term])
                # query的Wtq
                query_wtq[term] = query_tf[term] * query_idf[term]

            # 遍历所有的相关文档
            for doc in relevant_tweetids:
                doc_tf = defaultdict(dict)
                doc_wtd = defaultdict(dict)
                normalizer = 0
                for term in unique_query:
                    for item in postingsList[term]:
                        if item[0] == doc:
                            tf_raw = item[1]
                            doc_tf[term] = 1 + math.log10(tf_raw)
                            normalizer += (doc_tf[term] ** 2)
                        else:
                            doc_tf[term] = 0
                # 归一化
                for term in unique_query:
                    doc_wtd[term] = doc_tf[term] / math.sqrt(normalizer)

                # 文档评分
                for term in unique_query:
                    if doc not in score_document:
                        score_document[doc] = query_wtq[term] * doc_wtd[term]
                    else:
                        score_document[doc] = score_document[doc] + query_wtq[term] * doc_wtd[term]

            # 排序输出
            score = sorted(score_document.items(), key=lambda x: x[1], reverse=True)
            print("Output the top 10 document_id:")
            for i in range(10):
                print("tweetid:", score[i][0], "score:", score[i][1])


def main():
    get_postings()
    doSearch()


if __name__ == "__main__":
    main()
