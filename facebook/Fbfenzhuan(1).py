import json
import os.path
import csv
import clr
import re
import time
from functools import reduce
import datetime
from tkinter import scrolledtext
import pyodbc
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from threading import Thread
from tkinter import ttk
import ttkbootstrap as ttk
import requests
from ftplib import FTP
import os
import sys
import subprocess
import threading
from tkinter import messagebox, simpledialog
from tkinter.ttk import Progressbar
import tkinter as tk
import random
pyodbc.pooling = True
#os.environ['PYTHONBREAKPOINT'] = '0'
headers_list = [
    {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'
    }
]
# headers = random.choice(headers_list)#随机请求头
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
def get_cookies():
    global login_num
    global email,password
    # if os.path.exists('login.txt') == True:
    #     with open('login.txt', 'r', encoding='utf-8') as f:
    #         login_inf = f.read()
    #         login_strings = login_inf.split(',')
    #         email = login_strings[0].strip('\n')
    #         password = login_strings[1].strip('\n')
    # else:
    #     email = start_entry.get()
    #     password = end_entry.get()
    #     with open('login.txt', 'w', encoding='utf-8') as f:
    #         f.write(email + "," + password + '\n')
    #     login_num = 1
    #     root.destroy()
    email = start_entry.get()
    password = end_entry.get()
    get_absolute_path('login.txt')
    with open('login.txt', 'w', encoding='utf-8') as f:
        f.write(email + "," + password + '\n')
    login_num = 1
    root.destroy()
    # 启动浏览器
    # driver = webdriver.Chrome()
    chrome_options = Options()
    prefs = {
        'profile.default_content_setting_values':
            {
                'notifications': 2
            }
    }
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Edge(chrome_options)  # 调用火狐浏览器
    # driver = webdriver.Firefox()
    # 打开Facebook登录页面
    driver.get('https://www.facebook.com/')
    time.sleep(1)
    # 查找用户名和密码输入框
    email_element = driver.find_element(By.ID, 'email')
    password_element = driver.find_element(By.ID, 'pass')

    print(email,password)
    email_element.send_keys(email)
    password_element.send_keys(password + Keys.RETURN)
    try:
        # WebDriverWait(driver, 50).until(EC.url_to_be('https://www.facebook.com/'))
        WebDriverWait(driver, 55).until(
            EC.presence_of_element_located(
                (By.XPATH, '//input[@aria-label="搜尋 Facebook" or @aria-label="搜索 Facebook"]'))
        )
        get_absolute_path('login.txt')
        with open('login.txt', 'r', encoding='utf-8') as f:
            login_inf = f.read()
            login_strings = login_inf.split(',')
            email = login_strings[0].strip('\n')
            password = login_strings[1].strip('\n')
            try:
                kongzhi = login_strings[2].strip('\n')
            except Exception:
                try:
                    guanbi_xuanxiang = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//div[@class="html-div x1k74hu9 x1ejq31n xd10rxx x1sy0etr x17r0tee x1rg5ohu xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x3ajldb"]/div/span[2]/div/div'))
                    )
                    guanbi_xuanxiang.click()
                    guanbi_xinxiaoxi = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//input[@aria-label="彈出新訊息" and @aria-checked="true"]'))
                    )
                    driver.execute_script("arguments[0].click();", guanbi_xinxiaoxi)
                    time.sleep(2)
                    guanbi_laidian = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//input[@aria-label="來電音效" and @aria-checked="true"]'))
                    )
                    driver.execute_script("arguments[0].click();", guanbi_laidian)
                    try:
                        dianji_xuanze = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH,
                                                            '//div[@class="x1n2onr6 x1ja2u2z x1afcbsf x78zum5 xdt5ytf x1a2a7pz x6ikm8r x10wlt62 x71s49j x1jx94hy x1qpq9i9 xdney7k xu5ydu1 xt3gfkd x104qc98 x1g2kw80 x16n5opg xl7ujzl xhkep3z x1n7qst7 xh8yej3"]/div[4]/div/div[3]'))
                        )
                        # 执行JavaScript代码
                        dianji_xuanze.click()
                        print("已点击")
                        dianji_tingyong = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@aria-label="停用"]'))
                        )
                        dianji_tingyong.click()
                        print("已点击2")
                        get_absolute_path('login.txt')
                        with open('login.txt', 'a', encoding='utf-8') as f:
                            f.write(",1")
                    except Exception as e:
                        print(f"发生错误: {e}")
                except Exception:
                    print("点过了")
                    get_absolute_path('login.txt')
                    with open('login.txt', 'a', encoding='utf-8') as f:
                        f.write(",1")
    except Exception as e:
        driver.quit()
        print(f"发生错误: {e}")
        # try:
        #     os.remove('login.txt')
        # except FileNotFoundError:
        #     pass
        login()
        return
    # 获取cookie
    Cookies = driver.get_cookies()

    JsCookies = json.dumps(Cookies)
    config_file = get_absolute_path('cookies.txt')
    if os.path.exists(config_file):
        with open("cookies.txt", "w") as f:
            f.write(JsCookies)
        print("Cookies重新写入!")
    else:
        with open("cookies.txt", "w") as f:
            f.write(JsCookies)
        print("Cookies重新写入!")
    driver.quit()  # 退出网站
    if login_log == 1:
        get_Search_data()
    else:
        read_cookies()
def read_cookies():
    global login_log,login_num
    login_log = 2
    chrome_options = Options()
    prefs = {
        'profile.default_content_setting_values':
            {
                'notifications':2
            }
    }
    chrome_options.add_experimental_option('prefs',prefs)
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.page_load_strategy = 'eager'
    global  driver
    # driver = webdriver.Chrome(chrome_options)
    driver = webdriver.Edge(chrome_options)
    # driver = webdriver.Firefox()
    driver.set_script_timeout(50)
    driver.get('https://www.facebook.com/')  # 访问网站
    driver.delete_all_cookies()  # 清除由于浏览器打开已有的cookies
    config_file = get_absolute_path('cookies.txt')
    if os.path.exists(config_file):
    # if os.path.exists('cookies.txt') == True:
        print("存在文件！")
        # 从文件读取cookie
        with open('cookies.txt', 'r') as file:
            Cookies = json.load(file)
            cookie_dit = {}
            for cookie in Cookies:
                cookie_dit[cookie["name"]] = cookie["value"]
                if isinstance(cookie.get('expiry'), float):
                    cookie['expiry'] = int(cookie['expiry'])
                driver.add_cookie(cookie)
    else:
        messagebox.showwarning("賬號錯誤", "未存在本地帳號，請先登錄！" )
        driver.quit()
        login()
        return
    driver.refresh()# 刷新浏览器，刷新后发现网站已经通过cookie登录上了
    try:
        time.sleep(5)
        password_element = driver.find_element(By.NAME, 'pass')
        config_file = get_absolute_path('login.txt')
        if os.path.exists(config_file):
        # if os.path.exists('login.txt') == True:
            with open('login.txt', 'r', encoding='utf-8') as f:
                login_inf = f.read()
                login_strings = login_inf.split(',')
                password = login_strings[1].strip('\n')
        password_element.send_keys(password)
        password_element.submit()
    except Exception:
        print("未找到名为'pass'的元素")
    try:
        # WebDriverWait(driver, 50).until(EC.url_to_be('https://www.facebook.com/'))
        WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located((By.XPATH, '//input[@aria-label="搜尋 Facebook" or @aria-label="搜索 Facebook"]'))
                            )
    except Exception as e:
        print(f"发生错误: {e}")
        driver.quit()
        #再次登录看是否是过期
        global login_num
        if login_num == 1:
            login_num = 2
            get_cookies()
        else:
            # try:
            #     os.remove('login.txt')
            # except FileNotFoundError:
            #     pass
            login()
        return
    config_file = get_absolute_path('input_data.txt')
    if os.path.exists(config_file):
    # if os.path.exists('input_data.txt') == True:
        with open('input_data.txt', 'r', encoding='utf-8') as f:
            break_dada = f.read()
            split_data = break_dada.replace(',', ' ').strip().split()
            if split_data[0] == 'None':
                split_data[0] = ''
        in_search_show = split_data[0]
    else:
        in_search_show = ''
    if in_search_show != '':
        in_search_show = "搜尋内容："+in_search_show
    global show
    global text
    show = tk.Tk()
    show.title("爬取進度"+"    "+in_search_show)
    show.resizable(0, 0)
    url_window(show, 400, 500)
    # text = tk.scrolledtext.ScrolledText(show)
    # text = tk.scrolledtext.ScrolledText(show, bg='#8FDEFC', font=("微软雅黑", 12))
    # text.pack(fill='both', expand=True)
    text = scrolledtext.ScrolledText(show, wrap=tk.WORD, font=("微软雅黑", 12))
    text.pack(expand=True, fill='both')

    # 设置背景颜色
    set_background_color(text, '#8FDEFC')
    start_printing()
    show.mainloop()
def set_background_color(scrolled_text, color):
    # 设置内部 Text 小部件的背景颜色
    scrolled_text.config(bg=color)
    # 设置内部 Text 小部件的插入光标背景颜色
    scrolled_text.config(insertbackground=color)
    # 设置内部 Text 小部件的选择背景颜色
    scrolled_text.config(selectbackground=color)
    # 设置内部 Text 小部件的选择前景颜色
    scrolled_text.config(selectforeground='white')
    # 设置内部 Scrollbar 的背景颜色
    scrolled_text.vbar.config(bg=color)
def login():
    global root
    root = tk.Tk()
    root.title("帳號登錄")
    config_file = get_absolute_path('login.txt')
    if os.path.exists(config_file):
    # if os.path.exists('login.txt') == True:
        with open('login.txt', 'r', encoding='utf-8') as f:
            login_inf = f.read()
            login_strings = login_inf.split(',')
            password = login_strings[1].strip('\n')
            email = login_strings[0].strip('\n')
    else:
        password = ''
        email = ''
    root.resizable(0, 0)
    frame = tk.Frame(root)
    center_window(root, 300, 150)
    frame.pack(padx=10, pady=10)
    global start_entry
    global end_entry
    start_label = tk.Label(frame, text="FB帳號：")
    start_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    start_entry = tk.Entry(frame)
    start_entry.insert(tk.END, email)
    start_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    frame2 = tk.Frame(root)
    frame2.pack(padx=10, pady=10)
    end_label = tk.Label(frame2, text="FB密碼 ：")
    end_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    end_entry = tk.Entry(frame2)
    end_entry.insert(tk.END, password)
    end_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    export_button = tk.Button(root, text="登錄", command=get_cookies)
    export_button.pack()
    root.attributes("-topmost", True)
    root.mainloop()
