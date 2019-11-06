#coding:utf-8

'''
data_analysis.py

数据分析文件，针对酒店评论内容，评论评分，出行类型做出分析

主要函数：
    基础模块：
        数据库读取函数：read_sql()
        文本过滤函数：filter_str()
        长度读取函数：

    评论分析模块：
    * 词频统计&词云显示
        评论分级函数：comment_rank()
        分词函数：fenci()
        去停用词函数：drop_stopwords()
        词频统计函数：words_freq()
        词云生成函数：wordcloud_gen()
        词云解析函数：comment_cloud_parse()
        词云可视化函数：comment_cloud_vision()
    * 词语关联
        词语关联函数：word_relate()
        无价值词过滤函数：words_filter()
        词语关联解析函数：word_relate_parse()
        区域词关联函数：local_word_relate_parse()
    
    评分分析模块：
    * 评分占比
        评分分级函数：score_rank()
        评分百分比计算函数：score_percent_parse()
        评分占比可视化函数：comment_score_vision()

    出行类型分析模块：
        出行类型百分比计算函数：trip_type_percent_parse()
        出行类型可视化函数：trip_type_vision()
'''


import pandas as pd
import numpy as np
import jieba
import re
from sqlalchemy import create_engine
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib
import pygal
import numpy as np
import os


# 连接数据库
engine = create_engine("mysql+pymysql://root:123456@localhost:3306/hotel_info",encoding="utf-8")



'''
数据库读取函数
'''
def read_sql(hotel_name):
    # 从数据库中读取数据
    sql = f'select * from {hotel_name}'
    df = pd.read_sql_query(sql,engine)

    # 去除空数据，在df上修改
    df.dropna(inplace=True) 

    # 去除重复数据，在df上修改
    df.drop_duplicates('comment',inplace=True)

    # 过滤评论除中英文及数字以外的其他字符的函数
    try:
        for i in range(len(df['comment'])):
            df.iloc[i,1] = filter_str(df.iloc[i,1])
    except Exception as e:
        print('过滤评论除中英文及数字以外的其他字符的函数-出错')
        print(e)
        print(i)

    return df


'''
过滤除中英文及数字以外的其他字符的函数
'''
def filter_str(desstr,restr=''):
    res = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")
    return res.sub(restr, desstr)


'''
长度读取函数
'''
def read_length(args_list):

    return str(len(args_list))


'''
头部数据读取函数
'''
def read_head(words_count,num=10):
    print(f'词频前{num}个：')
    print(words_count.iloc[:num,:])

    return None





'''
*************评论分析-词频统计&词云显示***************
评论分级：
0-3分：差评(C), 3-4分：中评(B), 4-5分：好评(A)
'''


'''
评论分级函数
'''
def comment_rank(df_total):
    df_A = df_total[df_total['total_score'] >= 4] # 好评
    df_B = df_total[(df_total['total_score'] >= 3) & (df_total['total_score'] < 4)] # 中评
    df_C = df_total[df_total['total_score'] < 3] # 差评
    return df_A,df_B,df_C


'''
分词函数：利用jieba分词库分词,返回分词结果列表
'''
def fenci(hotel_name):
    # 从数据库中读取数据
    df = read_sql(hotel_name)
    
    # 评论分级
    df_A,df_B,df_C = comment_rank(df)

    # 将评论转换成一个list
    comment_list = []
    for df_i in [df_A,df_B,df_C]:
        comment_list.append(df_i.comment.values.tolist())

    # 创建列表存储分词结果
    comment_S = []

    # 使用jieba分词
    for comment in comment_list:  # 每一种评论
        comment_S_rank = []
        for line in comment:  # 每一条评论
            current_segment = jieba.lcut(line) # 分词
            comment_S_rank.append(current_segment) # 保存分词的结果
        comment_S.append(comment_S_rank)

    return comment_S[0],comment_S[1],comment_S[2] # 返回三种分级的评论分词列表


