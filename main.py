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
    
    # 針對臺南市政府網站的主要內容區塊抓取
    main_content = soup.find('main') or soup.find(id='content') or soup.body
    
    # 取得純文字行（過濾掉空白行）
    lines = [line.strip() for line in main_content.get_text().splitlines() if line.strip()]
    return lines

def compare_and_highlight():
    current_lines = fetch_page_content()
    today_str = datetime.now().strftime('%Y-%m-%d')
    
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
    
    # 取得檔案最後修改日期作為「昨日內容」的代表日期（若無則帶今日）
    mtime = os.path.getmtime(DATA_FILE)
    prev_date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

    # 使用 HtmlDiff 產生對照頁面
    differ = difflib.HtmlDiff(tabsize=4, wrapcolumn=80)
    html_diff = differ.make_file(
        previous_lines, 
        current_lines, 
        fromdesc=f"昨日內容 ({prev_date_str})", 
        todesc=f"今日最新內容 ({today_str})",
        context=False,
        numlines=0
    )
    
    # 自訂 CSS 樣式：實現整列高亮與不同增刪顏色區隔
    custom_css = """
    <style>
        table.diff { font-family: Consolas, Monaco, monospace; border-collapse: collapse; width: 100%; font-size: 14px; }
        .diff_header { background-color: #f1f1f1; text-align: right; width: 4em; color: #aaa; padding: 2px 5px; }
        .diff_next { background-color: #c0c0c0; }
        
        /* 刪除列整列高亮 (淺紅底) */
        .diff_sub { background-color: #ffe6e6 !important; }
        /* 新增列整列高亮 (淺綠底) */
        .diff_add { background-color: #e6ffed !important; }
        
        /* 區塊內細部文字顏色變更 */
        td.diff_chg { background-color: #fffbdd; }
        span.diff_sub { background-color: #ffc0c0; color: #900; text-decoration: line-through; }
        span.diff_add { background-color: #acf2bd; color: #006000; font-weight: bold; }
        
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #fafafa; }
        h2 { color: #333; }
    </style>
    """
    
    # 將自訂 CSS 注入到產生的 HTML 中
    html_diff = html_diff.replace("</head>", f"{custom_css}</head>")
    
    with open(DIFF_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_diff)
        
    # 更新舊檔案為最新版本
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(current_lines))
        
    print(f"異動比對結果已輸出至：{DIFF_OUTPUT}")

if __name__ == "__main__":
    compare_and_highlight()