def get_text():
    global text_content, getsetuanrenshu,shebeibianhao,xuanzekuang,login_num
    getsetuanrenshu = getnum_entry.get()
    shebeibianhao = shebei_entry.get()
    # xuanzekuang = radio_var.get()
    selected_value = combo_var.get()
    option_to_number = {"社團": 1, "粉絲專業": 2}  # 字典用于映射选项到数字
    xuanzekuang = option_to_number[selected_value]  # 将选中的字符串值转换为数字
    login_num = 1
    text_content = listbox.get('0.0', 'end').replace(' ', '').rstrip('\n').split("\n")
    if any(item == '' for item in text_content):
        messagebox.showwarning("社團錯誤", "數據爲空請輸入社團鏈接！")
    print(text_content)
    print("len(text_content):",len(text_content))
    if xuanzekuang == 1:
        url_links = []
        for i in range(len(text_content)):
            link = text_content[i].split("/")
            link = link[4]
            url_links.append(link)
        set1 = set(url_links)
        set2 = set(result)
        intersection = set1.intersection(set2)
        jiaoji_bidui = ["https://www.facebook.com/groups/" + v + "/members" for v in intersection]
        if intersection:
            print("有数据存在")
            # 将相同的社团链接存储在一个字符串中
            error_links = ",\n".join(["https://www.facebook.com/groups/" + item + "/members" for item in intersection])
            qidonglianxu = check_var.get()
            if qidonglianxu == False:
                # 显示弹窗
                messagebox.showwarning("社團錯誤", "該社團獲取過：" + error_links)
                time.sleep(1)
            text_content = [x for x in text_content if x not in jiaoji_bidui]
            if not text_content:
                messagebox.showwarning("社團錯誤", "該社團全部獲取過！")
                listbox.delete(0, tk.END)
                return
        else:
            print("没有数据存在")
    text_content = list(dict.fromkeys(text_content))
    print("text_content:",text_content)
    global search_text, get_num
    try:
        print("搜索内容：",search_text,get_num)
    except Exception:
        search_text = 'None'
        get_num = 0
    config_file = get_absolute_path('input_data.txt')
    if os.path.exists(config_file):
    # if os.path.exists('input_data.txt') == True:
        get_num = num_entry.get()
        search_text = Search_entry.get()
        if search_text == '' or get_num == '':
            search_text = 'None'
            get_num = 0
    # with open('equipment.txt', 'w', newline='', encoding='utf-8') as t:
    #     t.write(str(shebeibianhao))
    with open('input_data.txt', 'w', encoding='utf-8') as f:
        f.write(str(search_text)+ "," + str(get_num)  + "," + str(getsetuanrenshu)+ "," +str(shebeibianhao) + "," + str(xuanzekuang) + "," + str(text_content))
    window.destroy()
    read_cookies()

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height-100 - height) / 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
def print_output(text_widget, interval=1):
    print("社團！")
    url_list = text_content
    societies_num = 0
    societies_user_num_max = 0
    upstart_time = datetime.datetime.now()
    global societies_in
    global e,r,v
    global societies_up_num
    connection_string = (
        r"Driver={SQL Server};"
        r"Server=dbs.kydb.vip;"
        r"Database=FbSocietiesUser;"
        r"UID=sa;"
        r"PWD=Yunsin@#861123823_shp4;"
        r"timeout=35;"  # 增加timeout值
    )
    conn = pyodbc.connect(connection_string, timeout=35,pooling=True)
    # 创建游标
    cursor = conn.cursor()
    if os.path.exists('Societiesuser.txt') == True:
        with open('Societiesuser.txt', 'r', encoding='utf-8') as file:
            societies_inf = file.readlines()
            societies_strings = societies_inf[-1]
            societies_strings = societies_strings.strip(',')
            societies_u = societies_strings.split(',')[-2].strip()
            societies_up_num = societies_strings.split(',')[-1].strip()
            societies_u = 'https://www.facebook.com/groups/'+societies_u+'/members'
            link = societies_u.split("/")
            link = link[4]
        cursor.execute("SELECT societiesid FROM societiesInf")
        societies_id = cursor.fetchall()
        societies_id_str = [str(id_tuple[0]) for id_tuple in societies_id]
    else:
        link = ''
        societies_id_str = ''
    if link not in societies_id_str:
        url_list.insert(0, societies_u)
        func = lambda x, y: x if y in x else x + [y]
        url_list = reduce(func, [[], ] + url_list)
        societies_in = 1
        print("societies_u 不在 societies_id 里面")
        threads = []  # 用于存储线程
        for i in range(len(url_list)):
            print(url_list[i])
            societies_user_num = 0
            congxin_link2 = 0
            start_time = datetime.datetime.now()
            # 创建一个新的CSV文件名
            csv_filename = f'data_{i}.csv'
            # 准备要插入的数据
            in_csv_data = []
            driver.get(url_list[i])
            try:
                number = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//span[@class="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x6prxxf xvq8zen xo1l8bm xi81zsa"]/strong'))
                )
                number = number.text
                number = int(re.sub('[ ·,()\']', '', number))
                print("成员总人数：", number)
            except Exception:
                continue
            Societies_name = driver.find_element(By.XPATH,
                                                 '//div[@class="x1e56ztr x1xmf6yo"]/h1/span/a')
            Societies_name = Societies_name.text
            print("社团名字：", Societies_name)
            text_widget.insert('end', '社團名字：' + Societies_name + '\n')
            text_widget.insert('end', '社團成員縂人數：' + str(number) + '\n')
            href, name, image = [], [], []
            serial_number = 0
            if societies_in == 1:
                with open('Societiesuser.txt', 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    ult = [[line.split(',')[:2]] for line in lines]
                    href = [item for sublist in ult for item in sublist[0]]
                    serial_number = int(societies_up_num)
                with open('Societiesuser.txt', 'r', newline='', encoding='utf-8') as txtfile:
                    for line in txtfile:
                        data = line.strip().split(',')
                        if len(data) == 4:
                            userid, username, societiesid, _ = data
                            in_csv_data.append([userid, username, societiesid])
            if os.path.exists('Societiesuser.txt') == True and societies_in == 2:
                os.remove('Societiesuser.txt')
            if serial_number > int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                serial_number = 0
            same_link_count = 0
            last_three_links = []
            url_id = url_list[i].split("/")
            Societies_url_id = url_id[4]
            g = []
            while 1:
                time.sleep(interval)
                js_scroll_down = "window.scrollBy(0, 1000);"
                try:
                    driver.execute_script(js_scroll_down)
                    time.sleep(3)
                    wait = WebDriverWait(driver, 35)
                    element = wait.until(EC.presence_of_all_elements_located((By.XPATH,
                                                                               "//div[@class='x78zum5 xdt5ytf x1xmf6yo x1e56ztr xq8finb x1n2onr6 xqcrz7y']//span/span/a")))
                    # element = driver.find_elements(By.XPATH,
                    #                                '//div[@class="x78zum5 xdt5ytf xq8finb x1xmf6yo x1e56ztr x1n2onr6 xqcrz7y"]/span/span/a')

                    # print("len element: ", len(element))
                    if serial_number >= 300:
                        element = element[-30:]
                    for e in element:
                        if e.text != None and e.get_attribute("href") != None:
                            r, v = e.get_attribute("href"), e.get_attribute("aria-label")
                            pattern = re.compile(r'(\d+)(?!.*\d)')
                            match = pattern.search(r)
                            if match == None:
                                continue
                            if match:
                                r = match.group()
                            g.append(r)
                            if societies_in ==1 and href[-2] in g:
                                if r in href:
                                    continue
                                else:
                                    href.append(r)
                                    href.append(v)
                                print(r, v)
                                serial_number = serial_number + 1
                                text_widget.insert('end', str(serial_number) + '  ' + r + ' ' + v + '\n')
                                text_widget.see('end')  # 滚动到最后一行
                                text_widget.update()  # 更新UI，以显示最新的输出
                                in_csv_data.append([r, v, Societies_url_id])
                                with open('Societiesuser.txt', 'a', encoding='utf-8') as f:
                                    f.write(r + "," + v + "," + Societies_url_id + "," + str(serial_number) + '\n')
                                if serial_number == int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                                    print("獲取數量：", int(getsetuanrenshu), serial_number)
                                    break
                            if societies_in == 2:
                                if r in href:
                                    continue
                                else:
                                    href.append(r)
                                    href.append(v)
                                # print(r, v)
                                serial_number = serial_number + 1
                                text_widget.insert('end', str(serial_number) + '  ' + r + ' ' + v + '\n')
                                text_widget.see('end')  # 滚动到最后一行
                                text_widget.update()  # 更新UI，以显示最新的输出
                                in_csv_data.append([r, v, Societies_url_id])
                                with open('Societiesuser.txt', 'a', encoding='utf-8') as f:
                                    f.write(r + "," + v + "," + Societies_url_id + "," + str(serial_number) + '\n')
                                if serial_number == int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                                    print("獲取數量：", int(getsetuanrenshu), serial_number)
                                    break
                    if serial_number == int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                        print("獲取數量：",int(getsetuanrenshu),serial_number)
                        with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                            file.write("社團名字："+Societies_name+" 地址："+ url_list[i]+" 數量："+ str(int(len(href)/2)) +'\n')
                        break
                    if societies_in == 1 and  href[-2] in g:
                        last_three_links.append(href[-2])
                        if len(last_three_links) > 3:
                            last_three_links.pop(0)
                        if len(last_three_links) == 3 and len(set(last_three_links)) == 1:
                            same_link_count += 1
                        else:
                            same_link_count = 0
                        if same_link_count == 3:
                            with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                                file.write("社團名字：" + Societies_name + " 地址：" + url_list[i] + " 數量：" + str(
                                    int(len(href) / 2)) + '\n')
                            break
                    if societies_in == 2:
                        last_three_links.append(href[-2])
                        if len(last_three_links) > 3:
                            last_three_links.pop(0)
                        if len(last_three_links) == 3 and len(set(last_three_links)) == 1:
                            same_link_count += 1
                        else:
                            same_link_count = 0
                        if same_link_count == 3:
                            with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                                file.write("社團名字：" + Societies_name + " 地址：" + url_list[i] + " 數量：" + str(
                                    int(len(href) / 2)) + '\n')
                            break
                    js_scroll_down = "window.scrollBy(0, 1000);"
                    driver.execute_script(js_scroll_down)
                    time.sleep(3)
                except Exception as ex:
                    print("错误：", ex)
                    driver.refresh()
                    time.sleep(3)
                    with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                        file.write("社團名字：" + Societies_name + " 地址：" + url_list[i] + " 數量：" + str(
                            int(len(href) / 2)) + '\n')
                    break
                time.sleep(interval)
            # 将数据写入CSV文件
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['userid', 'username', 'societiesid'])  # 写入表头
                csv_writer.writerows(in_csv_data)  # 写入数据

            # 创建并启动一个线程来提交数据
            thread = threading.Thread(target=submit_data_to_database,
                                      args=(connection_string, csv_filename, i + 1, societiesid_fenzu))
            threads.append(thread)
            thread.start()
            end_time = datetime.datetime.now()
            text_widget.insert('end', '------獲取完成！----' + '\n')
            text_widget.insert('end', '獲取社團人數：' + str(serial_number) + '\n')
            text_widget.insert('end', '耗時：' + str(end_time - start_time) + '\n')
            text_widget.insert('end', '-------------------' + '\n')
            text_widget.see('end')
            societies_num = societies_num + 1
            societies_user_num = societies_user_num + serial_number
            societies_user_num_max = societies_user_num_max + societies_user_num
            cursor.close()
            conn.close()
            try:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                print("societiesInf:", Societies_url_id, Societies_name, number, serial_number)
                if serial_number > 0:
                    cursor.execute("INSERT INTO societiesInf (societiesid,societiesname,number,getnum) VALUES (?,?,?,?)",
                                   Societies_url_id, Societies_name, number, serial_number)
                    print("----")
                    conn.commit()
            except Exception:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                print("societiesInf:",Societies_url_id, Societies_name, number, serial_number)
                cursor.execute("INSERT INTO societiesInf (societiesid,societiesname,number,getnum) VALUES (?,?,?,?)",
                               Societies_url_id, Societies_name, number, serial_number)
                print("----")
                conn.commit()
            print("获取完成！")
            upend_time = datetime.datetime.now()
            try:
                # 建立数据库连接
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()

                cursor.execute("""
                                        MERGE INTO upData AS target
                                        USING (VALUES (?, ?, ?)) AS source(deviceName, updatanumber, uptime)
                                        ON target.deviceName = source.deviceName AND CAST(target.uptime AS DATE) = CAST(source.uptime AS DATE)
                                        WHEN MATCHED THEN
                                            UPDATE SET target.updatanumber = target.updatanumber + source.updatanumber,
                                                       target.uptime = source.uptime
                                        WHEN NOT MATCHED THEN
                                            INSERT (deviceName, updatanumber, uptime)
                                            VALUES (source.deviceName, source.updatanumber, source.uptime);
                                    """, shebeibianhao, societies_user_num, upend_time)

                # 提交更改
                conn.commit()
            except Exception as e:
                print(f"An error occurred: {e}")
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()

                cursor.execute("""
                                        MERGE INTO upData AS target
                                        USING (VALUES (?, ?, ?)) AS source(deviceName, updatanumber, uptime)
                                        ON target.deviceName = source.deviceName AND CAST(target.uptime AS DATE) = CAST(source.uptime AS DATE)
                                        WHEN MATCHED THEN
                                            UPDATE SET target.updatanumber = target.updatanumber + source.updatanumber,
                                                       target.uptime = source.uptime
                                        WHEN NOT MATCHED THEN
                                            INSERT (deviceName, updatanumber, uptime)
                                            VALUES (source.deviceName, source.updatanumber, source.uptime);
                                    """, shebeibianhao, societies_user_num, upend_time)

                conn.commit()
            with open('uptime.txt', 'a', encoding='utf-8') as file:
                file.write("設備：" + str(shebeibianhao) + " 數量：" + str(societies_user_num) + " 時間：" + str(
                    upend_time) + '\n')
            societies_in = 2
            print(len(href))
        text_widget.insert('end', '等待所有任務完成請勿關閉...------------' + '\n')
        text_widget.insert('end', '請勿關閉!------------' + '\n')
        text_widget.insert('end', '請勿關閉!------------' + '\n')
        text_widget.see('end')
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        text_widget.insert('end', '-------全部社團爬取完成！！------' + '\n')
        print("全部社团爬取完成！")
        text_widget.insert('end',
                           '獲取社團數：' + str(societies_num) + ' 爬取社團總人數:' + str(societies_user_num_max) + '\n')
        text_widget.see('end')
        upend_time2 = datetime.datetime.now()
        if os.path.exists('input_data.txt') == True:
            with open('input_data.txt', 'w', encoding='utf-8') as f:
                f.write(str(search_text) + "," + str(get_num) + "," + str(getsetuanrenshu) + "," + str(shebeibianhao) + "," + str(xuanzekuang) + "," + "None")
        text_widget.insert('end', '縂耗時：' + str(upend_time2 - upstart_time) + '\n')
        text_widget.see('end')
        cursor.close()
        conn.close()
    else:
        print("societies_u 在 societies_id 里面")
        threads = []  # 用于存储线程
        for i in range(len(url_list)):
            print(url_list[i])
            societies_user_num = 0
            start_time = datetime.datetime.now()
            # 创建一个新的CSV文件名
            csv_filename = f'data_{i}.csv'
            # 准备要插入的数据
            in_csv_data = []
            driver.get(url_list[i])  # 访问网站
            try:
                number = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//span[@class="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x6prxxf xvq8zen xo1l8bm xi81zsa"]/strong'))
                )
                number = number.text
                number = int(re.sub('[ ·,()\']', '', number))
                print("成员总人数：", number)
            except Exception:
                continue
            Societies_name = driver.find_element(By.XPATH,
                                                 '//div[@class="x1e56ztr x1xmf6yo"]/h1/span/a')
            Societies_name = Societies_name.text
            print("社团名字：", Societies_name)
            text_widget.insert('end', '社團名字：'+ Societies_name +'\n')
            text_widget.insert('end', '社團成員總人數：' + str(number) + '\n')
            href, name, image = [], [], []  # 重复
            if os.path.exists('Societiesuser.txt') == True:
                os.remove('Societiesuser.txt')
            serial_number = 0
            same_link_count = 0
            last_three_links = []
            url_id = url_list[i].split("/")
            Societies_url_id = url_id[4]
            while 1:
                time.sleep(interval)
                js_scroll_down = "window.scrollBy(0, 1000);"
                try:
                    driver.execute_script(js_scroll_down)
                    time.sleep(3)
                    # element = driver.find_elements(By.XPATH,
                    #                                '//div[@class="x78zum5 xdt5ytf xq8finb x1xmf6yo x1e56ztr x1n2onr6 xqcrz7y"]/span/span/a')
                    wait = WebDriverWait(driver, 35)
                    element = wait.until(EC.presence_of_all_elements_located((By.XPATH,
                                                                              "//div[@class='x78zum5 xdt5ytf x1xmf6yo x1e56ztr xq8finb x1n2onr6 xqcrz7y']//span/span/a")))
                    # print("len element: ", len(element))
                    if serial_number >= 300:
                        element = element[-30:]
                    for e in element:
                        if e.text != None and e.get_attribute("href") != None:
                            r, v = e.get_attribute("href"), e.get_attribute("aria-label")
                            pattern = re.compile(r'(\d+)(?!.*\d)')
                            match = pattern.search(r)
                            if match == None:
                                continue
                            if match:
                                r = match.group()
                            if r in href:
                                continue
                            else:
                                href.append(r)
                                href.append(v)
                            # print(r, v)
                            serial_number = serial_number+1
                            text_widget.insert('end', str(serial_number)+'  '+r + ' ' + v + '\n')
                            text_widget.see('end')  # 滚动到最后一行
                            text_widget.update()  # 更新UI，以显示最新的输出
                            in_csv_data.append([r, v, Societies_url_id])
                            with open('Societiesuser.txt', 'a', encoding='utf-8') as f:
                                f.write(r + "," + v + "," + Societies_url_id + "," + str(serial_number) + '\n')
                            if serial_number == int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                                print("獲取數量：", int(getsetuanrenshu), serial_number)
                                break
                    if serial_number == int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                        print("獲取數量：", int(getsetuanrenshu),serial_number)
                        with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                            file.write("社團名字："+Societies_name+" 地址："+ url_list[i]+" 數量："+ str(int(len(href)/2)) +'\n')
                        break
                    last_three_links.append(href[-2])
                    if len(last_three_links) > 3:
                        last_three_links.pop(0)
                    if len(last_three_links) == 3 and len(set(last_three_links)) == 1:
                        same_link_count += 1
                    else:
                        same_link_count = 0
                    if same_link_count == 3:
                        with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                            file.write("社團名字："+Societies_name+" 地址："+ url_list[i]+" 數量："+ str(int(len(href)/2)) +'\n')
                        break
                    js_scroll_down = "window.scrollBy(0, 1000);"
                    driver.execute_script(js_scroll_down)
                    time.sleep(3)
                except Exception as ex:
                    print("错误：",ex)
                    driver.refresh()
                    time.sleep(3)
                    with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                        file.write("社團名字：" + Societies_name + " 地址：" + url_list[i] + " 數量：" + str(
                            int(len(href) / 2)) + '\n')
                    break
                time.sleep(interval)
            # 将数据写入CSV文件
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['userid', 'username', 'societiesid'])  # 写入表头
                csv_writer.writerows(in_csv_data)  # 写入数据

            # 创建并启动一个线程来提交数据
            thread = threading.Thread(target=submit_data_to_database,
                                      args=(connection_string, csv_filename, i + 1, societiesid_fenzu))
            threads.append(thread)
            thread.start()
            end_time = datetime.datetime.now()
            text_widget.insert('end', '------獲取完成！----'+'\n')
            text_widget.insert('end', '獲取人數：' + str(serial_number)+'\n')
            text_widget.insert('end', '耗時：' + str(end_time - start_time) + '\n')
            text_widget.insert('end', '-------------------'+ '\n')
            text_widget.see('end')
            societies_num = societies_num+1
            societies_user_num = societies_user_num + serial_number
            societies_user_num_max = societies_user_num_max + societies_user_num
            # cursor.close()
            # conn.close()
            try:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                print("societiesInf:", Societies_url_id, Societies_name, number, serial_number)
                if serial_number > 0:
                    cursor.execute("INSERT INTO societiesInf (societiesid,societiesname,number,getnum) VALUES (?,?,?,?)",
                                   Societies_url_id, Societies_name, number, serial_number)
                    print("----")
                    # 提交更改并关闭连接
                    conn.commit()
            except Exception:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                print("societiesInf:",Societies_url_id, Societies_name, number, serial_number)
                if serial_number > 0:
                    cursor.execute("INSERT INTO societiesInf (societiesid,societiesname,number,getnum) VALUES (?,?,?,?)",
                                   Societies_url_id, Societies_name, number, serial_number)
                    print("----")
                    # 提交更改并关闭连接
                    conn.commit()
            print("获取完成！")
            upend_time = datetime.datetime.now()
            try:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                # 使用 MERGE 语句
                cursor.execute("""
                        MERGE INTO upData AS target
                        USING (VALUES (?, ?, ?)) AS source(deviceName, updatanumber, uptime)
                        ON target.deviceName = source.deviceName AND CAST(target.uptime AS DATE) = CAST(source.uptime AS DATE)
                        WHEN MATCHED THEN
                            UPDATE SET target.updatanumber = target.updatanumber + source.updatanumber,
                                       target.uptime = source.uptime
                        WHEN NOT MATCHED THEN
                            INSERT (deviceName, updatanumber, uptime)
                            VALUES (source.deviceName, source.updatanumber, source.uptime);
                    """, shebeibianhao, societies_user_num, upend_time)
                conn.commit()
            except Exception:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                # 使用 MERGE 语句
                cursor.execute("""
                        MERGE INTO upData AS target
                        USING (VALUES (?, ?, ?)) AS source(deviceName, updatanumber, uptime)
                        ON target.deviceName = source.deviceName AND CAST(target.uptime AS DATE) = CAST(source.uptime AS DATE)
                        WHEN MATCHED THEN
                            UPDATE SET target.updatanumber = target.updatanumber + source.updatanumber,
                                       target.uptime = source.uptime
                        WHEN NOT MATCHED THEN
                            INSERT (deviceName, updatanumber, uptime)
                            VALUES (source.deviceName, source.updatanumber, source.uptime);
                    """, shebeibianhao, societies_user_num, upend_time)
                # 提交更改并关闭连接
                conn.commit()
            with open('uptime.txt', 'a', encoding='utf-8') as file:
                file.write("設備：" + str(shebeibianhao) + " 數量：" + str(societies_user_num) + " 時間：" + str(
                    upend_time) + '\n')
            print(len(href))
        text_widget.insert('end', '等待所有任務完成請勿關閉...------------' + '\n')
        text_widget.insert('end', '請勿關閉!------------' + '\n')
        text_widget.insert('end', '請勿關閉!------------' + '\n')
        text_widget.see('end')
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        text_widget.insert('end', '-------全部社團爬取完成！！------' + '\n')
        print("全部社团爬取完成！")
        text_widget.insert('end', '獲取社團數：' + str(societies_num) + ' 爬取社團縂人數:'+str(societies_user_num_max)+'\n')
        text_widget.see('end')  # 滚动到最后一行
        upend_time2 = datetime.datetime.now()
        if os.path.exists('input_data.txt') == True:
            with open('input_data.txt', 'w', encoding='utf-8') as f:
                f.write(str(search_text) + "," + str(get_num) + "," + str(getsetuanrenshu) + "," + str(
                    shebeibianhao) + "," + str(xuanzekuang) + "," + "None")
        text_widget.insert('end', '縂耗時：' + str(upend_time2 - upstart_time) + '\n')
        text_widget.see('end')
        # 关闭Cursor:
        cursor.close()
        # 关闭连接
        conn.close()
        # show.destroy()
