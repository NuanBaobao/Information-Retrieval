# -*- coding: utf-8 -*-

# 导入相关库
import sys
from collections import defaultdict
from textblob import TextBlob  # 导入文本处理工具
from textblob import Word
import json


postings = defaultdict(dict)  # inverted index


# 处理整个文本的函数
def get_postings():
    global postings
    # 读入数据

    with open("data.txt", "r") as f:  # 打开文件
        data = f.readlines()  # 读取文件

    usefulness = [",", "'", "‘", "“", "’", "-", "”", "——"]

    # 一行一行处理
    for line in data:
        # 大写转小写
        line = line.lower()
        line = json.loads(line)

        # 处理当前行得到tweetid和text文本
        tweetid = Word(line['tweetid'])
        text = TextBlob(line['text'] + " " + line['username']).words.singularize()
        texts = []
        for word in text:
            if word in usefulness:
                continue
            temp = Word(word)
            # temp = temp.lemmatize()  # 词形还原
            texts.append(temp)

        # 构建postings表
        tempset = set(texts)
        for term in tempset:
            if term in postings.keys():
                postings[term].append(tweetid)
            else:
                postings[term] = [tweetid]
    # 建立完postings后要进行排序，方便后面优化查询
    for term in postings.keys():
        postings[term].sort()


def oneword(term):
    global postings
    return postings[term]


def op_and(term1, term2):
    global postings  # 全局变量
    res = []
    if (term1 not in postings) or (term2 not in postings):
        return res
    else:
        # 计算term1，term2对应postings数组的长度
        len1 = len(postings[term1])
        len2 = len(postings[term2])
        x = 0
        y = 0
        # 双指针算法
        while x < len1 and y < len2:
            if postings[term1][x] == postings[term2][y]:
                res.append(postings[term1][x])
                x += 1
                y += 1
            elif postings[term1][x] < postings[term2][y]:
                x += 1
            else:
                y += 1
        return res


def op_or(term1, term2):  # 或操作
    res = []
    if (term1 not in postings) and (term2 not in postings):
        return res
    elif term2 not in postings:
        res = postings[term1]
    elif term1 not in postings:
        res = postings[term2]
    else:  # term1,term2都存在    
        len1 = len(postings[term1])
        len2 = len(postings[term2])
        x = 0
        y = 0
        # 同样采用双指针
        while x < len1 and y < len2:
            if postings[term1][x] == postings[term2][y]:#两个词都在
                res.append(postings[term1][x])
                x += 1
                y += 1
            elif postings[term1][x] < postings[term2][y]:
                res.append(postings[term1][x])#term1中的词在
                x += 1
            else:
                res.append(postings[term2][y])
                y += 1
        if x < len1:#将未搜索完的加入
            while x < len1:
                res.append(postings[term1][x])
                x += 1
        if y < len2:
            while y < len2:
                res.append(postings[term2][y])
                y += 1
    return res


def op_not(term1, term2):  # 非操作
    res = []
    if term1 not in postings:
        return res
    elif term2 not in postings:
        res = postings[term1]
        return res
    else:
        len1 = len(postings[term1])
        len2 = len(postings[term2])
        x = 0
        y = 0
        # 双指针
        while x < len1 and y < len2:
            if postings[term1][x] == postings[term2][y]:
                x += 1
                y += 1
            elif postings[term1][x] < postings[term2][y]:
                res.append(postings[term1][x])
                x += 1
            else:
                y += 1
        if x < len1:
            while x < len1:
                res.append(postings[term1][x])
                x += 1
    return res


def input_query(doc):
    # 处理输入数据，与terms中的term匹配
    doc = doc.lower()
    terms = TextBlob(doc).words.singularize()
    res = []
    for term in terms:
        term = Word(term)
        #term = term.lemmatize()  # 词形还原
        res.append(term)
    return res


def Union(term1, term2):
    res = []
    if (len(term1) == 0) or (len(term2) == 0):
        return res
    else:
        # 计算term1，term2对应postings数组的长度
        len1 = len(term1)
        len2 = len(term2)
        x = 0
        y = 0
        # 双指针算法
        while x < len1 and y < len2:
            if term1[x] == term2[y]:
                res.append(term1[x])
                x += 1
                y += 1
            elif term1[x] < term2[y]:
                x += 1
            else:
                y += 1
        return res


def optimize_query(query):
    global postings
    # 按照出现排序，查询优化
    query = sorted(query, key=lambda x: len(postings[x]))
    res = postings[query[0]]
    for i in range(len(query)):
        res = Union(res, postings[query[i]])
    return res


def doSearch():  # 查询
    query = input_query(input("please input query： "))
    if not query:
        sys.exit()
    if len(query) == 1:#单个词查询
        answer = oneword(query[0])
        print(answer)
    elif query[1] == "and":#and查询
        answer = op_and(query[0], query[2])
        print(answer)
    elif query[1] == "or":#or查询
        answer = op_or(query[0], query[2])
        print(answer)
    elif query[1] == "not":#not查询
        answer = op_not(query[0], query[2])
        print(answer)
    else:#and优化查询
        answer = optimize_query(query)
        print(answer)


def main():
    get_postings()
    while 1:
        doSearch()


if __name__ == "__main__":
    main()

