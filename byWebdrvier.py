import os
import time
import json

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

task_page_url = "https://www.south-plus.net/plugin.php?H_name-tasks.html.html"
get_reward_url = "https://www.south-plus.net/plugin.php?H_name-tasks-actions-newtasks.html.html"

XPATH_WEEK = "//a[@onclick=\"startjob('14');\"]"
XPATH_DAY = "//a[@onclick=\"startjob('15');\"]"

serverKey = os.environ.get('serverKey')
cookie_json = os.environ.get('COOKIE')

if cookie_json:
    try:
        cookies = json.loads(cookie_json)
    except json.JSONDecodeError:
        raise Exception("无法解析 COOKIE 环境变量为 JSON。")
else:
    raise Exception("未找到 COOKIE 环境变量，请设置后重试。")

complete = []
driver = None
try:
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 如果你在无头模式下运行
    chrome_options.add_argument("--no-sandbox")  # 解决一些权限问题
    chrome_options.add_argument("--disable-dev-shm-usage")  # 解决共享内存问题
    service = Service(rf'/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.south-plus.net/index.php")
    for cookie in cookies:
        if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
            cookie['sameSite'] = 'Lax'  # 或者 'None'，根据需要尝试
        driver.add_cookie(cookie)
    print("Cookies 加载完毕。")
    driver.refresh()
    time.sleep(2)

    # 领取任务
    print(f"正在打开任务页面: {task_page_url}")
    driver.get(task_page_url)
    print("等待日常申请任务按钮出现")
    wait = WebDriverWait(driver, 5)
    try:
        button = wait.until(
            EC.element_to_be_clickable((By.XPATH, XPATH_DAY))
        )
        button.click()
        print("日常任务申请成功。")
        complete.append('日常任务申请')
    except Exception as e:
        print(f"日常任务申请失败/已领取/已完成: {e}")
    time.sleep(2)

    print("等待页面刷新")
    driver.refresh()

    print("等待周常申请任务按钮出现")
    wait = WebDriverWait(driver, 5)
    try:
        button = wait.until(
            EC.element_to_be_clickable((By.XPATH, XPATH_WEEK))
        )
        button.click()
        print("周常任务申请成功。")
        complete.append('周常任务申请')
    except Exception as e:
        print(f"周常任务申请失败/已领取/已完成: {e}")
    time.sleep(2)

    # 领取奖励
    print(f"正在打开领取奖励页面: {get_reward_url}")
    driver.get(get_reward_url)
    print("等待日常领取奖励按钮出现")
    wait = WebDriverWait(driver, 5)
    try:
        button = wait.until(
            EC.element_to_be_clickable((By.XPATH, XPATH_DAY))
        )
        button.click()
        print("日常任务领取奖励成功。")
        complete.append('日常任务领奖')
    except Exception as e:
        print(f"日常任务领取奖励失败/已领取: {e}")
    time.sleep(2)

    print("等待页面刷新")
    driver.refresh()

    print("等待周常领取奖励按钮出现")
    wait = WebDriverWait(driver, 5)
    try:
        button = wait.until(
            EC.element_to_be_clickable((By.XPATH, XPATH_WEEK))
        )
        button.click()
        print("周常任务领取奖励成功。")
        complete.append('周常任务领奖')
    except Exception as e:
        print(f"周常任务领取奖励失败/已领取: {e}")
    time.sleep(2)

    print("5秒后自动关闭浏览器...")
    time.sleep(5)

except FileNotFoundError:
    print("错误：未找到 cookies.json 文件。")
    print("请先运行 get_cookies.py 来生成它。")
except Exception as e:
    print(f"自动化签到时发生错误: {e}")
    print("如果提示'找不到元素'，请检查你的 XPATH 是否正确 (步骤4)。")
    print("如果一直卡住，可能是Cookie失效了，请重新运行 get_cookies.py。")

finally:
    if driver:
        driver.quit()

    message = '\n'.join(complete) if complete else '无任务完成'
    if serverKey:
        url = f"https://sctapi.ftqq.com/{serverKey}.send?title={message}&desp=messagecontent"
        payload = {}
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
    else:
        print("未设置 serverKey，跳过通知发送。")