def print_output2(text_widget, interval=1):
    print("粉絲專業！")
    url_list = text_content
    new_urls = []
    for url in url_list:
        if '/profile.php?' in url:
            # 对于 profile.php 类型的链接
            parts = url.split('?')
            new_url = f"{parts[0]}?{parts[1]}&sk=followers"
        else:
            # 对于其他类型的链接
            new_url = f"{url}/followers"
        new_urls.append(new_url)
    url_list = new_urls
    societies_num = 0
    societies_user_num_max = 0
    upstart_time = datetime.datetime.now()
    global societies_in
    global e,r,v
    global societies_up_num
    connection_string = (
        r"Driver={SQL Server};"
        r"Server=dbs.kydb.vip;"
        r"Database=FbSocietiesUser;"
        r"UID=sa;"
        r"PWD=Yunsin@#861123823_shp4;"
        r"timeout=35;"  # 增加timeout值
    )
    conn = pyodbc.connect(connection_string,timeout=25,pooling=True)
    # 创建游标
    cursor = conn.cursor()
    if os.path.exists('Fansuser.txt') == True:
        with open('Fansuser.txt', 'r', encoding='utf-8') as file:
            societies_inf = file.readlines()
            societies_strings = societies_inf[-1]
            societies_strings = societies_strings.strip(',')
            societies_u = societies_strings.split(',')[-2].strip()
            societies_up_num = societies_strings.split(',')[-1].strip()
            if '/profile.php?' in societies_u:
                # 对于 profile.php 类型的链接
                parts = societies_u.split('?')
                societies_u = f"{parts[0]}?{parts[1]}&sk=followers"
            else:
                # 对于其他类型的链接
                societies_u = f"{societies_u}/followers"
            societies_u = 'https://www.facebook.com/'+societies_u
            if '/profile.php?' in societies_u:
                # 提取profile.php类型链接中的id
                id_match = re.search(r'id=(\d+)', societies_u)
                if id_match:
                    link = id_match.group(1)
            else:
                # 提取其他类型链接中的用户名
                path_parts = societies_u.split('/')
                link = path_parts[-2]
        cursor.execute("SELECT userid FROM FansInf")
        societies_id = cursor.fetchall()
        societies_id_str = [str(id_tuple[0]) for id_tuple in societies_id]
    else:
        link = ''
        societies_id_str = ''
    if link not in societies_id_str:
        url_list.insert(0, societies_u)
        func = lambda x, y: x if y in x else x + [y]
        url_list = reduce(func, [[], ] + url_list)
        societies_in = 1
        print("societies_u 不在 societies_id 里面")
        threads = []  # 用于存储线程
        for i in range(len(url_list)):
            print(url_list[i])
            societies_user_num = 0
            congxin_link2 = 0
            start_time = datetime.datetime.now()
            # 创建一个新的CSV文件名
            csv_filename = f'data_{i}.csv'
            # 准备要插入的数据
            in_csv_data = []
            driver.get(url_list[i])
            try:
                Fans_name = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//div[@class="x1e56ztr x1xmf6yo"]/span/h1'))
                ).text
                print("Fans_name:", Fans_name)
            except Exception:
                continue
            number = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//div[@class="x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x1iyjqo2 x2lwn1j"]/div[2]/span/a[2]'))
            ).text
            text_widget.insert('end', '粉絲專業名字：' + Fans_name + '\n')
            text_widget.insert('end', '追蹤者總人數：' + str(number) + '\n')
            href, name, image = [], [], []
            serial_number = 0
            if societies_in == 1:
                with open('Fansuser.txt', 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    ult = [[line.split(',')[:2]] for line in lines]
                    href = [item for sublist in ult for item in sublist[0]]
                    serial_number = int(societies_up_num)
                with open('Fansuser.txt', 'r', newline='', encoding='utf-8') as txtfile:
                    for line in txtfile:
                        data = line.strip().split(',')
                        if len(data) == 4:
                            userid, username, societiesid, _ = data
                            in_csv_data.append([userid, username, societiesid])
            if os.path.exists('Fansuser.txt') == True and societies_in == 2:
                os.remove('Fansuser.txt')
            if serial_number > int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                serial_number = 0
            same_link_count = 0
            last_three_links = []
            if '/profile.php?' in url_list[i]:
                # 提取profile.php类型链接中的id
                id_match = re.search(r'id=(\d+)', url_list[i])
                if id_match:
                    url_id = id_match.group(1)
            else:
                # 提取其他类型链接中的用户名
                path_parts = url_list[i].split('/')
                url_id = path_parts[-2]
            Societies_url_id = url_id
            g = []
            while 1:
                time.sleep(interval)
                js_scroll_down = "window.scrollBy(0, 1000);"
                try:
                    driver.execute_script(js_scroll_down)
                    time.sleep(3)
                    wait = WebDriverWait(driver, 25)
                    Fans_userid_list = wait.until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                       "//div[@data-pagelet='ProfileAppSection_0']/div/div/div/div[2]/div[3]/div/div[2]/div/a")))
                    Fans_username_list = wait.until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                         "//div[@data-pagelet='ProfileAppSection_0']/div/div/div/div[2]/div[3]/div/div[2]/div/a/span")))
                    if serial_number >= 300:
                        Fans_userid_list = Fans_userid_list[-30:]
                    if serial_number >= 300:
                        Fans_username_list = Fans_username_list[-30:]
                    for Fans_user, Fans_username in zip(Fans_userid_list, Fans_username_list):
                        if Fans_username.text != None and Fans_user.get_attribute("href") != None:
                            p, o = Fans_user.get_attribute("href"), Fans_username.text
                            if '/profile.php?' in p:
                                # 提取profile.php类型链接中的id
                                id_match = re.search(r'id=(\d+)', p)
                                if id_match:
                                    p = id_match.group(1)
                            else:
                                # 提取其他类型链接中的用户名
                                path_parts = p.split('/')
                                p = path_parts[-1]
                            g.append(p)
                            if societies_in ==1 and href[-2] in g:
                                if p in href:
                                    continue
                                else:
                                    href.append(p)
                                    href.append(o)
                                print(p, o)
                                serial_number = serial_number + 1
                                text_widget.insert('end', str(serial_number) + '  ' + p + ' ' + o + '\n')
                                text_widget.see('end')  # 滚动到最后一行
                                text_widget.update()  # 更新UI，以显示最新的输出
                                in_csv_data.append([p, o, Societies_url_id])
                                with open('Fansuser.txt', 'a', encoding='utf-8') as f:
                                    f.write(p + "," + o + "," + Societies_url_id + "," + str(serial_number) + '\n')
                                if serial_number == int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                                    print("獲取數量：", int(getsetuanrenshu), serial_number)
                                    break
                            if societies_in == 2:
                                if p in href:
                                    continue
                                else:
                                    href.append(p)
                                    href.append(o)
                                # print(p, o)
                                serial_number = serial_number + 1
                                text_widget.insert('end', str(serial_number) + '  ' + p + ' ' + o + '\n')
                                text_widget.see('end')  # 滚动到最后一行
                                text_widget.update()  # 更新UI，以显示最新的输出
                                in_csv_data.append([p, o, Societies_url_id])
                                with open('Fansuser.txt', 'a', encoding='utf-8') as f:
                                    f.write(p + "," + o + "," + Societies_url_id + "," + str(serial_number) + '\n')
                                if serial_number == int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                                    print("獲取數量：", int(getsetuanrenshu), serial_number)
                                    break
                    if serial_number == int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                        print("獲取數量：",int(getsetuanrenshu),serial_number)
                        with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                            file.write("粉絲專頁名字："+Fans_name+" 地址："+ url_list[i]+" 數量："+ str(int(len(href)/2)) +'\n')
                        break
                    if societies_in == 1 and  href[-2] in g:
                        last_three_links.append(href[-2])
                        if len(last_three_links) > 3:
                            last_three_links.pop(0)
                        if len(last_three_links) == 3 and len(set(last_three_links)) == 1:
                            same_link_count += 1
                        else:
                            same_link_count = 0
                        if same_link_count == 3:
                            with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                                file.write("粉絲專頁名字：" + Fans_name + " 地址：" + url_list[i] + " 數量：" + str(
                                    int(len(href) / 2)) + '\n')
                            break
                    if societies_in == 2:
                        last_three_links.append(href[-2])
                        if len(last_three_links) > 3:
                            last_three_links.pop(0)
                        if len(last_three_links) == 3 and len(set(last_three_links)) == 1:
                            same_link_count += 1
                        else:
                            same_link_count = 0
                        if same_link_count == 3:
                            with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                                file.write("粉絲專頁名字：" + Fans_name + " 地址：" + url_list[i] + " 數量：" + str(
                                    int(len(href) / 2)) + '\n')
                            break
                    js_scroll_down = "window.scrollBy(0, 1000);"
                    driver.execute_script(js_scroll_down)
                    time.sleep(3)
                except Exception as ex:
                    print("错误：", ex)
                    # driver.refresh()
                    time.sleep(3)
                    with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                        file.write("粉絲專頁名字：" + Fans_name + " 地址：" + url_list[i] + " 數量：" + str(
                            int(len(href) / 2)) + '\n')
                    break
                time.sleep(interval)
            # 将数据写入CSV文件
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['userid', 'username', 'societiesid'])  # 写入表头
                csv_writer.writerows(in_csv_data)  # 写入数据

            # 创建并启动一个线程来提交数据
            thread = threading.Thread(target=submit_data_to_database,
                                      args=(connection_string, csv_filename, i + 1, societiesid_fenzu))
            threads.append(thread)
            thread.start()
            end_time = datetime.datetime.now()
            text_widget.insert('end', '------獲取完成！----' + '\n')
            text_widget.insert('end', '獲取粉絲專頁人數：' + str(serial_number) + '\n')
            text_widget.insert('end', '耗時：' + str(end_time - start_time) + '\n')
            text_widget.insert('end', '-------------------' + '\n')
            text_widget.see('end')
            societies_num = societies_num + 1
            societies_user_num = societies_user_num + serial_number
            societies_user_num_max = societies_user_num_max + societies_user_num
            # cursor.close()
            # conn.close()
            try:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                print("societiesInf:", Societies_url_id, Fans_name, number, serial_number)
                cursor.execute("INSERT INTO FansInf (societiesid,societiesname,number,getnum) VALUES (?,?,?,?)",
                               Societies_url_id, Fans_name, number, serial_number)
                print("----")
                conn.commit()
            except Exception:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                print("societiesInf:",Societies_url_id, Fans_name, number, serial_number)
                cursor.execute("INSERT INTO FansInf (societiesid,societiesname,number,getnum) VALUES (?,?,?,?)",
                               Societies_url_id, Fans_name, number, serial_number)
                print("----")
                conn.commit()
            print("获取完成！")
            upend_time = datetime.datetime.now()
            try:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                cursor.execute("""
                                        MERGE INTO upData AS target
                                        USING (VALUES (?, ?, ?)) AS source(deviceName, updatanumber, uptime)
                                        ON target.deviceName = source.deviceName AND CAST(target.uptime AS DATE) = CAST(source.uptime AS DATE)
                                        WHEN MATCHED THEN
                                            UPDATE SET target.updatanumber = target.updatanumber + source.updatanumber,
                                                       target.uptime = source.uptime
                                        WHEN NOT MATCHED THEN
                                            INSERT (deviceName, updatanumber, uptime)
                                            VALUES (source.deviceName, source.updatanumber, source.uptime);
                                    """, shebeibianhao, societies_user_num, upend_time)
                # 提交更改并关闭连接
                conn.commit()
            except Exception:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                cursor.execute("""
                                        MERGE INTO upData AS target
                                        USING (VALUES (?, ?, ?)) AS source(deviceName, updatanumber, uptime)
                                        ON target.deviceName = source.deviceName AND CAST(target.uptime AS DATE) = CAST(source.uptime AS DATE)
                                        WHEN MATCHED THEN
                                            UPDATE SET target.updatanumber = target.updatanumber + source.updatanumber,
                                                       target.uptime = source.uptime
                                        WHEN NOT MATCHED THEN
                                            INSERT (deviceName, updatanumber, uptime)
                                            VALUES (source.deviceName, source.updatanumber, source.uptime);
                                    """, shebeibianhao, societies_user_num, upend_time)
                # 提交更改并关闭连接
                conn.commit()
            with open('uptime.txt', 'a', encoding='utf-8') as file:
                file.write("設備：" + str(shebeibianhao) + " 數量：" + str(societies_user_num) + " 時間：" + str(
                    upend_time) + '\n')
            societies_in = 2
            print(len(href))
        text_widget.insert('end', '等待所有任務完成請勿關閉...------------' + '\n')
        text_widget.insert('end', '請勿關閉!------------' + '\n')
        text_widget.insert('end', '請勿關閉!------------' + '\n')
        text_widget.see('end')
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        text_widget.insert('end', '-------全部粉絲專頁爬取完成！！------' + '\n')
        print("全部粉絲專頁爬取完成！")
        text_widget.insert('end',
                           '獲取粉絲專頁數：' + str(societies_num) + ' 爬取粉絲專頁追蹤者總人數:' + str(societies_user_num_max) + '\n')
        text_widget.see('end')
        upend_time2 = datetime.datetime.now()
        if os.path.exists('input_data.txt') == True:
            with open('input_data.txt', 'w', encoding='utf-8') as f:
                f.write(str(search_text) + "," + str(get_num) + "," + str(getsetuanrenshu) + "," + str(
                    shebeibianhao) + "," + str(xuanzekuang) + "," + "None")
        text_widget.insert('end', '縂耗時：' + str(upend_time2 - upstart_time) + '\n')
        text_widget.see('end')
        cursor.close()
        conn.close()
    else:
        print("societies_u 在 societies_id 里面")
        threads = []  # 用于存储线程
        for i in range(len(url_list)):
            print(url_list[i])
            societies_user_num = 0
            start_time = datetime.datetime.now()
            # 创建一个新的CSV文件名
            csv_filename = f'data_{i}.csv'
            # 准备要插入的数据
            in_csv_data = []
            driver.get(url_list[i])  # 访问网站
            try:
                Fans_name = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//div[@class="x1e56ztr x1xmf6yo"]/span/h1'))
                ).text
                print("Fans_name:", Fans_name)
            except Exception:
                continue
            number = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//div[@class="x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x1iyjqo2 x2lwn1j"]/div[2]/span/a[2]'))
            ).text
            text_widget.insert('end', '粉絲專頁名字：'+ Fans_name +'\n')
            text_widget.insert('end', '追蹤者總人數：' + str(number) + '\n')
            href, name, image = [], [], []  # 重复
            if os.path.exists('Fansuser.txt') == True:
                os.remove('Fansuser.txt')
            serial_number = 0
            same_link_count = 0
            last_three_links = []
            if '/profile.php?' in url_list[i]:
                # 提取profile.php类型链接中的id
                id_match = re.search(r'id=(\d+)', url_list[i])
                if id_match:
                    url_id = id_match.group(1)
            else:
                # 提取其他类型链接中的用户名
                path_parts = url_list[i].split('/')
                url_id = path_parts[-2]
            Societies_url_id = url_id
            while 1:
                time.sleep(interval)
                js_scroll_down = "window.scrollBy(0, 1000);"
                try:
                    driver.execute_script(js_scroll_down)
                    time.sleep(3)
                    wait = WebDriverWait(driver, 25)
                    Fans_userid_list = wait.until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                       "//div[@data-pagelet='ProfileAppSection_0']/div/div/div/div[2]/div[3]/div/div[2]/div/a")))
                    Fans_username_list = wait.until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                         "//div[@data-pagelet='ProfileAppSection_0']/div/div/div/div[2]/div[3]/div/div[2]/div/a/span")))
                    if serial_number >= 300:
                        Fans_userid_list = Fans_userid_list[-30:]
                    if serial_number >= 300:
                        Fans_username_list = Fans_username_list[-30:]
                    for Fans_user, Fans_username in zip(Fans_userid_list, Fans_username_list):
                        if Fans_username.text != None and Fans_user.get_attribute("href") != None:
                            p, o = Fans_user.get_attribute("href"), Fans_username.text
                            if '/profile.php?' in p:
                                # 提取profile.php类型链接中的id
                                id_match = re.search(r'id=(\d+)', p)
                                if id_match:
                                    p = id_match.group(1)
                            else:
                                # 提取其他类型链接中的用户名
                                path_parts = p.split('/')
                                p = path_parts[-1]
                            if p in href:
                                continue
                            else:
                                href.append(p)
                                href.append(o)
                            # print(r, v)
                            serial_number = serial_number+1
                            text_widget.insert('end', str(serial_number)+'  '+p + ' ' + o + '\n')
                            text_widget.see('end')  # 滚动到最后一行
                            text_widget.update()  # 更新UI，以显示最新的输出
                            in_csv_data.append([p, o, Societies_url_id])
                            with open('Fansuser.txt', 'a', encoding='utf-8') as f:
                                f.write(p + "," + o + "," + Societies_url_id + "," + str(serial_number) + '\n')
                            if serial_number == int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                                print("獲取數量：", int(getsetuanrenshu), serial_number)
                                break
                    if serial_number == int(getsetuanrenshu) and int(getsetuanrenshu) != 0:
                        print("獲取數量：", int(getsetuanrenshu),serial_number)
                        with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                            file.write("粉絲專頁名字："+Fans_name+" 地址："+ url_list[i]+" 數量："+ str(int(len(href)/2)) +'\n')
                        break
                    last_three_links.append(href[-2])
                    if len(last_three_links) > 3:
                        last_three_links.pop(0)
                    if len(last_three_links) == 3 and len(set(last_three_links)) == 1:
                        same_link_count += 1
                    else:
                        same_link_count = 0
                    if same_link_count == 3:
                        with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                            file.write("粉絲專頁名字："+Fans_name+" 地址："+ url_list[i]+" 數量："+ str(int(len(href)/2)) +'\n')
                        break
                    js_scroll_down = "window.scrollBy(0, 1000);"
                    driver.execute_script(js_scroll_down)
                    time.sleep(3)
                except Exception as ex:
                    print("错误：",ex)
                    # driver.refresh()
                    time.sleep(3)
                    with open('Societieslog.txt', 'a', encoding='utf-8') as file:
                        file.write("粉絲專頁名字：" + Fans_name + " 地址：" + url_list[i] + " 數量：" + str(
                            int(len(href) / 2)) + '\n')
                    break
                time.sleep(interval)
            # 将数据写入CSV文件
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['userid', 'username', 'societiesid'])  # 写入表头
                csv_writer.writerows(in_csv_data)  # 写入数据

            # 创建并启动一个线程来提交数据
            thread = threading.Thread(target=submit_data_to_database,
                                      args=(connection_string, csv_filename, i + 1, societiesid_fenzu))
            threads.append(thread)
            thread.start()
            end_time = datetime.datetime.now()
            text_widget.insert('end', '------獲取完成！----'+'\n')
            text_widget.insert('end', '獲取人數：' + str(serial_number)+'\n')
            text_widget.insert('end', '耗時：' + str(end_time - start_time) + '\n')
            text_widget.insert('end', '-------------------'+ '\n')
            text_widget.see('end')
            societies_num = societies_num + 1
            societies_user_num = societies_user_num + serial_number
            societies_user_num_max = societies_user_num_max + societies_user_num
            # cursor.close()
            # conn.close()
            try:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                print("FansInf:", Societies_url_id, Fans_name, number, serial_number)
                cursor.execute("INSERT INTO FansInf (userid,fansname,number,getnum) VALUES (?,?,?,?)",
                               Societies_url_id, Fans_name, number, serial_number)
                print("----")
                # 提交更改并关闭连接
                conn.commit()
                print("获取完成！")
                print(len(href))
            except Exception:
                conn = pyodbc.connect(connection_string, timeout=35,pooling=True)
                cursor = conn.cursor()
                print("FansInf:",Societies_url_id, Fans_name, number, serial_number)
                cursor.execute("INSERT INTO FansInf (userid,fansname,number,getnum) VALUES (?,?,?,?)",
                               Societies_url_id, Fans_name, number, serial_number)
                print("----")
                # 提交更改并关闭连接
                conn.commit()
            print("获取完成！")
            upend_time = datetime.datetime.now()
            try:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                cursor.execute("""
                                        MERGE INTO upData AS target
                                        USING (VALUES (?, ?, ?)) AS source(deviceName, updatanumber, uptime)
                                        ON target.deviceName = source.deviceName AND CAST(target.uptime AS DATE) = CAST(source.uptime AS DATE)
                                        WHEN MATCHED THEN
                                            UPDATE SET target.updatanumber = target.updatanumber + source.updatanumber,
                                                       target.uptime = source.uptime
                                        WHEN NOT MATCHED THEN
                                            INSERT (deviceName, updatanumber, uptime)
                                            VALUES (source.deviceName, source.updatanumber, source.uptime);
                                    """, shebeibianhao, societies_user_num, upend_time)
                # 提交更改并关闭连接
                conn.commit()
            except Exception:
                conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
                cursor = conn.cursor()
                cursor.execute("""
                                        MERGE INTO upData AS target
                                        USING (VALUES (?, ?, ?)) AS source(deviceName, updatanumber, uptime)
                                        ON target.deviceName = source.deviceName AND CAST(target.uptime AS DATE) = CAST(source.uptime AS DATE)
                                        WHEN MATCHED THEN
                                            UPDATE SET target.updatanumber = target.updatanumber + source.updatanumber,
                                                       target.uptime = source.uptime
                                        WHEN NOT MATCHED THEN
                                            INSERT (deviceName, updatanumber, uptime)
                                            VALUES (source.deviceName, source.updatanumber, source.uptime);
                                    """, shebeibianhao, societies_user_num, upend_time)
                # 提交更改并关闭连接
                conn.commit()
            with open('uptime.txt', 'a', encoding='utf-8') as file:
                file.write("設備：" + str(shebeibianhao) + " 數量：" + str(societies_user_num) + " 時間：" + str(
                    upend_time) + '\n')
            print(len(href))
        text_widget.insert('end', '等待所有任務完成請勿關閉...------------' + '\n')
        text_widget.insert('end', '請勿關閉!------------' + '\n')
        text_widget.insert('end', '請勿關閉!------------' + '\n')
        text_widget.see('end')
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        text_widget.insert('end', '-------全部粉絲專頁爬取完成！！------' + '\n')
        print("全部粉絲專頁爬取完成！")
        text_widget.insert('end', '獲取粉絲專頁數：' + str(societies_num) + ' 爬取粉絲專頁追蹤者縂人數:'+str(societies_user_num_max)+'\n')
        text_widget.see('end')  # 滚动到最后一行
        upend_time2 = datetime.datetime.now()
        if os.path.exists('input_data.txt') == True:
            with open('input_data.txt', 'w', encoding='utf-8') as f:
                f.write(str(search_text) + "," + str(get_num) + "," + str(getsetuanrenshu) + "," + str(
                    shebeibianhao) + "," + str(xuanzekuang) + "," + "None")
        text_widget.insert('end', '縂耗時：' + str(upend_time2 - upstart_time) + '\n')
        text_widget.see('end')
        # 关闭Cursor:
        cursor.close()
        # 关闭连接
        conn.close()



        # show.destroy()
def submit_data_to_database(connection_string, csv_filename, batch_number, societiesid_fenzu):
    conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
    cursor = conn.cursor()
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # 跳过表头
        data = list(csv_reader)
        print(f"线程 {batch_number}: 开始提交数据...")
        batch_size = 80  # 你可以根据实际情况调整这个值
        for i in range(0, len(data), batch_size):
            batch_data = data[i:i + batch_size]
            insert_data_to_database(cursor, batch_data)
            conn.commit()  # 每一批提交一次
            sleep_time = random.uniform(8, 14)
            time.sleep(sleep_time)
        print(f"线程 {batch_number}: 提交完成。")
        user_ids = [row[0] for row in data]
        print(len(user_ids))
    cursor.close()
    conn.close()
    print(f"完成: ",csv_filename)
    os.remove(csv_filename)
def submit_data_to_database2(connection_string, csv_filename, batch_number, societiesid_fenzu):
    # 连接到数据库
    conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
    cursor = conn.cursor()

    # 从CSV文件中读取数据并插入数据库
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # 跳过表头
        data = list(csv_reader)
        print(f"线程 {batch_number}: 开始提交数据...")
        # insert_data_to_database(cursor, data)
        # # 提交数据到数据库
        # conn.commit()
        batch_size = 100  # 你可以根据实际情况调整这个值
        for i in range(0, len(data), batch_size):
            batch_data = data[i:i + batch_size]
            insert_data_to_database(cursor, batch_data)
            conn.commit()  # 每一批提交一次
            sleep_time = random.uniform(5, 10)
            time.sleep(sleep_time)
        print(f"线程 {batch_number}: 提交完成。")

        # 获取userid并执行societiesid_fenzu
        user_ids = [row[0] for row in data]
        print(len(user_ids))
        # for user_id in user_ids:
        #     print("当前位置：",csv_filename,user_id)
        #     societiesid_fenzu(user_id, cursor, conn)

    # 关闭游标和连接
    cursor.close()
    conn.close()
    print(f"完成: ",csv_filename)
    # 删除CSV文件（可选）
    os.remove(csv_filename)
def insert_data_to_database(cursor, data):
    # 使用executemany插入数据
    if xuanzekuang == 1:
        cursor.executemany(
            "INSERT INTO societiesUser (userid, username, societiesid) VALUES (?, ?, ?)",
            data
        )
    else:
        cursor.executemany(
            "INSERT INTO FansUser (userid, username, societiesid) VALUES (?, ?, ?)",
            data
        )
def societiesid_fenzu(user_ids, cursor, conn):
    userid = user_ids
    try:
        cursor.execute("SELECT societiesid FROM societiesUser WHERE userid = ?", (userid,))
        data = cursor.fetchall()
        joinsocieties_value = ','.join(str(d[0]) for d in data)  # 假设d[0]是需要拼接的值
        update_query = "UPDATE societiesUser SET joinsocieties = ? WHERE userid = ?"
        cursor.execute(update_query, (joinsocieties_value, userid))  # 注意这里是直接execute而非executemany，因为我们只更新一个userid对应的记录
        conn.commit()
    except Exception as ex:
        print("错误位置：",ex)
        connection_string = (
            r"Driver={SQL Server};"
            r"Server=dbs.kydb.vip;"
            r"Database=FbSocietiesUser;"
            r"UID=sa;"
            r"PWD=Yunsin@#861123823_shp4;"
            r"timeout=35;"  # 增加timeout值
        )
        conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
        # 创建游标
        cursor = conn.cursor()
        cursor.execute("SELECT societiesid FROM societiesUser WHERE userid = ?", (userid,))
        data = cursor.fetchall()
        joinsocieties_value = ','.join(str(d[0]) for d in data)  # 假设d[0]是需要拼接的值
        update_query = "UPDATE societiesUser SET joinsocieties = ? WHERE userid = ?"
        cursor.execute(update_query, (joinsocieties_value, userid))  # 注意这里是直接execute而非executemany，因为我们只更新一个userid对应的记录
        conn.commit()

def start_printing():
    if xuanzekuang == 1:# 创建一个线程来运行持续的打印任务
        Thread(target=print_output, args=(text, 1),daemon=True).start()
    else:
        Thread(target=print_output2, args=(text, 1), daemon=True).start()
def url_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width - width) / 1.2)
    y = int((screen_height-100 - height) / 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
def data_bidui():
    cursor.execute("SELECT * FROM societiesUser")
    data = cursor.fetchall()
    result = {}
    update_data = []
    for row in data:
        key = row[1]
        if key not in result:
            result[key] = []
        result[key].append(row[3])
    for key, values in result.items():
        result[key] = ",".join(str(value) for value in values)
        update_data.append((result[key], key))
def up_sql():
    # 设置连接字符串
    connection_string = (
        r"Driver={SQL Server};"
        r"Server=dbs.kydb.vip;"
        r"Database=FbSocietiesUser;"
        r"UID=sa;"
        r"PWD=Yunsin@#861123823_shp4;"
        r"timeout=35;"  # 增加timeout值
    )
    global cursor,conn
    conn = pyodbc.connect(connection_string, timeout=35, pooling=True)
    # 创建游标
    cursor = conn.cursor()
    cursor.execute("SELECT societiesid FROM societiesInf")
    results = cursor.fetchall()
    # 遍历并打印结果集:
    lists = []
    for row in results:
        lists.append(tuple(row))
    unique_data = list(set(lists))
    global result
    result = [item[0] for item in unique_data]
def get_Search_data():
    global  data_list,login_log
    # danxuankuang_value = radio_var.get()
    selected_value = combo_var.get()
    option_to_number = {"社團": 1, "粉絲專頁": 2}  # 字典用于映射选项到数字
    danxuankuang_value = option_to_number[selected_value]  # 将选中的字符串值转换为数字
    print("danxuankuang_value:",danxuankuang_value)
    login_log = 1
    chrome_options = Options()
    prefs = {
        'profile.default_content_setting_values':
            {
                'notifications':2
            }
    }
    chrome_options.add_experimental_option('prefs',prefs)
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.page_load_strategy = 'eager'
    # driver = webdriver.Chrome(chrome_options)
    driver = webdriver.Edge(chrome_options)  # 调用火狐浏览器
    # driver = webdriver.Firefox()
    driver.set_script_timeout(60)
    driver.get('https://www.facebook.com/')  # 访问网站
    driver.set_window_size(550, 800)
    driver.delete_all_cookies()  # 清除由于浏览器打开已有的cookies
    config_file = get_absolute_path('cookies.txt')
    if os.path.exists(config_file):
    # if os.path.exists('cookies.txt') == True:
        print("存在文件！1")
        # 从文件读取cookie
        with open('cookies.txt', 'r') as file:
            Cookies = json.load(file)
            cookie_dit = {}
            for cookie in Cookies:
                cookie_dit[cookie["name"]] = cookie["value"]
                if isinstance(cookie.get('expiry'), float):
                    cookie['expiry'] = int(cookie['expiry'])
                driver.add_cookie(cookie)
    else:
        messagebox.showwarning("賬號錯誤", "未存在本地賬號，請先登錄！" )
        driver.quit()
        login()
        return
    driver.refresh()  # 刷新浏览器，刷新后发现网站已经通过cookie登录上了
    try:
        time.sleep(5)
        password_element = driver.find_element(By.NAME, 'pass')
        config_file = get_absolute_path('login.txt')
        if os.path.exists(config_file):
        # if os.path.exists('login.txt') == True:
            with open('login.txt', 'r', encoding='utf-8') as f:
                login_inf = f.read()
                login_strings = login_inf.split(',')
                password = login_strings[1].strip('\n')
        password_element.send_keys(password)
        password_element.submit()
    except Exception:
        print("未找到名为'pass'的元素")
    try:
        # WebDriverWait(driver, 35).until(EC.url_to_be('https://www.facebook.com/'))
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, '//input[@aria-label="搜尋 Facebook" or @aria-label="搜索 Facebook"]'))
        )
    except Exception:
        driver.quit()
        global login_num
        if login_num == 1:
            login_num = 2
            get_cookies()
        else:
            try:
                get_absolute_path('login.txt')
                os.remove('login.txt')
            except FileNotFoundError:
                pass
            login()
        return
    data_list = []
    global get_num,search_text
    get_num = int(num_entry.get())
    search_text = Search_entry.get()
    if danxuankuang_value == 1:
        Search_input = f"https://www.facebook.com/search/groups?q={search_text}&filters=eyJwdWJsaWNfZ3JvdXBzOjAiOiJ7XCJuYW1lXCI6XCJwdWJsaWNfZ3JvdXBzXCIsXCJhcmdzXCI6XCJcIn0ifQ%3D%3D"
    else:
        Search_input = f"https://www.facebook.com/search/pages?q={search_text}"
    driver.get(Search_input)
    # js_scroll_down = "window.scrollBy(0, 1000);"
    # driver.execute_script(js_scroll_down)
    same_link_count = 0
    last_three_links = []
    num_count = 0
    while 1:
        js_scroll_down = "window.scrollBy(0, 1000);"
        driver.execute_script(js_scroll_down)
        # Search_input = driver.find_elements(By.XPATH,
        #                                    '//div[@class="xu06os2 x1ok221b"]/span/div/a')
        wait = WebDriverWait(driver, 35)
        Search_input = wait.until(EC.presence_of_all_elements_located((By.XPATH,
                                                                  "//div[@class='xu06os2 x1ok221b']/span/div//a[contains(@class, 'x1i10hfl') and contains(@class, 'xjbqb8w')]")))
        if danxuankuang_value == 1:
            for shetuan_url in Search_input:
                shetuan_dizi = shetuan_url.get_attribute("href")
                if shetuan_dizi+"members" not in data_list and len(data_list) != get_num or get_num == 0 and shetuan_dizi+"members" not in data_list:
                    data_list.append(shetuan_dizi+"members")
                    listbox.insert(tk.END, str(data_list[num_count]) + '\n')
                    listbox.see(tk.END)  # 滚动到最后一行
                    num_count +=1
            if len(data_list) == get_num and get_num != 0:
               break
            last_three_links.append(data_list[-1])
            if len(last_three_links) > 3:
                last_three_links.pop(0)
            if len(last_three_links) == 3 and len(set(last_three_links)) == 1:
                same_link_count += 1
            else:
                same_link_count = 0
            if same_link_count == 3:
                break
        else:
            for shetuan_url in Search_input:
                shetuan_dizi = shetuan_url.get_attribute("href")
                if shetuan_dizi not in data_list and (len(data_list) < get_num or get_num == 0):
                    data_list.append(shetuan_dizi)
                    listbox.insert(tk.END, str(data_list[num_count]) + '\n')
                    listbox.see(tk.END)  # 滚动到最后一行
                    num_count += 1
            if len(data_list) == get_num and get_num != 0:
               break
            last_three_links.append(data_list[-1])
            if len(last_three_links) > 3:
                last_three_links.pop(0)
            if len(last_three_links) == 3 and len(set(last_three_links)) == 1:
                same_link_count += 1
            else:
                same_link_count = 0
            if same_link_count == 3:
                break
        time.sleep(2)
    print(data_list)
    print(len(data_list))

def Get_shouquan(get_result):
    # 数据库连接字符串
    connection_string = (
        r"Driver={SQL Server};"
        r"Server=dbs.kydb.vip;"
        r"Database=LINEGroupSend;"
        r"UID=sa;"
        r"PWD=Yunsin@#861123823_shp4;"
        r"timeout=35;"  # 增加timeout值
    )

    try:
        # 连接数据库
        conn = pyodbc.connect(connection_string,timeout=35, pooling=True)
        cursor = conn.cursor()

        # SQL查询语句
        query = """
            SELECT PCCoded, installDate, ExpiryDate 
            FROM FBUserData 
            WHERE PCCoded = ?
        """
        cursor.execute(query, (get_result,))
        shujuku_results = cursor.fetchall()
        global  days_remaining
        # 输出查询结果
        if shujuku_results:
            for row in shujuku_results:
                PCCoded = row[0]
                installDate = row[1]
                ExpiryDate = row[2]

                current_date = datetime.datetime.now().date()
                installDate = installDate.date()
                ExpiryDate = ExpiryDate.date()

                if installDate <= current_date <= ExpiryDate:
                    print("当前日期在有效期内。")
                    days_remaining = (ExpiryDate - current_date).days
                    # messagebox.showinfo("成功提示", f"授權成功！還剩{days_remaining}天。")
                    set_societies()
                else:
                    print("当前日期不在有效期内。")
                    messagebox.showwarning("過期提示", "當前日期不在有效期內！請聯係客服！")
        else:
            print("沒有授權！")
            messagebox.showwarning("授權提示", "當前設備沒有授權！")
            # 如果查询结果为空，则弹出输入框
            input_value = simpledialog.askstring(" ", "機器碼:",initialvalue=get_result)
            if input_value:
                print(f"输入的内容是: {input_value}")
                if input_value != get_result:
                    messagebox.showwarning("授權提示", "當前授權碼與本機授權不一致！請重試！")
                else:
                    Get_shouquan(input_value)
            else:
                print("用户取消了输入。")
    except pyodbc.Error as e:
        print(f"数据库连接或查询错误：{e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()
def resource_path(relative_path):
    """ 获取资源文件绝对路径 """
    try:
        # PyInstaller 创建临时文件夹，所有打包的文件都在这个文件夹下面
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
def on_closing():
    if messagebox.askokcancel("退出", "確定退出程序嗎？"):
        window.destroy()
def set_societies():
    # if os.path.exists('equipment.txt') == True:
    #     with open('equipment.txt', 'r', newline='', encoding='utf-8') as x:
    #         equipment = x.read()
    #     split_data = ['', 0, 2024, equipment, 1]
    # else:
    #     split_data = ['',0,2024,'001',1]

    split_data = ['', 0, 2025, '001', 1]
    split_data2 = []
    config_file = get_absolute_path('input_data.txt')
    if os.path.exists(config_file):
    # if os.path.exists('input_data.txt') == True:
        with open('input_data.txt', 'r', encoding='utf-8') as f:
            break_dada = f.read()
            split_data = break_dada.replace(',', ' ').strip().split()
            print(split_data)
            if split_data[0] == 'None':
                split_data[0] = ''
            if split_data[5] == 'None':
                split_data[5] = ''
            else:
                split_data2 = split_data[5:]
    global Search_entry, listbox, window, num_entry,getnum_entry,shebei_entry,radio_var,check_var,Yes_button,combo_var
    window = tk.Tk()
    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.title("全盈 雲控")
    center_window(window, 458, 420)
    # main_frame = Labelframe(window, padding="5",bootstyle="info",text="aaa")
    # window.iconbitmap(resource_path('turtle.png'))
    window.resizable(0,0)
    # 定义样式
    style = ttk.Style()
    style.configure('TFrame', background='#f3d751')  # 指定背景颜色
    style.configure('TLabel', background='#f3d751')
    # style.configure('TButton', background='#f0f0f0')
    style.configure('TRadiobutton', background='#f3d751')
    style.configure('TCheckbutton', background='#f3d751')
    # style.configure('TButton', background='#f3d751')
    main_frame = ttk.Frame(window, style='TFrame')
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    # 创建 Canvas
    # canvas = tk.Canvas(window, bg="white")
    # canvas.pack(fill=tk.BOTH, expand=True)
    #
    # # 绘制圆角矩形
    # round_rectangle(canvas, 10, 10, 446, 400, radius=25, fill="#f0f0f0")
    #
    # # 创建主框架
    # main_frame = ttk.Frame(canvas)
    # main_frame.place(x=20, y=20, width=526, height=470)

    # # 加载背景图片
    # background_image = Image.open("br.png")  # 替换为您的图片路径
    # background_photo = ImageTk.PhotoImage(background_image)
    # background_label = tk.Label(main_frame, image=background_photo)
    # background_label.place(x=0, y=0, relwidth=1, relheight=1)  # 将图片作为背景填充整个窗口

    # # 设置字体和 DPI
    # default_font = ("Arial", 9)
    # window.option_add("*Font", default_font)
    print(split_data[0],split_data[1],split_data[2],split_data[3],split_data[4],split_data[5])
    Search_entry = ttk.Entry(main_frame, width=32)
    Search_entry.grid(row=0, column=0, padx=5, pady=5)
    Search_entry.insert(tk.END, split_data[0])
    search_button = ttk.Button(main_frame, text="搜尋",width=7)
    search_button.grid(row=0, column=1, padx=5, pady=5)
    num_label = ttk.Label(main_frame, text="搜尋數量：")
    num_label.place(height=20, width=60, x=25, y=47)
    num_entry = ttk.Entry(main_frame, width=10)
    num_entry.insert(tk.END, split_data[1])
    num_entry.grid(row=1, column=0, padx=1, pady=3)
    getnum_label = ttk.Label(main_frame, text="爬取人數：")
    getnum_label.place(height=20, width=110, x=208, y=47)
    getnum_entry = ttk.Entry(main_frame, width=10)
    getnum_entry.insert(tk.END, split_data[2])
    # getnum_entry.grid(row=1, column=1, padx=1, pady=3)
    getnum_entry.place(height=31, width=85, x=280, y=45)
    shebei_label = ttk.Label(main_frame, text="設備编号：")
    shebei_label.place(height=20, width=60, x=25, y=85)
    shebei_entry = ttk.Entry(main_frame, width=10)
    shebei_entry.insert(tk.END, split_data[3])
    shebei_entry.grid(row=2, column=0, padx=1, pady=3)
    # 创建 IntVar 对象来跟踪当前的选择
    # radio_var = IntVar(value=int(split_data[4]))  # 设置默认选中项的值，这里设置为第一个单选按钮
    # # 创建并放置单选按钮
    # Radiobutton(main_frame, text="社團", variable=radio_var, value=1, padding=1).place(height=20, width=50, x=195,
    #                                                                                    y=85)
    # Radiobutton(main_frame, text="粉絲專業", variable=radio_var, value=2, padding=1).place(height=20, width=75, x=255,y=85)
    # 创建并放置下拉框
    # 设置默认选中项的值，这里设置为第一个选项
    default_value = int(split_data[4])
    options=["社團","粉絲專頁"]  # 下拉框选项
    combo_var = ttk.StringVar(value=options[default_value - 1])  # 设置默认选中项

    combobox = ttk.Combobox(main_frame, textvariable=combo_var, values=options, state='readonly',bootstyle="primary")
    combobox.place(height=25, width=110, x=208, y=85)

    # 勾选框
    check_var = ttk.BooleanVar()
    checkbutton = ttk.Checkbutton(main_frame, text="啓用連續", variable=check_var, padding=1)
    checkbutton.place(height=20, width=80, x=340, y=88)

    scrollbar = ttk.Scrollbar(main_frame, orient="vertical",bootstyle="round")
    scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
    listbox = tk.Text(main_frame, width=60, height=14, yscrollcommand=scrollbar.set)
    listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
    for item in split_data2:
        item = item.strip('\'][')+'\n'
        listbox.insert(tk.END, item)
    scrollbar.config(command=listbox.yview)
    Yes_button = ttk.Button(main_frame, text="確定",width=7, command=get_text)
    Yes_button.grid(row=4, column=1, padx=5, pady=5)

    version_label = ttk.Label(main_frame, text=f"版本: {version}")

    # 使用 .place() 方法将标签定位到主框架的左下角
    # 注意，这里使用了相对位置，x 和 y 分别表示从左边和下边的偏移量
    version_label.place(relx=0.0, rely=1.0, x=10, y=-10, anchor=tk.SW)
    # 创建一个标签用于显示版本号
    version_time_label = ttk.Label(main_frame, text=f"剩餘時長: {days_remaining} 天")

    # 使用 .place() 方法将标签定位到主框架的左下角
    # 注意，这里使用了相对位置，x 和 y 分别表示从左边和下边的偏移量
    version_time_label.place(relx=0.0, rely=1.0, x=105, y=-10, anchor=tk.SW)

    def on_search_click():
        search_thread = threading.Thread(target=search_thread_func)
        search_thread.daemon = True  # 设置为守护线程，主线程退出时自动结束
        search_thread.start()  # 启动搜索的线程

    search_button.config(command=on_search_click)  # 将搜索按钮的命令更改为启动新线程的函数
    # 将数据库查询操作放在一个新的线程中执行
    t = threading.Thread(target=up_sql)
    t.start()
    t.join()
    window.mainloop()

def cleanup():
    messagebox.showinfo("程序停止", "程序結束！" )
def search_thread_func():
    global data_list,login_num
    login_num =1
    if Search_entry.get() == '':
        messagebox.showinfo("輸入提示", "搜索內容為空！")
        return
    get_Search_data()
    qidonglianxu = check_var.get()
    print("選擇框：",qidonglianxu)
    if qidonglianxu == True:
       Yes_button.invoke()
def connect_ftp(host, port, user, password):
    ftp = FTP()
    try:
        ftp.connect(host, port, timeout=10)
        ftp.login(user, password)
        print("FTP 连接建立成功。")
        return ftp
    except Exception as e:
        print(f"FTP 连接失败： {e}")
        return None

def download_file_with_progress(ftp, remote_path, local_path, progress_var, progress_label):
    try:
        directory = '/'.join(remote_path.split('/')[:-1])
        ftp.cwd(directory)
        filename = remote_path.split('/')[-1]
        files = ftp.nlst()  # 使用nlst来获取目录列表
        if filename not in files:
            print(f"文件 {filename} 不存在。")
            return
        file_size = ftp.size(filename)
        bytes_downloaded = 0
        with open(local_path, 'wb') as file:
            def callback(data):
                nonlocal bytes_downloaded
                file.write(data)
                bytes_downloaded += len(data)
                progress_var.set(int((bytes_downloaded / file_size) * 100))
                progress_label.config(text=f"下載進度: {bytes_downloaded}/{file_size} ({bytes_downloaded / file_size * 100:.2f}%)")
                root.update()  # 更新GUI
            ftp.retrbinary(f'RETR {filename}', callback, blocksize=8192)
        print(f"文件 {filename} 下载成功。")
        create_shutdown_and_extract_script(local_path)
    except Exception as e:
        print(f"下载文件时发生错误： {e}")

def create_shutdown_and_extract_script(zip_file_path):
    script_content = (
        f'@echo off\n'
        f'echo 关闭当前程序...\n'
        f'taskkill /F /IM {os.path.basename(sys.executable)}\n'
        f':CHECK\n'
        f'tasklist | findstr /I /C:"{os.path.basename(sys.executable)}" >nul\n'
        f'if %errorlevel%==0 (\n'
        f'    timeout /T 1 /NOBREAK >nul\n'
        f'    goto CHECK\n'
        f')\n'
        f'echo 删除旧程序...\n'
        f'del "{os.path.basename(sys.executable)}"\n'
        f'echo 解压新程序...\n'
        f'powershell -Command "Add-Type -Assembly \"System.IO.Compression.FileSystem\"; [IO.Compression.ZipFile]::ExtractToDirectory(\'{zip_file_path}\', \'.\')"\n'
        f'echo 启动新程序...\n'
        f'start .\\Fbfenzhuan.exe\n'
        f'echo 删除压缩包...\n'
        f'del "%~dp0%{zip_file_path}"  >nul 2>&1\n'
        f'echo 删除更新脚本...\n'
        f'del update.bat\n'
    )
    get_absolute_path('update.bat')
    with open('update.bat', 'w', encoding='utf-8') as bat_file:
        bat_file.write(script_content)
    print("批处理文件创建完成，请手动运行 update.bat 完成更新。")

def get_real_path():
    """
    获取应用程序的真实路径。
    """
    if getattr(sys, 'frozen', False):  # 判断是否为打包后的exe文件
        application_path = os.path.dirname(sys.executable)  # 打包后的exe路径
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))  # 脚本路径
    return application_path

