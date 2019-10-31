#coding:utf-8

'''
crawl_main.py

爬虫主体文件：针对携程平台爬取酒店数据

主要函数：
    爬虫初始化函数：init_crawl()
    评论解析函数：comment_parse()
    评分解析函数：score_parse()
    出行类型解析函数：trip_parse()
    爬虫主函数：crawl()
'''


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# WebDriverWait 库，负责循环等待
from selenium.webdriver.support.ui import WebDriverWait
# expected_conditions 类，负责条件出发
from selenium.webdriver.support import expected_conditions as EC
# 超时异常
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import datetime
import re

# 本地函数
from crawl_sql import create_table
from crawl_sql import insert_info
from crawl_sql import insert_hotel_list




'''
爬虫初始化函数
'''
def init_crawl():
    # chrome参数配置
    options = Options()

    # 设置编码
    options.add_argument('lang=zh_CN.UTF-8')

    # 无图片加载，提升速度
    options.add_argument('blink-settings=imagesEnabled=false')

    # 此步骤很重要! 设置为开发者模式，防止被各大网站识别出来使用了Selenium
    options.add_experimental_option('excludeSwitches', ['enable-automation'])

    # executable_path
    chrome_driver = 'C:\Program Files (x86)\Google\Chrome\Application\chromedriver'

    # 创建chrome对象
    driver = webdriver.Chrome(chrome_options=options,executable_path = chrome_driver)

    return driver


'''
解析函数：提取评论
'''
def comment_parse(bs, comment_list):

    # # bs4解析
    # bs = BeautifulSoup(html,'lxml')

    # 所有含有评论的标签列表
    comment_list_tag = bs.find_all('div',class_='J_commentDetail')

    # 添加评论
    for tag in comment_list_tag:
        comment_list.append(tag.get_text())
    
    return None


''' 
解析函数：提取评分
'''
def score_parse(bs, total_score_list, envir_score_list, dev_score_list, serv_score_list, clean_score_list):

    # # bs4解析
    # bs = BeautifulSoup(html,'lxml')

    # 所有含有评分的标签列表
    score_list_tag = bs.find_all('p',class_='comment_title')

    # 添加评分
    for tag in score_list_tag:

        # 添加整体评分
        total_score_list.append(float(tag.contents[1].contents[0].get_text()))

        # 获取属性data-value信息
        value = tag.contents[0]['data-value']

        # 正则匹配
        pattern = r'\d.\d'
        re_value = re.findall(pattern,value)

        # 添加环境评分
        envir_score_list.append(float(re_value[0]))

        # 添加设施评分
        dev_score_list.append(float(re_value[1]))

        # 添加服务评分
        serv_score_list.append(float(re_value[2]))

        # 添加卫生评分
        clean_score_list.append(float(re_value[3]))

    return None


'''
解析函数，获取出行类型
'''
def trip_parse(bs,trip_type_list):

    # 获取所有出行类型的标签
    trip_list_tag = bs.find_all('span',class_='type')

    # 添加出行类型
    for tag in trip_list_tag:
        trip_type_list.append(tag.contents[1])

    return None




