from flask import request
import json, time
from linebot import LineBotApi, WebhookHandler
from linebot.models import FlexSendMessage, TextSendMessage
from web_app import app
from web_app.models import User, Document

line_bot_api = LineBotApi(app.config['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(app.config['CHANNEL_SECRET'])


def contruct_svb():
    svbs = Document.query.filter_by(tag='svb').all()
    if svbs is None:
        return (False, dict())
    else:
        res = []
        for svb in svbs:
            if ('TSE-SVB' not in svb.title) or len(svb.title.split()) < 2:
                continue

            issue_num = {
                "gravity": "center",
                "text": svb.title.split()[0],
                "weight": "bold",
                "margin": "md",
                "type": "text",
                "contents": [],
                "action": {
                    "uri": svb.link,
                    "type": "uri"
                }
            }

            title = {
                "wrap": True,
                "type": "text",
                "contents": [],
                "weight": "regular",
                "text": " ".join(svb.title.split()[1:]),
                "action": {
                "uri": svb.link,
                "type": "uri"
            }
            }

            date = {
                "text": svb.uploadDate.strftime('%d/%m/%Y'),
                "contents": [],
                "color": "#000000FF",
                "type": "text"
            }

            seperator = {
                "type": "separator",
                "color": "#939393FF",
                "margin": "lg"
            }

            res.extend([issue_num, title, date, seperator])

    if len(res) == 0:
        return (False, dict())
    else:
        contents = {
                "header": {
                "spacing": "none",
                "contents": [
                    {
                    "contents": [],
                    "size": "lg",
                    "text": "ข่าวสารบริการฉบับล่าสุด",
                    "align": "center",
                    "weight": "bold",
                    "type": "text",
                    "color": "#000000FF"
                    }
                ],
                "layout": "vertical",
                "type": "box"
                },
                "footer": {
                "contents": [
                    {
                    "wrap": True,
                    "contents": [],
                    "type": "text",
                    "align": "center",
                    "text": "ท่านสามารถติดตามข่าวสารฉบับอื่นๆได้ค่ะ"
                    }
                ],
                "layout": "horizontal",
                "type": "box"
                },
                "direction": "ltr",
                "type": "bubble",
                "body": {
                "contents": res,
                "backgroundColor": "#FFFFFFFF",
                "spacing": "xs",
                "layout": "vertical",
                "type": "box"
                }
            }
        return (True, contents)




def chat_handler():
    body = request.get_json()
    temp = json.dumps(body, indent=2)
    print(temp)
    events = body['events'][0]

    userId = body['events'][0]['source']['userId']
    user = User.query.filter_by(userId=userId).first()
    if user and user.status == 'member':
        reply_token = events['replyToken']
        
        if events['type'] == 'message':
            if events['message']['type'] == 'text':
                text = events['message']['text'].lower()
                print('Txt msg:', text)

                # if text == "use richmenu":
                #     print('Link richmenu to user')
                #     res = line_bot_api.link_rich_menu_to_user(userId, 'richmenu-c49d7b2cfa7740deb71b7e1ac68ddfeb')
                #     print(res)
                #     return

                # if text == "clear richmenu":
                #     print('Clear richmenu from user')
                #     res = line_bot_api.unlink_rich_menu_from_user(userId)
                #     print(type(res))
                #     return

                if text in ["สวัสดี", 'Hello', 'Hi', 'หวัดดี', 'สวัสดีครับ', 'สวัสดีคับ', 'สวัสดีค่ะ']:
                    text_msg = TextSendMessage(text='สวัสค่ะคุณ ' + user.name)
                    line_bot_api.reply_message(reply_token, text_msg)
                    return

                if text in ["ข่าวสารบริการล่าสุด", 'ข่าวสารบริการ', 'svb', 'service bulletin', 'ข่าวสาร']:
                    content = contruct_svb()
                    if content[0]:
                        flex_message = FlexSendMessage(
                            alt_text='ข่าวสารบริการฉบับล่าสุด',
                            contents=content[1]
                        )           
                        line_bot_api.reply_message(reply_token, flex_message)


def set_rich_menu(userId, richMenuId):
    line_bot_api.link_rich_menu_to_user(userId, richMenuId)
    nowId = line_bot_api.get_rich_menu_id_of_user(userId)
    print('Now richmenu ID: ' + nowId)

def unlink_rich_menu(userId):
    line_bot_api.unlink_rich_menu_from_user(userId)

def push_text_msg(userId, txt_msg):
    line_bot_api.push_message(userId, TextSendMessage(text=txt_msg))
