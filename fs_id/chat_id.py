import requests


def get_chat_id(token, chat_name):
    url = "https://open.feishu.cn/open-apis/im/v1/chats"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": 100}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return None
    result = response.json()
    if result["code"] != 0:
        return None
    for chat in result["data"]["items"]:
        if chat["name"] == chat_name:
            return chat["chat_id"]
    return None


if __name__ == "__main__":
    from access_token import AccessTokenClass

    token = AccessTokenClass().get_access_token()
    if token is None:
        print("get access token failed")
        exit(1)
    chat_id = get_chat_id(token, "战队大群")
    if chat_id:
        print(f"chat_id: {chat_id}")
    else:
        print("chat not found")
