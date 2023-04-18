import requests, json
from flask import session


class UserIDToken():
    
    def __init__(self, userIDtoken, channel_ID):
        self.userIDtoken = userIDtoken
        self.channel_ID = channel_ID
        self.is_valid = False
        self.err_msg = ""
        self.detail = dict()

    def verify(self):
        if not UserIDToken:
            self.err_msg = "Token not found"
        else:
            line_url = "https://api.line.me/oauth2/v2.1/verify"
            data = {
                "id_token": self.userIDtoken,
                "client_id": self.channel_ID
            }
            res = requests.post(line_url, data)
            if res.status_code != 200:
                self.err_msg = "Token expired or invalid"
            else:
                self.detail = json.loads(res.content)
                self.is_valid = True