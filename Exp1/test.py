from textblob import TextBlob  # 导入文本处理工具
from textblob import Word

term = "house"
temp = Word(term)
print(term)
temp.lemmatize("v")  # 词形还原

