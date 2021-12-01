# 实验内容

#### 实现以下指标评价，并对Experiment2的检索结果进行评价
- Mean Average Precision (MAP)
- Mean Reciprocal Rank (MRR)
- Normalized Discounted Cumulative Gain (NDCG)

# 实验目的
- 理解MAP（平均精度均值）、MRR（平均倒数排名）、NDCG（归一化折损累积增益）算法，并且在已有数据上编程实现

# 实验环境
Windows11、python3.9、Anaconda3

# 实验基本原理相关算法详解

## 1.MAP(平均精度值均值)

- 了解MAP之前我们先了解一下precision和recall，这两个标准的定义是这样的

  - **Precision:** 即精确率,检索最相关的顶级文档的能力.
  - **Recall:** 即召回率， 检索到语料库中所有相关项的能力
- 也就是说，精确率=检索到的相关文档数量/检索的文档总量， 召回率=检索到的相关文档数量/总的相关文档数量，如图所示

![](F:\IR\exp3\images\1.jpg)

- 上图比较直观，圆圈内（true   positives + false  positives）是我们选出的元素,它对应于分类任务中我们取出的结果

![](F:\IR\exp3\images\2.png)

- 而实验中的MAP如何计算呢？其实就是AP(可以理解为precision)的总和平均值，计算方法如下

  ![](F:\IR\exp3\images\4.png)

- 在实现代码中，对于每一条query,我先得到了相关文档出现的Rank，然后计算AP，最后累加求平均计算MAP,实现代码如下：

  ```python
  # 平均精度均值
  def MAP_eval(data_dict):
      MAP = 0
      for query_result in data_dict:
          data = data_dict[query_result]              # 一条查询对应的所有文档及其相关性 query_id[[doc_id,rel]，[doc_id,rel],.....]
          AP = 0                                      # 初始化每一条query的AP为0
          Rank = []                                   # Rank记录每一条query中相关文档出现的位置，方便用来计算AP
          for result in data:                         # [doc_id,rel]
              rel = result[1]
              if(rel > 0):
                  index = data.index(result) + 1      # 记录该doc是第几个出现的
                  Rank.append(index)
          # print(Rank)
          num_related_doc = len(Rank)                 # 总的相关文档数
          i = 1
          for index in Rank:
              precision = i / index                   # 计算精度
              # print("precision= ",precision)
              AP += precision
              i += 1
          AP /= num_related_doc                       # 计算AP
          # print(AP)
          MAP += AP                   
      MAP = MAP / len(data_dict)                      # 计算所有query的AP,得到MAP
      return MAP
  ```

  

