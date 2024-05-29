import csv
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# 初始化 Chrome WebDriver
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)  # 假设 Chrome WebDriver 在系统路径中

# 打开ll_deal.csv文件并处理每一行
with open("ll_deal.csv", "r", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    # 创建输出 CSV 文件
    with open("output.csv", "w", newline="", encoding="utf-8") as output_csvfile:
        fieldnames = ["Input", "Output"]
        writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # 遍历 ll_deal.csv 文件中的每一行
        for row in reader:
            question = row["text"]
            # 发送 POST 请求模拟用户输入
            url = "https://d8b9b9d7c6eb9d8dd9.gradio.live/"
            data = {"textbox": question}
            response = requests.post(url, data=data)

            # 加载页面
            driver.get(url)
            # 等待页面加载完成
            wait = WebDriverWait(driver, 10)  # 最长等待时间设置为10秒
            input_box = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'textarea[placeholder="请输入询问内容并按Enter键发送"]')))
            time.sleep(2)  # 为了稳妥，再等待2秒

            # 输入用户文本并模拟按下 Enter 键
            input_box.clear()
            input_box.send_keys(question)
            input_box.send_keys(Keys.ENTER)

            # 等待输出结果加载
            output_box = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[placeholder="来自模型的回复"]')))
            time.sleep(5)  # 增加等待时间以确保结果加载完全

            # 获取输出结果
            output_text = output_box.get_attribute("value").strip()

            # 将结果保存到输出 CSV 文件
            writer.writerow({"Input": question, "Output": output_text})

            # 等待一段时间以避免过快请求
            time.sleep(2)

# 关闭 WebDriver
driver.quit()

print("结果已保存到 output.csv 文件中。")