'''
爬虫主函数
'''
def crawl(driver,url):
    try:
        # 异常值
        error = None

        # 爬虫计时
        start_time = time.time()

        # 加载界面
        driver.get(url)

        # 等待页面加载完成，超时6秒抛出异常
        WebDriverWait(driver,6).until(EC.presence_of_element_located((By.CLASS_NAME,'c_down')))

        # 拿到页面源码
        html = driver.page_source

        # 利用bs4解析
        bs = BeautifulSoup(html,'lxml')



        '''
        创建参数变量
        '''
        # 创建评论列表，评论数
        comment_list = []
        comment_num = 0

        # 创建评分列表
        total_score_list = []
        envir_score_list = []
        dev_score_list = []
        serv_score_list = []
        clean_score_list = []

        # 创建出行类型的列表
        trip_type_list = []

        # 当前页码
        current_page = 1

        # 寻找需要爬取的页面总数
        pages_sum = bs.find('span',class_='c_page_ellipsis').next_sibling['value']

        # 含有酒店名称的标签
        hotel_name_tag = bs.find(itemprop="name")

        # 提取名称，除去'精选'字段
        if len(hotel_name_tag.contents) > 1:
            hotel_name = hotel_name_tag.contents[1].strip()
        else:
            hotel_name = hotel_name_tag.get_text()


        # 创建酒店评论信息表，存储评论和评分
        create_table(hotel_name)

        # 调用解析函数，获取评论
        comment_parse(bs,comment_list)

        # 更新评论数
        comment_num += len(comment_list)


        # 调用解析函数，获取出行类型
        trip_parse(bs,trip_type_list)


        # 调用解析函数，获取评分
        score_parse(bs,total_score_list,
                        envir_score_list,
                        dev_score_list,
                        serv_score_list,
                        clean_score_list)


        # 评论，评分写入数据库
        insert_info(hotel_name,comment_list,
                                total_score_list,
                                envir_score_list,
                                dev_score_list,
                                serv_score_list,
                                clean_score_list,
                                trip_type_list)



        # 点击下一页的次数是 pages_sum-1 次
        for i in range(int(pages_sum)-1):

            try:
                driver.delete_all_cookies()
                # 点击下一页
                driver.execute_script("document.querySelector('a.c_down').click();")
                # driver.execute_script("window.scrollTo(0,2500);")

                # 当前页面加一
                current_page += 1

                # 等待界面加载，判断当前页的变化，超时6秒抛出异常
                locator = (By.XPATH,'//a[@class="current"]')
                WebDriverWait(driver,6).until(EC.text_to_be_present_in_element(locator, str(current_page)))

                # 等待评论加载出来
                WebDriverWait(driver,6).until(EC.presence_of_element_located((By.CLASS_NAME,'comment_detail_list')))

                # 各个列表置空
                comment_list = []
                total_score_list = []
                envir_score_list = []
                dev_score_list = []
                serv_score_list = []
                clean_score_list = []
                trip_type_list = []

                # 拿到页面源码
                html = driver.page_source

                bs = BeautifulSoup(html,'lxml')

                # 去哪儿评论截止过滤：携程评论最后会有两三百页去哪儿网的评论，没评分，不利于分析，过滤掉
                if len(bs.find_all('span',class_='score')) < 15:
                    break

                # 调用解析函数，获取评论
                comment_parse(bs,comment_list)

                # 更新评论数
                comment_num += len(comment_list)


                # 调用解析函数，获取出行类型
                trip_parse(bs,trip_type_list)


                # 调用解析函数，获取评分
                score_parse(bs,total_score_list,
                                envir_score_list,
                                dev_score_list,
                                serv_score_list,
                                clean_score_list)


                # 评论，评分写入数据库
                insert_info(hotel_name,comment_list,
                                        total_score_list,
                                        envir_score_list,
                                        dev_score_list,
                                        serv_score_list,
                                        clean_score_list,
                                        trip_type_list)

            except TimeoutException:
                print('超时')
                print(current_page)
                print(driver.find_element_by_xpath('//a[@class="current"]').text)
                # continue

            except Exception as e:
                print(e)
                continue


        print(f'共爬取{comment_num}条评论')

        # 获取爬取的日期
        now_time = datetime.datetime.now()
        crawl_date  = f'{now_time.year}-{now_time.month}-{now_time.day}'

        # 获取酒店总体的评分
        hotel_score = float(bs.find('div',class_='comment_total_score').contents[2].contents[0].get_text())

        # 爬虫计时
        end_time = time.time()

        # 爬取时间，单位：分
        crawl_time = round((end_time - start_time)/60,2)

        # 酒店基本信息写进hotel_list表 
        insert_hotel_list(hotel_name, hotel_score, comment_num, crawl_time, crawl_date)
        print('success')

        # 用时
        print(f'本次爬虫共用时{crawl_time}分')

    except Exception as e:
        print(e)
        error = str(e)

    finally:
        driver.quit()
        if error:
            return error
        else:
            return 'success!'


if __name__ == '__main__':
    # browser.delete_all_cookies()

    driver = init_crawl()
    # crawl(driver,'https://hotels.ctrip.com/hotel/4687218.html')   # 迪士尼乐园酒店
    # crawl(driver,'https://hotels.ctrip.com/hotel/4687213.html')    # 迪士尼总动员酒店  1287 1319