## 2.Mean Reciprocal Rank (MRR)：平均倒数排名
- MRR的计算方法很简单，对于每一个query返回的所有文档中，找出第一个真正相关的文档位置，第一个真正相关的文档越靠前，结果越好。具体来说：对于一个query，若第一个真正相关的文档排在第n位，则MRR得分就是 1/n 。（如果没有正确答案，则得分为0）

  ![](https://img-blog.csdnimg.cn/20190224234419318.png)

- Q为样本query集合，|Q|表示Q中query个数，Rank(i)表示在第i个query中，第一个正确答案的排名

- MRR计算例子

- 假设现在有4个query语句,q1,q2,q3,q4

- q1的正确结果在第4位，q2和q3没有正确结果（即未检索到文档），q4正确结果在第5位,那么得分就是1/4+0+0+1/5=0.45,最后MRR就是求平均，即该系统MRR=0.45/4=0.1125,实现代码如下：

  ```python
  # 平均倒数排名,对比MAP，当返回的相关结果较少时，使用它更加合适
  def MRR_eval(data_dict):
      MRR = 0                                                       
      for query_id in data_dict:                      # query_id
          data = data_dict[query_id]                  # 一条查询对应的所有文档及其相关性 query_id[[doc_id,rel]，[doc_id,rel],.....]
          RR = 0                                      # 初始化每一条query的RR为0                     
          for result in data:                         # [doc_id,rel]
              rel = result[1]
              if(rel > 0):
                  index = data.index(result) + 1      # 记录该doc是第几个出现的相关文档
                  RR = 1 / index                      # 计算RR
                  MRR += RR
                  break
                    
      MRR = MRR / len(data_dict)                      # 计算所有query的RR,得到MRR
      return MRR
  ```

  

## 3.NDCG(归一化折损累积增益)
- NDCG(Normalized Discounted cumulative gain)归一化折损累计增益，这个指标通常是用来衡量和评价搜索结果算法,其主要思想就是高关联度的结果比一般关联度的结果更影响最终的指标得分，有高关联度的结果出现在更靠前的位置的时候，指标会越高，那么具体如何计算呢？

- 首先计算累计增益**(CG)**，它是当前文档之前所有文档的相关性得分之和，计算公式如下

  ![](F:\IR\exp3\images\5.png)



- 优化累加式指标**(DCG)**，当我们计算出CG之后发现，排名越往后的文档的CG越高，而用户更关心高排名的文档，所以我们
  折扣结果。在这里，我们将越往后的文档的权重设置的越小,代表更低的关注度，公式如下

  ![](F:\IR\exp3\images\6.png)

- 然后我们发现针对不同的query,返回的文档集合是不一样的，不能简单地用DCG,为了比较DCG，对其值进行规范化，从而得到一个理想的

  rank的归一化DCG为1.0,称为**IDCG**,将返回的文档按照相关性从大到小排序,计算IDCG,实现公式如下
  
  ![](F:\IR\exp3\images\7.png)
  
- 最后我们将DCG和IDCG综合起来得到归一化的DCG理想的排名**NDCG**,NDCG具有可比性不同的查询，衡量返回的结果和理想结果之间的差距，当得分越接近1时，代表返回的结果越接近理想情况，模型越好，实现公式如下

  ![](F:\IR\exp3\images\8.png)

- 实现代码如下：

  ```python
  # 归一化折损累积增益,
  def NDCG_eval(data_dict):
      NDCG = 0
      for query_id in data_dict:
          data = data_dict[query_id]                                      # 一条查询对应的所有文档及其相关性 query_id[[doc_id,rel]，[doc_id,rel],.....]
          CG = 0                                                          # 初始化每一条query的CG为0
          DCG = 0                                                         # 初始化每一条query的CG为0
          IDCG = 0                                                        # 初始化每一条query的IDCG为0
          # 计算DCG
          i = 1
          for result in data:                                             # [doc_id,rel]
              rel = result[1]
              CG +=  rel                                                  # CGn = sum(rel(i))
              if i == 1:
                  DCG = rel                                               # DCGn = rel1 + sum(2-n)rel(i) / log2(i)
              else:
                  DCG += (rel / math.log2(i))
              i += 1
  
          # 计算IDCG
          sorted_data = sorted(data, key = lambda x:x[1],reverse = True)  # 按照文档评分rel排序
          i = 1
          for result in sorted_data:                                      # [doc_id,rel]
              rel = result[1]
              # IDCG += ((2 ** rel - 1) / math.log2(i + 1))
              if i == 1:
                  IDCG = rel                                              # IDCGn = rel1 + sum(2-n)rel(i) / log2(i)
              else:
                  IDCG += (rel / math.log2(i))
              i += 1
  
          NDCG += DCG / IDCG
          
      NDCG = NDCG / len(data_dict)                                        # 计算NDCG
      return NDCG
  ```
  
  
  
# 实验预处理

- 首先对得到的数据进行预处理，我们得到的数据是与实验2相关的，也就是把实验2的每一条query对应的document的真正相关性得到，处理后得到如图所示的文件，分别代表查询id，对应文档id以及相关性

  ![](F:\IR\exp3\images\10.png)

- 下面我们对数据进行处理，这里建立数据字典，键值为query_id，值为列表，存储返回的已排好序的文档id及评分，如图所示

  ![](F:\IR\exp3\images\11.png)

- 实现代码如下

  ```python
  def generate_tweetid_gain(file_path):
      data_dict = {}
      with open(file_path, 'r', errors='ignore') as f:
          for line in f:
              result = line.strip().split(' ')    # 171 Q0 305345146675949568 0
              query_id = result[0]                # 查询id
              docu_id = result[2]                 # 文档id
              rel = int(result[3])                # 文档相关性
              if query_id not in data_dict:       # 为每个query建立列表，记录query查询回来的排序后的文档以及相关性
                  data_dict[query_id] = []
              if rel > 0:                         # 记录文档id和相关性
                  data_dict[query_id].append([docu_id,rel])
              else:
                  data_dict[query_id].append([docu_id,0])
      return data_dict
  ```

  

# 实验结果

  ![](F:\IR\exp3\images\9.png)

  #### 实验代码

  ```python
  import pandas as pd
  import math
  import numpy as np
  
  def generate_tweetid_gain(file_path):
      data_dict = {}
      with open(file_path, 'r', errors='ignore') as f:
          for line in f:
              result = line.strip().split(' ')    # 171 Q0 305345146675949568 0
              query_id = result[0]                # 查询id
              docu_id = result[2]                 # 文档id
              rel = int(result[3])                # 文档相关性
              if query_id not in data_dict:       # 为每个query建立列表，记录query查询回来的排序后的文档以及相关性
                  data_dict[query_id] = []
              if rel > 0:                         # 记录文档id和相关性
                  data_dict[query_id].append([docu_id,rel])
              else:
                  data_dict[query_id].append([docu_id,0])
      return data_dict
  
  # 平均精度均值
  def MAP_eval(data_dict):
      MAP = 0
      for query_result in data_dict:
          data = data_dict[query_result]              # 一条查询对应的所有文档及其相关性 query_id[[doc_id,rel]，[doc_id,rel],.....]
          AP = 0                                      # 初始化每一条query的AP为0
          Rank = []                                   # Rank记录每一条query中相关文档出现的位置，方便用来计算AP
          for result in data:                         # [doc_id,rel]
              rel = result[1]
              if(rel > 0):
                  index = data.index(result) + 1      # 记录该doc是第几个出现的
                  Rank.append(index)
          # print(Rank)
          num_related_doc = len(Rank)                 # 总的相关文档数
          i = 1
          for index in Rank:
              precision = i / index                   # 计算精度
              # print("precision= ",precision)
              AP += precision
              i += 1
          AP /= num_related_doc                       # 计算AP
          # print(AP)
          MAP += AP                   
      MAP = MAP / len(data_dict)                      # 计算所有query的AP,得到MAP
      return MAP
  
  # 平均倒数排名,对比MAP，当返回的相关结果较少时，使用它更加合适
  def MRR_eval(data_dict):
      MRR = 0                                                       
      for query_id in data_dict:                      # query_id
          data = data_dict[query_id]                  # 一条查询对应的所有文档及其相关性 query_id[[doc_id,rel]，[doc_id,rel],.....]
          RR = 0                                      # 初始化每一条query的RR为0                     
          for result in data:                         # [doc_id,rel]
              rel = result[1]
              if(rel > 0):
                  index = data.index(result) + 1      # 记录该doc是第几个出现的相关文档
                  RR = 1 / index                      # 计算RR
                  MRR += RR
                  break
                    
      MRR = MRR / len(data_dict)                      # 计算所有query的RR,得到MRR
      return MRR
  
  # 归一化折损累积增益,
  def NDCG_eval(data_dict):
      NDCG = 0
      for query_id in data_dict:
          data = data_dict[query_id]                                      # 一条查询对应的所有文档及其相关性 query_id[[doc_id,rel]，[doc_id,rel],.....]
          CG = 0                                                          # 初始化每一条query的CG为0
          DCG = 0                                                         # 初始化每一条query的CG为0
          IDCG = 0                                                        # 初始化每一条query的IDCG为0
          # 计算DCG
          i = 1
          for result in data:                                             # [doc_id,rel]
              rel = result[1]
              CG +=  rel                                                  # CGn = sum(rel(i))
              if i == 1:
                  DCG = rel                                               # DCGn = rel1 + sum(2-n)rel(i) / log2(i)
              else:
                  DCG += (rel / math.log2(i))
              i += 1
  
          # 计算IDCG
          sorted_data = sorted(data, key = lambda x:x[1],reverse = True)  # 按照文档评分rel排序
          i = 1
          for result in sorted_data:                                      # [doc_id,rel]
              rel = result[1]
              # IDCG += ((2 ** rel - 1) / math.log2(i + 1))
              if i == 1:
                  IDCG = rel                                              # IDCGn = rel1 + sum(2-n)rel(i) / log2(i)
              else:
                  IDCG += (rel / math.log2(i))
              i += 1
  
          NDCG += DCG / IDCG
          
      NDCG = NDCG / len(data_dict)                                        # 计算NDCG
      return NDCG
  
  def evaluation():
      # query relevance file
      file_path = './qrels.txt'
      data_dict = generate_tweetid_gain(file_path)
      MAP = MAP_eval(data_dict)
      print('MAP', ' = ', round(MAP, 5), sep='')
      MRR = MRR_eval(data_dict)
      print('MRR', ' = ', round(MRR, 5), sep='')
      NDCG = NDCG_eval(data_dict)
      print('NDCG', ' = ', round(NDCG, 5), sep='')
      
  if __name__ == '__main__':
      evaluation()
  ```

  
