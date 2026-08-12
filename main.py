import os
import requests
from bs4 import BeautifulSoup
import difflib
from datetime import datetime

# 目標網址：臺南市政府首長行程/訊息
URL = "https://www.tainan.gov.tw/News_Leader.aspx?n=14212&sms=16577"
DATA_FILE = "latest_content.txt"
DIFF_OUTPUT = "diff.html"

def fetch_page_content():
    """抓取網頁主要內容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(URL, headers=headers)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 針對臺南市政府網站的主要內容區塊抓取（通常在 .news_box、table 或 .main 區域）
    # 這裡抓取整頁主要文字，並去除多餘空白與動態 Session 資訊
    main_content = soup.find('main') or soup.find(id='content') or soup.body
    
    # 取得純文字行（過濾掉空白行）
    lines = [line.strip() for line in main_content.get_text().splitlines() if line.strip()]
    return lines

def compare_and_highlight():
    current_lines = fetch_page_content()
    
    # 檢查是否有上次儲存的版本
    if not os.path.exists(DATA_FILE):
        print("首次執行，已建立基底檔案。")
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(current_lines))
        return
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        previous_lines = f.read().splitlines()
        
    # 比對新舊資料
    if previous_lines == current_lines:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 網頁內容無異動。")
        return
        
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 偵測到網頁異動！正在產生高亮報告...")
    
    # 使用 HtmlDiff 產生高亮對照頁面
    differ = difflib.HtmlDiff()
    html_diff = differ.make_file(
        previous_lines, 
        current_lines, 
        fromdesc="昨日內容", 
        todesc="今日最新內容"
    )
    
    with open(DIFF_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_diff)
        
    # 更新舊檔案為最新版本
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(current_lines))
        
    print(f"異動比對結果已輸出至：{DIFF_OUTPUT}")

if __name__ == "__main__":
    compare_and_highlight()