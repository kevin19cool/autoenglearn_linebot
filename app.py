#!/usr/bin/env python
# coding: utf-8

# In[3]:


from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
from bs4 import BeautifulSoup
import random
import bbc

app = Flask(__name__)
# 設定 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = "y7d25f985bEjEGsukSVAjI4ENEKVtvm+omHcKnub8PPwlPrlktdk9LMYWkel0cYzWUsfzlGIFMTbC+MuR9OEI78KTYrd9CiPjUvR4+IptURzX9Z9Bjr5BMCYPmpnXvBtkkNUCdJnfDhBRU3mCu+d4QdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "14200733689e76984c5cf98449663211"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def split_content(content, max_length=500):
    # 將文章內容分割成不超過指定字數的段落
    return [content[i:i+max_length] for i in range(0, len(content), max_length)]
    
def fetch_full_article_content(article_url):
    # 抓取文章頁面
    response = requests.get(article_url)
    response.raise_for_status()

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # 提取文章內容段落
    paragraphs = soup.find_all("p")
    content = "\n".join(paragraph.get_text() for paragraph in paragraphs)
    return content

# 接收 LINE Webhook
@app.route("/callback", methods=["POST"])
def callback():
    # 驗證 LINE 的簽名
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"



# 處理訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    if user_message.lower() in ["news", "新聞", "article"]:
        # 抓取 BBC 文章
        news_list = bbc.news.get_latest_news(bbc.Languages.English)
        random_article = random.choice(news_list)
        destination_link = random_article["news_link"]
        full_content_2 = fetch_full_article_content(destination_link)
        
        if not full_content_2:
            reply_message = "未找到文章！"
        else:
            reply_name ="文章名稱:"+random_article["title"]
            reply_link ="文章連結:"+random_article["news_link"]
            reply_content ="文章內容:"
            # 分割內容
            split_contents = split_content(full_content_2)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_name)
                TextSendMessage(text=reply_link)
                        )
             for part in split_contents:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=part),
                        )
    else:
        reply_message = "請輸入 'news' 或 '新聞' 來隨機獲取一篇文章。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message),
        )
    # 回應用戶訊息
    

    
if __name__ == "__main__":
    app.run(port=5000)


# In[ ]:




