from fs_id import AccessTokenClass, get_chat_id, get_users_id_from_chat

CHAT_NAME = "战队大群"

if __name__ == '__main__':
    # get access_token
    access_token_obj = AccessTokenClass()
    access_token = access_token_obj.get_access_token()
    if not access_token:
        print('get access_token failed')
        exit()

    # get chat_id
    chat_id = get_chat_id(access_token, CHAT_NAME)
    if not chat_id:
        print('get chat_id failed')
        exit()

    # get users_id_from_chat
    users_id_list = list(get_users_id_from_chat(access_token, chat_id))
    if len(users_id_list) == 0:
        print('get users_id_from_chat failed')
        exit()