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
import matplotlib.pyplot as plt
import numpy as np


plt.rcParams['font.sans-serif']=['SimHei']#设置字体以便支持中文


'''
词关联可视化函数，参数：地区、关键词、前向关联词下标、后向关联词下标
'''
def graph_vision(location,keyword):

    with open(f'D:/Project/test/词关联可视化json文件/{keyword}.json','r',encoding='utf-8') as f:
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

'''
条形图可视化函数：
分类关键词内部褒贬义词统计
'''
def bar_vision():
    labels = ['位置','距离地铁站']
    active_means = [91.3,77.0]
    negative_means = [8.7,23.0]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, active_means, width, label='好评',color='orange')
    rects2 = ax.bar(x + width/2, negative_means, width, label='差评',color='darkcyan')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title('位置关联词占比统计')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc='best')

    autolabel(rects1,ax)
    autolabel(rects2,ax)

    fig.tight_layout()
    # plt.ylim([0,120])
    plt.show()


def autolabel(rects,ax):
    """条形图的文本标签显示在上方"""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')



if __name__ == '__main__':
    # graph_vision('上海','前台').render('D:/Project/test/static/前台.html')
    # graph_vision('上海','早餐').render('D:/Project/test/static/早餐.html')
    # graph_vision('上海','房间').render('D:/Project/test/static/房间.html')
    # graph_vision('上海','设施').render('D:/Project/test/static/设施.html')
    # graph_vision('上海','价格').render('D:/Project/test/static/价格.html')
    # graph_vision('上海','环境').render('D:/Project/test/static/环境.html')
    # graph_vision('上海','位置').render('D:/Project/test/static/位置.html')
    # graph_vision('上海','入住').render('D:/Project/test/static/入住.html')

    bar_vision()