'''
去停用词函数：把分词结果列表去掉高频无用的停用词
'''
def drop_stopwords(comment_S):
    # 读取停用词表
    stopwords=pd.read_csv("D:/Project/test/stopwords.txt",index_col=False,sep="\t",quoting=3,names=['stopword'], encoding='utf-8')

    # 停用词转换为列表
    stopwords = stopwords.stopword.values.tolist()

    # 所有评论出现的所有词语
    all_words = []

    # 遍历传入的未分词列表，去停用词
    for line in comment_S:
        for word in line:
            if word in stopwords or word == '\n' or word == '\t':
                continue
            all_words.append(word)

    return all_words


'''
词频统计函数
'''
def words_freq(all_words):
    # 转换格式
    df_all_words=pd.DataFrame({'all_words':all_words})

    # df_all_words里面有重复的词语，先groupby一下，每组就是一个词，后续的agg是对每一个分组的操作，统计每个词的总数量
    # words_count是DataFrame格式的变量，一列是词，一列是count
    words_count=df_all_words.groupby('all_words')['all_words'].agg(np.size)
    words_count = words_count.to_frame()  
    words_count.columns = ['count']

    # 还原index，按数量降序排序
    words_count=words_count.reset_index().sort_values(by=["count"],ascending=False)
    
    return words_count


'''
词云生成函数，选取前cloud_num个高频词生成词云
'''
def wordcloud_gen(words_count,cloud_num):
    # 参数配置，设置显示区域大小
    matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)

    # 创建词云对象
    word_cloud=WordCloud(scale=4, # scale参数越大分辨率越高，越清晰，4已经1800*2500分辨率了
                        width = 500,
                        height = 250,
                        font_path="./data/simhei.ttf", # 字体路径
                        background_color="white", # 背景颜色
                        max_font_size=70,min_font_size=12, # 字体最大最小大小
                        prefer_horizontal=1.0) #词语水平方向排版出现的频率

    # 选取数据集 词:词频
    word_frequence = {x[0]:x[1] for x in words_count.head(cloud_num).values}

    # 训练词云
    word_cloud=word_cloud.generate_from_frequencies(word_frequence)

    return word_cloud


'''
评论词云可视化函数：从分词列表里生成词云图，返回去停用词，统计词频后的words_count
'''
def comment_cloud_vision(rank,comment_S,cloud_num=10):

    all_words = drop_stopwords(comment_S)
    words_count = words_freq(all_words)
    word_cloud = wordcloud_gen(words_count,cloud_num)
    plt.imshow(word_cloud)
    plt.axis('off') # 去掉坐标轴
    plt.savefig(f'D:/Project/test/static/{rank}.png',quality=95)

    return words_count