def get_absolute_path(relative_path):
    """
    将相对路径转换为基于应用程序安装目录的绝对路径。
    """
    application_path = get_real_path()
    return os.path.join(application_path, relative_path)

def create_registry_file():
    """
    创建注册表文件并导入注册表。
    """
    # 使用绝对路径生成注册表文件
    regeditfile = get_absolute_path('regeditfile.reg')
    sstap_path = get_absolute_path("Fbfenzhuan.exe")
    sstap_path_registry = sstap_path.replace("\\", "\\\\")

    script_content = (
        'Windows Registry Editor Version 5.00\n\n'
        '[HKEY_CLASSES_ROOT\\myAppProtocol]\n'
        '@="URL:myAppProtocol Protocol"\n'
        '"URL Protocol"=""\n\n'
        '[HKEY_CLASSES_ROOT\\myAppProtocol\\DefaultIcon]\n'
        f'@="{sstap_path_registry},1"\n\n'
        '[HKEY_CLASSES_ROOT\\myAppProtocol\\shell]\n\n'
        '[HKEY_CLASSES_ROOT\\myAppProtocol\\shell\\open]\n\n'
        '[HKEY_CLASSES_ROOT\\myAppProtocol\\shell\\open\\command]\n'
        f'@="\\"{sstap_path_registry}\\" \\"%1\\""\n'
    )

    if not os.path.exists(regeditfile):
        try:
            with open(regeditfile, 'w', encoding='utf-8') as reg_file:
                reg_file.write(script_content)
            print("注册表文件创建完成，正在导入注册表...")

            # 等待片刻以确保文件已完全写入磁盘
            time.sleep(2)

            if os.path.exists(regeditfile):
                os.system(f'regedit /s "{regeditfile}"')  # 使用 'reg import' 而不是 'regedit /s'
                print("注册表导入完成。")
            else:
                print("注册表文件未找到，无法导入。")
        except PermissionError:
            print("权限不足，无法创建或修改注册表文件。请以管理员身份运行程序。")
        except Exception as e:
            print(f"发生了一个错误: {e}")

def center_window3(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
def install_new_version_thread(version, remote_version):
    def install():
        global root
        root = tk.Tk()
        root.withdraw()
        answer = messagebox.askyesno("新版本可用",
                                     f"檢測到新版本：\n当前版本：{version}\n最新版本：{remote_version}\n是否立即下載最新版本？")
        if answer:
            ftp, local_path = main_ftp()
            if ftp:
                progress_var = tk.IntVar()
                progress_var.set(0)
                progress_label = tk.Label(root, text="下載進度: 0/0 (0.00%)")
                progress_label.pack(pady=5)
                root.deiconify()
                root.title("下載更新")
                center_window3(root, 300, 100)
                root.resizable(0, 0)
                progress_bar = Progressbar(root, variable=progress_var, maximum=100, length=250)
                progress_bar.pack(pady=15)
                def start_download():
                    download_file_with_progress(ftp, '/UpData/FBfans/FBfans.zip', local_path, progress_var, progress_label)
                    ftp.quit()
                    messagebox.showinfo("更新完成", "下載完成。等待重新啟動。")
                    subprocess.run("update.bat",creationflags=subprocess.CREATE_NO_WINDOW)
                    # root.destroy()
                threading.Thread(target=start_download).start()
                root.mainloop()
            else:
                messagebox.showerror("FTP 连接失败", "无法连接到 FTP 服务器。")
        else:
            print("用户选择不安装。")

    thread = threading.Thread(target=install)
    thread.start()

def main_ftp():
    host = '8.218.78.204'
    port = 21
    user = 'fbs'
    password = 'fbs'
    remote_path = '/UpData/FBfans/FBfans.zip'
    local_path = 'FBfans.zip'
    ftp = connect_ftp(host, port, user, password)
    if ftp:
        return ftp, local_path
    return None, None

def version_ver():
    global version
    version = '1.0.0.8'
    print(version)
    remote_version_url = 'http://ver.ry188.vip/API/getver.aspx?N=FBfans'
    response = requests.get(remote_version_url)
    remote_version = response.text.strip()
    print(remote_version)
    if remote_version > version:
        print("有新版本可也。")
        install_new_version_thread(version, remote_version)
    else:
        print("当前已是最新版本。")
        clr.AddReference("mscorlib")
        clr.AddReference("AuthorizeManage")
        # 导入命名空间中的类
        from AuthorizeManage import AuthorizeX

        # 调用GetAuthorize方法
        get_result = AuthorizeX.GetAuthorize("FBCJ")
        print(get_result)
        Get_shouquan(get_result)
        # set_societies()
if __name__ == "__main__":
    # atexit.register(cleanup)
    # 设置当前工作目录为应用程序的真实路径
    application_path = get_real_path()
    os.chdir(application_path)
    print(f"当前工作目录已设置为: {application_path}")
    create_registry_file()#寫入註冊表
    version_ver()#檢測程序版本