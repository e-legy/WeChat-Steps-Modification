import os
import requests
import random
import re

# 获取环境变量
serverchan_sendkey = os.environ.get('SERVERCHAN_SENDKEY')  # 可以为空
telegram_api_token = os.environ.get('TELEGRAM_API_TOKEN')  # 可以为空
telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')      # 可以为空
accounts_and_passwords = os.environ.get('ACCOUNTS_AND_PASSWORDS')

# 检查必需的环境变量
if not accounts_and_passwords:  # 只检查 accounts_and_passwords
    print("账户信息未设置，无法继续操作。")
    exit(1)

# 解析账户和密码
account_password_pairs = [pair.split(',') for pair in accounts_and_passwords.split(';')]

# 发送 Telegram 消息
def send_telegram_message(message):
    if not telegram_api_token or not telegram_chat_id:  # 如果缺少 Telegram 配置，跳过
        print("Telegram 配置未设置，跳过消息发送。")
        return
    url = f"https://api.telegram.org/bot{telegram_api_token}/sendMessage"
    data = {'chat_id': telegram_chat_id, 'text': message, 'parse_mode': 'HTML'}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Telegram 消息发送失败：{e}")

# 发送 ServerChan 推送
def sc_send(sendkey, title, desp='', options=None):
    if not sendkey:  # 如果缺少 ServerChan 配置，跳过
        print("ServerChan 配置未设置，跳过消息发送。")
        return None
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
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ServerChan 推送失败：{e}")
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
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"请求失败：{e}")
        if _ == attempts - 1:
            if telegram_api_token and telegram_chat_id:  # 如果 Telegram 配置存在，发送通知
                send_telegram_message(f"<b>Steps_modifier</b>\n\n账号：{account}\n连续失败 {attempts} 次")
            if serverchan_sendkey:  # 如果 ServerChan 配置存在，发送通知
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