'''
评论词云解析函数，传入酒店名字或者区域名词，词云图里的词语数量，需要分析显示的评分等级
'''
def comment_cloud_parse(hotel_name=None,cloud_num=10,ranks=[],location=None,freq_num=30):

    if location:
        if hotel_name == '亚朵':
            sql = 'select hotel_name from hotel_list where hotel_name like "%%亚朵%%" or hotel_name like "%%drama%%"'
            df_hotel_name = pd.read_sql_query(sql,engine)

            # 创建三个分级列表，存储地区每个酒店的评论分词
            comment_S_A_local = []
            comment_S_B_local = []
            comment_S_C_local = []

            for hotel_name in df_hotel_name.iloc[:,0]:
                comment_S_A,comment_S_B,comment_S_C = fenci(hotel_name)
                for seg_A in comment_S_A:
                    comment_S_A_local.append(seg_A)
                for seg_B in comment_S_B:
                    comment_S_B_local.append(seg_B)
                for seg_C in comment_S_C:
                    comment_S_C_local.append(seg_C)

            # 判断需要可视化哪些等级的评论       
            for i in ranks:
                if i == 'A':
                    words_count = comment_cloud_vision('A',comment_S_A_local,cloud_num)
                    print(f'{location}区域好评量：'+read_length(comment_S_A_local))
                    read_head(words_count,num=freq_num)

                elif i == 'B':
                    words_count = comment_cloud_vision('B',comment_S_B_local,cloud_num)
                    print(f'{location}区域中评量：'+read_length(comment_S_B_local))
                    read_head(words_count,num=freq_num)

                elif i == 'C':
                    words_count = comment_cloud_vision('C',comment_S_C_local,cloud_num)
                    print(f'{location}区域差评量：'+read_length(comment_S_C_local))
                    read_head(words_count,num=freq_num)

                elif i == 'all':
                    # 全部评论
                    comment_S_all = []

                    for comm_temp in [comment_S_A_local,comment_S_B_local,comment_S_C_local]:
                        for comm in comm_temp:
                            comment_S_all.append(comm)

                    words_count = comment_cloud_vision('all',comment_S_all,cloud_num)
                    print(f'{location}区域总评量：'+read_length(comment_S_all))
                    read_head(words_count,num=freq_num)

        else:
            print('本地区该酒店暂无解析')
    
    else: # 单个酒店词云分析
        comment_S_A,comment_S_B,comment_S_C = fenci(hotel_name)

        # 判断需要可视化哪些等级的评论
        for i in ranks:
            if i == 'A':
                words_count = comment_cloud_vision('A',comment_S_A,cloud_num)
                print(f'{hotel_name}好评量：'+read_length(comment_S_A))
                read_head(words_count,num=freq_num)
                

            elif i == 'B':
                words_count = comment_cloud_vision('B',comment_S_B,cloud_num)
                print(f'{hotel_name}中评量：'+read_length(comment_S_B))
                read_head(words_count,num=freq_num)

            elif i == 'C':
                words_count = comment_cloud_vision('C',comment_S_C,cloud_num)
                print(f'{hotel_name}差评量：'+read_length(comment_S_C))
                read_head(words_count,num=freq_num)

            elif i == 'all':
                # 全部评论
                comment_S_all = []

                for comm_temp in [comment_S_A,comment_S_B,comment_S_C]:
                    for comm in comm_temp:
                        comment_S_all.append(comm)

                words_count = comment_cloud_vision('all',comment_S_all,cloud_num)
                print(f'{hotel_name}总评量：'+read_length(comment_S_all))
                read_head(words_count,num=freq_num)

    return None





'''
*************评论分析-词语关联***************
'''

'''
词语关联函数：寻找文本中关键词前后的一些有价值的关联词语
'''
def word_relate(all_words,keyword):

    pre_keyword = [] # 前关键词
    back_keyword = [] # 后关键词

    # 寻找下标
    for index in range(len(all_words)):
        if all_words[index] == keyword:
            if index == 0:
                back_keyword.append(all_words[index+1])
                continue
            if index == len(all_words)-1:
                pre_keyword.append(all_words[index-1])
                continue
            pre_keyword.append(all_words[index-1])
            back_keyword.append(all_words[index+1])

    return pre_keyword,back_keyword


'''
无价值词过滤函数
'''
def words_filter(keyword_count,keyword,direct):
    # 读取无价值词表
    if direct == 'pre':
        dropwords=pd.read_csv(f"D:/Project/test/词语关联前向无价值词/{keyword}无价值词.txt",index_col=False,sep="\t",quoting=3,names=['dropwords'], encoding='utf-8')
    elif direct == 'back':
        dropwords=pd.read_csv(f"D:/Project/test/词语关联后向无价值词/{keyword}无价值词.txt",index_col=False,sep="\t",quoting=3,names=['dropwords'], encoding='utf-8')


    # 无价值词转换为列表
    dropwords = dropwords.dropwords.values.tolist()

    # 由于直接从keyword_count里面过滤删除无价值的词，
    # 容易报IndexError的错，所以创建一个temp列表，添加过滤后的词语，
    # 最后转换成DataFrame格式
    temp = []

    for index in range(len(keyword_count['all_words'])):
        if keyword_count.iloc[index,0] in dropwords:
            continue
        temp.append(keyword_count.iloc[index,0])
    
    keyword_count = pd.DataFrame(temp,columns=['all_words'])

    return keyword_count


