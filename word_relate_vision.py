#coding:utf-8

'''
word_relate_vision.py

词关联可视化文件：分类的关键词经过词关联处理之后，根据前后向关联词进行可视化处理，人工检查前后向关联词
文件，选取适当的词进行可视化

主要函数：
    词关联可视化函数：graph_vision()
    条形图可视化函数：bar_vision()
    条形图文本标签显示函数：autolabel()
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
    labels = ['虹桥枢纽国展中心亚朵酒店','虹桥韩国街亚朵轻居酒店','虹桥国展蟠龙地铁站亚朵酒店','安亭亚朵酒店']
    active_means = [2.4,2.4,1.5,0.0]
    negative_means = [0.0,0.0,5.3]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(12,7))
    rects1 = ax.bar(x, active_means, width, label='差评率',color='darkcyan')
    # rects2 = ax.bar(x + width/2, negative_means, width, label='差评',color='darkcyan')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title('上海地区亚朵酒店差评率分析/%',fontsize=17)
    ax.set_xticks(x)
    ax.set_xticklabels(labels,fontsize=13)
    ax.legend(loc='best',fontsize=17)

    autolabel(rects1,ax)
    # autolabel(rects2,ax)

    fig.tight_layout()
    plt.yticks(fontsize=14)
    plt.ylim((0,7))
    plt.savefig('./static/条形图/上海地区差评率分析_5.png')
    # plt.show()


'''
条形图的文本标签显示函数
'''
def autolabel(rects,ax):
    """条形图的文本标签显示在上方"""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom',fontsize=13)



if __name__ == '__main__':
    # graph_vision('上海','前台').render('D:/Project/test/static/前台.html')
    # graph_vision('上海','早餐').render('D:/Project/test/static/早餐.html')
    # graph_vision('上海','房间').render('D:/Project/test/static/房间.html')
    # graph_vision('上海','设施').render('D:/Project/test/static/设施.html')
    # graph_vision('上海','价格').render('D:/Project/test/static/价格.html')
    # graph_vision('上海','环境').render('D:/Project/test/static/环境.html')
    # graph_vision('上海','位置').render('D:/Project/test/static/位置.html')
    graph_vision('上海','入住').render('D:/Project/test/static/入住.html')

    # bar_vision()