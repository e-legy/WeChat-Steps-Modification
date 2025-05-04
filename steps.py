import os
import requests
import random
import time
import re

def sc_send(sendkey: str, title: str, desp: str = '') -> dict:
    """Server酱消息推送"""
    if not sendkey:
        raise ValueError("Server酱SENDKEY未设置")
    
    if sendkey.startswith('sctp'):
        if not (match := re.fullmatch(r'sctp(\d+)t\w+', sendkey)):
            raise ValueError("无效的SCTP密钥格式")
        url = f'https://{match.group(1)}.push.ft07.com/send/{sendkey}.send'
    else:
        url = f'https://sctapi.ftqq.com/{sendkey}.send'

    try:
        resp = requests.post(
            url,
            json={'title': title, 'desp': desp},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"⚠️ 消息推送失败: {str(e)}")
        return {'error': str(e)}

def load_accounts(accounts_str: str) -> list:
    """从字符串解析账户信息"""
    if not accounts_str:
        raise ValueError("账户信息为空")
    
    try:
        return [pair.split(',') for pair in accounts_str.split(';') if pair]
    except Exception as e:
        raise ValueError(f"账户格式错误: {str(e)}")

def modify_steps(account: str, password: str, sendkey: str) -> str:
    """修改步数并发送通知"""
    min_steps = 10000  # 可改为从环境变量获取
    max_steps = 22000
    attempts = 3
    
    masked_account = f"{account[:3]}***{account[-3:]}"
    last_error = None

    for attempt in range(1, attempts+1):
        steps = random.randint(min_steps, max_steps)
        try:
            time.sleep(random.uniform(1, 3))
            resp = requests.get(
                f"https://steps.api.030101.xyz/api?account={account}&password={password}&steps={steps}",
                timeout=20
            )
            # 检查状态码
            if resp.status_code != 200:
                raise ValueError(f"API 请求失败，状态码: {resp.status_code}, 响应: {resp.text}")

            # 尝试解析 JSON
            try:
                data = resp.json()
            except Exception as e:
                raise ValueError(f"JSON 解析失败: {str(e)}, 响应: {resp.text}")

            if data.get('status') == 'success':
                msg = f"✅ 账号 {masked_account} 修改成功\n步数: {steps}"
                sc_send(sendkey, "步数修改成功", msg)
                return msg
            
            last_error = data.get('message', '未知错误')
        except Exception as e:
            last_error = str(e)
        
        print(f"尝试 {attempt}/{attempts} 失败: {last_error}")

    error_msg = f"❌ 账号 {masked_account} 修改失败\n错误: {last_error}"
    sc_send(sendkey, "步数修改失败", error_msg)
    return error_msg

def main():
    try:
        # 从GitHub Actions Secrets获取敏感信息
        sendkey = os.environ['SERVERCHAN_KEY']
        accounts_str = os.environ['ACCOUNT_INFO']
        
        accounts = load_accounts(accounts_str)
        print(f"🔍 加载到 {len(accounts)} 个账户")

        for acc, pwd in accounts:
            result = modify_steps(acc, pwd, sendkey)
            print(result)
            
    except Exception as e:
        if 'SERVERCHAN_KEY' in os.environ:
            sc_send(os.environ['SERVERCHAN_KEY'], "步数修改脚本崩溃", f"错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()
