import requests
import time
import yaml


class AccessTokenClass:
    def __init__(self):
        with open("FS_KEY.yaml", "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        self.app_id = config["APP_ID"]
        self.app_secret = config["APP_SECRET"]
        self.access_token = None
        self.expire_time = 0

    def get_access_token(self):
        if self.access_token is None or time.time() > self.expire_time:
            url = (
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
            )
            headers = {"Content-Type": "application/json; charset=utf-8"}
            data = {"app_id": self.app_id, "app_secret": self.app_secret}
            response = requests.post(url, headers=headers, json=data)
            if response.status_code != 200:
                return None
            result = response.json()
            if result.get("code") != 0:
                return None
            self.access_token = result["tenant_access_token"]
            self.expire_time = time.time() + result["expire"] - 10
        return self.access_token


if __name__ == "__main__":
    token = AccessTokenClass()
    print(token.get_access_token())
