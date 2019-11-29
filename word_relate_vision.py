#coding:utf-8

'''
word_relate_vision.py

词关联可视化文件：分类的关键词经过词关联处理之后，根据前后向关联词进行可视化处理，人工检查前后向关联词
文件，选取适当的词进行可视化

主要函数：
    词关联可视化函数：graph_vision()
    条形图可视化函数：bar_vision()
    条形图文本标签显示函数：autolabel()
    pyecharts条形图显示函数：bar_vision_charts()
    pyecharts饼图显示函数：pie_vision_charts()
'''

from pyecharts import options as opts
from pyecharts.charts import Graph, Bar, Pie
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

    with open(f'./词关联可视化json文件/{keyword}.json','r',encoding='utf-8') as f:
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
    labels = ['前台','前台服务','前台态度','前台服务员']
    active_means = [98.4,97.5,99.2,100.0]
    negative_means = [1.6,2.5,0.8,0.0]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(12,7))
    rects1 = ax.bar(x - width/2, active_means, width, label='好评率',color='orange')
    rects2 = ax.bar(x + width/2, negative_means, width, label='差评率',color='darkcyan')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title('前台关联词占比统计/%',fontsize=17)
    ax.set_xticks(x)
    ax.set_xticklabels(labels,fontsize=13)
    ax.legend(loc='best',fontsize=17)

    autolabel(rects1,ax)
    autolabel(rects2,ax)

    fig.tight_layout()
    plt.yticks(fontsize=14)
    plt.savefig('./static/条形图/前台.png')
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


'''
pyecharts条形图显示函数
'''
def bar_vision_charts():
    c = (
        Bar()
        .add_xaxis(['环境','前台','设施','早餐','入住','房间','位置','价格'])
        .add_yaxis("好评率", [98.988,98.848,98.792,98.259,98.238,94.863,90.229,87.248])
        .add_yaxis("差评率", [1.012,1.152,1.208,1.741,1.762,5.137,9.771,12.752])
    )
    return c


'''
pyecharts饼图显示函数
'''
def pie_vision_charts(values=None,labels=None):
    c = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(labels,values)],
            radius=["30%", "75%"],
            center=["45%", "50%"],
            label_opts=opts.LabelOpts(is_show=True),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return c


if __name__ == '__main__':
    # graph_vision('上海','前台').render('./static/前台.html')
    # graph_vision('上海','早餐').render('./static/早餐.html')
    # graph_vision('上海','房间').render('./static/房间.html')
    # graph_vision('上海','设施').render('./static/设施.html')
    # graph_vision('上海','价格').render('./static/价格.html')
    # graph_vision('上海','环境').render('./static/环境.html')
    # graph_vision('上海','位置').render('./static/位置.html')
    # graph_vision('上海','入住').render('./static/入住.html')

    # bar_vision()
    # bar_vision_charts().render('./static/分类统计图.html')
    # pie_vision_charts().render('./static/饼图统计图.html')

    graph_vision()

