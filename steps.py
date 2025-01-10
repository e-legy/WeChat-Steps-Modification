import os
import requests
import random
import re

# 获取环境变量
serverchan_sendkey = os.environ.get('SERVERCHAN_SENDKEY')
telegram_api_token = os.environ.get('TELEGRAM_API_TOKEN')  # Added: 获取 Telegram API Token
telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')      # Added: 获取 Telegram 聊天 ID
accounts_and_passwords = os.environ.get('ACCOUNTS_AND_PASSWORDS')

# 检查必需的环境变量
if not all([serverchan_sendkey, telegram_api_token, telegram_chat_id, accounts_and_passwords]):  # Added: 检查所有必需的环境变量
    print("缺少必要的环境变量，无法继续操作。")  # Added: 更详细的错误提示
    exit(1)

# 解析账户和密码
account_password_pairs = [pair.split(',') for pair in accounts_and_passwords.split(';')]

# 发送 Telegram 消息
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{telegram_api_token}/sendMessage"
    data = {'chat_id': telegram_chat_id, 'text': message, 'parse_mode': 'HTML'}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Added: 检查请求是否成功
    except requests.exceptions.RequestException as e:
        print(f"Telegram 消息发送失败：{e}")  # Added: 异常处理

# 发送 ServerChan 推送
def sc_send(sendkey, title, desp='', options=None):
    if options is None:
        options = {}
    if sendkey.startswith('sctp'):
        match = re.match(r'sctp(\d+)t', sendkey)
        if match:
            num = match.group(1)
            url = f'https://{num}.push.ft07.com/send/{sendkey}.send'
        else:
            raise ValueError('Invalid sendkey format for sctp')
    else:
        url = f'https://sctapi.ftqq.com/{sendkey}.send'
    params = {
        'title': title,
        'desp': desp,
        **options
    }
    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }
    try:
        response = requests.post(url, json=params, headers=headers)
        response.raise_for_status()  # Added: 检查请求是否成功
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ServerChan 推送失败：{e}")  # Added: 异常处理
        return None

# 修改微信步数
def modify_steps(account, password, min_steps, max_steps, attempts=3, timeout=20):
    for _ in range(attempts):
        steps = random.randint(min_steps, max_steps)
        url = f"https://steps.api.030101.xyz/api?account={account}&password={password}&steps={steps}"
        try:
            response = requests.get(url, timeout=timeout)
            result = response.json()
            if result.get('status') == 'success':
                return f"账号 {account[:3]}***{account[-3:]} 修改成功，步数：{steps}"
        except (requests.exceptions.RequestException, ValueError) as e:  # Added: 捕获 JSON 解析异常
            print(f"请求失败：{e}")
        if _ == attempts - 1:
            send_telegram_message(f"<b>Steps_modifier</b>\n\n账号：{account}\n连续失败 {attempts} 次")
            ret = sc_send(serverchan_sendkey, 'WeChat-Steps-Modification', f"账号：{account}\n连续失败 {attempts} 次")
            print(ret)
    return f"账号 {account[:3]}***{account[-3:]} 修改失败"

# 主程序
def main():
    min_steps = 12000
    max_steps = 16000
    for account, password in account_password_pairs:
        result = modify_steps(account, password, min_steps, max_steps)
        print(result)

if __name__ == "__main__":
    main()