'''
词关联解析函数：读取，分词，去停用词，关联，统计前向关联词，过滤前向无价值词，后向词列表直接返回
'''
def word_relate_parse(hotel_name,keyword,rank):

    comment_S_A,comment_S_B,comment_S_C = fenci(hotel_name)
    if rank == 'A':
        all_words = drop_stopwords(comment_S_A)
    elif rank == 'B':
        all_words = drop_stopwords(comment_S_B)
    elif rank == 'C':
        all_words = drop_stopwords(comment_S_C)
    elif rank == 'all':
        # 全部评论
        comment_S_all = []

        for comm_temp in [comment_S_A,comment_S_B,comment_S_C]:
            for comm in comm_temp:
                comment_S_all.append(comm)
        
        all_words = drop_stopwords(comment_S_all)

    pre_keyword,back_keyword = word_relate(all_words,keyword)
    # 关键词前关联词解析
    pre_keyword_count = words_freq(pre_keyword)
    # pre_keyword_count = words_filter(pre_keyword_count,keyword,'pre')

    return pre_keyword_count,back_keyword


'''
区域词关联函数：统计某个区域酒店的高频前向关联词和所有的后向关联词
'''
def local_word_relate_parse(location,keyword,hotel,rank):
    # 读取所有的酒店
    if hotel == '亚朵':
        sql = 'select hotel_name from hotel_list where hotel_name like "%%亚朵%%" or hotel_name like "%%drama%%"'

    else:
        print('该地区无该酒店')
        return None

    df_hotel_name = pd.read_sql_query(sql,engine)

    # 创建空的前向关联词DataFrame，后续直接append
    pre_keyword = pd.DataFrame({'all_words':[]})
    back_keyword = []


    # 所有酒店的统计，每个酒店取前十个前向高频词和所有的后向关联词
    for hotel in df_hotel_name.iloc[:,0]:
        keyword_count = word_relate_parse(hotel,keyword,rank)
        pre_keyword = pre_keyword.append(keyword_count[0].iloc[:10],sort=False)
        for word in keyword_count[1]:
            back_keyword.append(word)
    
    back_keyword = pd.DataFrame({'all_words':back_keyword})
    # 转换为列表传入words_freq()
    pre_keyword_count = words_freq(pre_keyword.all_words.values.tolist())
    back_keyword_count = words_freq(back_keyword.all_words.values.tolist())

    # 检查文件夹是否存在，不存在则创建
    if os.path.exists(f'D:/Project/test/{location}/{keyword}'):
        pass
    else:
        os.mkdir(f'D:/Project/test/{location}/{keyword}')

    # 存储数据
    pre_keyword_count.iloc[:20].to_csv(f'D:/Project/test/{location}/{keyword}/pre_keyword_count.csv',index=False,header=False)
    back_keyword_count.to_csv(f'D:/Project/test/{location}/{keyword}/back_keyword_count.csv',index=False,header=False)

    return None




'''
*************评分分析***************
'''

'''
评分分级函数
'''
def score_rank(df_total):
    df_5 = df_total[df_total['total_score'] == 5] # 5分
    df_4 = df_total[(df_total['total_score'] >= 4) & (df_total['total_score'] < 5)] # 4分
    df_3 = df_total[(df_total['total_score'] >= 3) & (df_total['total_score'] < 4)] # 3分
    df_2 = df_total[(df_total['total_score'] >= 2) & (df_total['total_score'] < 3)] # 2分
    df_1 = df_total[df_total['total_score'] < 2] # 1分

    return df_5,df_4,df_3,df_2,df_1


'''
评分百分比计算函数
'''
def score_percent_parse(df_hotel):
    # 评分分级
    df_5,df_4,df_3,df_2,df_1 = score_rank(df_hotel)

    # 统计数量
    count_5 = df_5.count()['total_score']
    count_4 = df_4.count()['total_score']
    count_3 = df_3.count()['total_score']
    count_2 = df_2.count()['total_score']
    count_1 = df_1.count()['total_score']

    # 百分比
    count_sum = count_1 + count_2 + count_3 + count_4 + count_5
    percent_5 = count_5 / count_sum
    percent_4 = count_4 / count_sum
    percent_3 = count_3 / count_sum
    percent_2 = count_2 / count_sum
    percent_1 = count_1 / count_sum

    return [percent_5,percent_4,percent_3,percent_2,percent_1]


'''
评分占比可视化函数
'''
def comment_score_vision(hotel_name):
    df_hotel = read_sql(hotel_name)

    # 计算评分百分比
    y = score_percent_parse(df_hotel)

    # 绘图
    font = FontProperties(fname=r"C:/Windows/Fonts/simhei.ttf", size=14)  # 解决绘图中文字符乱码问题
    x = [5,4,3,2,1]
    plt.ylim((0,1))
    plt.bar(x,y,label=hotel_name,color="orange")

    # 显示数值
    for a,b in zip(x,y):
        plt.text(a,b+0.01,'%.3f'%b, ha='center', va='bottom', fontsize=13)

    plt.title(hotel_name,FontProperties=font)
    plt.legend(prop=font,loc='best')
    plt.savefig(f'D:/Project/test/static/评分占比.png',quality=95)
    # plt.show()

    return None




'''
***********出行类型分析***********
'''

'''
出行类型百分比计算函数
出行类型：家庭亲子、情侣出游、商务出差、朋友出游、独自旅行、代人预订、其他
'''
def trip_type_percent_parse(df_hotel):
    
    df_fam = df_hotel[df_hotel['trip_type'] == '家庭亲子']
    df_coup = df_hotel[df_hotel['trip_type'] == '情侣出游']
    df_fri = df_hotel[df_hotel['trip_type'] == '朋友出游']
    df_bus = df_hotel[df_hotel['trip_type'] == '商务出差']
    df_own = df_hotel[df_hotel['trip_type'] == '独自旅行']
    df_rep = df_hotel[df_hotel['trip_type'] == '代人预订']
    df_else = df_hotel[df_hotel['trip_type'] == '其他']

    # 统计数量
    count_fam = df_fam.count()['trip_type']
    count_coup = df_coup.count()['trip_type']
    count_fri = df_fri.count()['trip_type']
    count_bus = df_bus.count()['trip_type']
    count_own = df_own.count()['trip_type']
    count_rep = df_rep.count()['trip_type']
    count_else = df_else.count()['trip_type']

    # 百分比
    count_sum = count_fam + count_coup + count_fri + count_bus + count_own + count_rep + count_else
    per_fam = round(count_fam / count_sum,3) * 100
    per_coup = round(count_coup / count_sum,3) * 100
    per_fri = round(count_fri / count_sum,3) * 100
    per_bus = round(count_bus / count_sum,3) * 100
    per_own = round(count_own / count_sum,3) * 100
    per_rep = round(count_rep / count_sum,3) * 100
    per_else = round(count_else / count_sum,3) * 100

    return [per_fam,per_coup,per_fri,per_bus,per_own,per_rep,per_else]


'''
出行类型可视化函数：绘制占比圈饼图
'''
def trip_type_vision(hotel_name):
    df_hotel = read_sql(hotel_name)

    # 计算出行类型百分比
    trip_per = trip_type_percent_parse(df_hotel)

    # pygal模块绘制圈饼图
    pie_chart = pygal.Pie(inner_radius=.4)
    pie_chart.title = f'{hotel_name}出行类型 (in %)'
    pie_chart.add('家庭亲子', trip_per[0])
    pie_chart.add('情侣出游', trip_per[1])
    pie_chart.add('朋友出游', trip_per[2])
    pie_chart.add('商务出差', trip_per[3])
    pie_chart.add('独自旅行', trip_per[4])
    pie_chart.add('代人预订', trip_per[5])
    pie_chart.add('其他', trip_per[6])
    pie_chart.render_to_file('D:/bar_chart.svg')



if __name__ == '__main__':
    # trip_type_vision('上海外滩亚朵轻居酒店')
    # comment_score_vision('上海外滩亚朵轻居酒店')
    local_word_relate_parse('上海','房间隔音','亚朵','all')
    # comment_cloud_parse(hotel_name='亚朵',location='上海',cloud_num=100,ranks=['all'])
    pass