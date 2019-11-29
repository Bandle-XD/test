#coding:utf-8

'''
run.py

系统后台文件：flask框架构建
'''

from flask import Flask, redirect, request, render_template, url_for, session
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import Session
from pyecharts.charts import Bar
from pyecharts import options as opts
from jinja2 import Markup

# 本地函数
from crawl_main import crawl, init_crawl
from data_analysis import comment_cloud_parse

engine = create_engine("mysql+pymysql://root:123456@localhost:3306/hotel_info",encoding="utf-8")



'''
登录验证函数：验证用户名和密码
'''
def valid_login(uname,passwd):
    metadata = MetaData() # 定义元数据对象
    session = Session(engine) # session进行操作

    # 获取user表对象
    User = Table('user',metadata,autoload=True,autoload_with=engine)

    # 查询数据返回第一条
    res = session.query(User).first()
    
    if res[1] != uname:
        return 1
    elif res[2] != passwd:
        return 2
    else:
        return 0


# def bar_base():
#     c = (
#         Bar(init_opts=opts.InitOpts(width='1300px',height='650px'))
#         .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
#         .add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
#         .add_yaxis("商家B", [15, 25, 16, 55, 48, 8])
#         .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"),
#                          legend_opts=opts.LegendOpts(textstyle_opts={'fontSize':40}))
#     )
#     return c


'''
-------------flask主体内容--------------
'''
app = Flask(__name__)

# 在flask项目中，Session, Cookies以及一些第三方扩展都会用到SECRET_KEY值，这是一个比较重要的配置值。
app.config['SECRET_KEY'] = '123456'



'''
登录验证，部分页面访问需要授权
'''
@app.before_request
def before_req1(*args, **kwargs):
    if request.path == '/':
        return None
    user = session.get('username')
    if user:
        return None
    return redirect('/')


'''
登录界面
'''
@app.route('/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        uname = request.form['username']
        passwd = request.form['password']
        # 验证登录
        res = valid_login(uname,passwd)
        if res == 1:
            return '用户名不存在'
        elif res == 2:
            return '密码错误'
        elif res == 0:
            # 登陆成功，用户信息保存进session
            session['username'] = uname
            return redirect(url_for('home'))


'''
系统主界面
'''
@app.route('/home')
def home():
    return render_template('home.html')


'''
爬虫主界面
'''
@app.route('/crawl',methods=['GET','POST'])
def crawl_main():
    if request.method == 'GET':
        return render_template('crawl.html')
    else:
        url = request.form['url']
        driver = init_crawl()
        res = crawl(driver,url)
        return res


'''
数据分析主界面
'''
@app.route('/da')
def da_main():
    return render_template('da.html')



'''
爬取记录主界面
'''
@app.route('/record')
def record_main():
    return render_template('record.html')


'''
词频统计主界面
'''
@app.route('/word_freq',methods=['GET','POST'])
def word_freq():
    if request.method == 'GET':
        return render_template('word_freq.html')
    else:
        location = request.form['location']
        hotel_name = request.form['hotel_name']
        cloud_num = request.form['cloud_num']
        ranks = ['A','B','C','all']
        if location == '':
            location = None
        
        # src = comment_cloud_parse(location=location,hotel_name=hotel_name,cloud_num=int(cloud_num),ranks=ranks)
        src = ['/static/词频分析/上海/亚朵/A.png',
                '/static/词频分析/上海/亚朵/B.png',
                '/static/词频分析/上海/亚朵/C.png',
                '/static/词频分析/上海/亚朵/all.png']
        # print(locals()['src'])
        if src == '本地区该酒店暂无解析':
            return '本地区该酒店暂无解析'

        return render_template('word_freq_res.html',locals=locals())
    # c = bar_base()
    # return Markup(c.render_embed())



if __name__ == '__main__':
    app.run(debug=True)
    


