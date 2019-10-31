#coding:utf-8

'''
crawl_sql.py

爬虫数据库接口文件，建表，写表

主要函数：
    建表函数：create_table()
    评论写表函数：insert_info()
    酒店基本信息写表函数：insert_hotel_list()
'''


from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import Session
from sqlalchemy import Column,String,Integer,Text,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists
import pymysql
import pandas as pd

# 连接数据库
engine = create_engine("mysql+pymysql://root:123456@localhost:3306/hotel_info",encoding="utf-8")

# 创建orm基类
Base = declarative_base()


'''
建表函数：不同的酒店建不同的表，存储评论，评分
'''
def create_table(hotel_name):

    # 清理Base的缓存，非常重要，避免后续删表建表出现问题，因为是
    # create_all和drop_all()，不然会误删，和某个表存在的情况
    Base.metadata.clear()

    class Hotel(Base):
        __tablename__ = hotel_name
        id = Column(Integer,primary_key=True,autoincrement=True)
        comment = Column(Text)
        total_score = Column(Float)
        envir_score = Column(Float)
        dev_score = Column(Float)
        serv_score = Column(Float)
        clean_score = Column(Float)
        trip_type = Column(String(64))
    

    Base.metadata.drop_all(engine) # 删除之前已有的表
    Base.metadata.create_all(engine) # 创建新表
    # engine.dispose()
    return None


'''
写表函数：评论写进表
'''
def insert_info(hotel_name, comment_list, total_score_list, envir_score_list,
                dev_score_list, serv_score_list, clean_score_list,trip_type_list):

    # 新建pandas中的DataFrame类型，准备写入mysql
    df = pd.DataFrame({'comment':comment_list,
                        'total_score':total_score_list,
                        'envir_score':envir_score_list,
                        'dev_score':dev_score_list,
                        'serv_score':serv_score_list,
                        'clean_score':clean_score_list,
                        'trip_type':trip_type_list})

    # 将新建的DataFrame写入mysql中的表
    df.to_sql(hotel_name,engine,if_exists='append',index=False)
    return None


'''
写表函数：酒店基本信息写进hotel_list表
'''
def insert_hotel_list(hotel_name, hotel_score, comment_num, crawl_time, crawl_date):
    
    # metadata = MetaData() # 定义元数据对象
    # session = Session(engine) # session进行操作

    # # 获取hotel_list表对象
    # Hotel = Table('hotel_list',metadata,autoload=True,autoload_with=engine)

    # # 判断酒店之前是否有爬取记录，返回True或False，有则删除
    # if session.query(exists().where(Hotel.c.hotel_name == hotel_name)).scalar():
    #     session.delete(session.query(Hotel).filter(Hotel.c.hotel_name == hotel_name).all())

    # 新建pandas中的DataFrame类型，准备写入mysql
    df = pd.DataFrame({'hotel_name':[hotel_name],'hotel_score':[hotel_score],'comment_num':[comment_num],
                            'crawl_time':[crawl_time],'crawl_date':[crawl_date]})

    # 将新建的DataFrame写入mysql中的表
    df.to_sql('hotel_list',engine,if_exists='append',index=False)
    return None


if __name__ == '__main__':
    pass