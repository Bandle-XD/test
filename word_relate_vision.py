#coding:utf-8

'''
word_relate_vision.py

词关联可视化文件：分类的关键词经过词关联处理之后，根据前后向关联词进行可视化处理，人工检查前后向关联词
文件，选取适当的词进行可视化

主要函数：
    词关联可视化函数：graph_vision()
'''

from pyecharts import options as opts
from pyecharts.charts import Graph, Page
import pandas as pd
import json
import os



'''
词关联可视化函数，参数：地区、关键词、前向关联词下标、后向关联词下标
'''
def graph_vision(location,keyword):

    with open(f'D:/Project/test/{keyword}.json','r',encoding='utf-8') as f:
        j = json.load(f)
        nodes, links, categories = j

    # pyecharts V1 版本开始支持链式调用
    c = (
        Graph()
        .add(
            "",
            nodes,
            links,
            categories,
            repulsion=4000)
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{keyword}关联词分析"))
    )
    return c

graph_vision('上海','前台').render('D:/Project/test/static/前台.html')
# graph_vision('上海','早餐').render('D:/Project/test/static/早餐.html')