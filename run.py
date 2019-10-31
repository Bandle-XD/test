'''
run.py

系统后台文件：flask框架构建
'''

from flask import Flask, redirect, request, render_template, url_for, flash, session
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import Session

# 本地函数
from crawl_main import crawl, init_crawl


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
        # res = crawl()
        return render_template('crawl.html',args=locals())
    else:
        url = request.form['url']
        driver = init_crawl()
        res = crawl(driver,url)
        return res


'''
数据分析主界面
'''
@app.route('/da',methods=['GET','POST'])
def da_main():
    if request.method == 'GET':
        return render_template('da.html')
    else:
        pass


'''
爬取记录主界面
'''
@app.route('/record')
def record_main():
    return render_template('record.html')


if __name__ == '__main__':
    app.run(debug=True)
    


