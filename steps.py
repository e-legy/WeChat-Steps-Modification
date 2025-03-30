import os
import requests
import random
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def sc_send(sendkey: str, title: str, desp: str = '') -> dict:
    """Server酱消息推送（安全版）"""
    if not sendkey:
        raise ValueError("Server酱SENDKEY未设置")
    
    # 自动识别新旧版Server酱key
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

def load_accounts() -> list:
    """加载账户配置"""
    accounts = os.getenv('ACCOUNTS_AND_PASSWORDS')
    if not accounts:
        raise ValueError("未设置ACCOUNTS_AND_PASSWORDS环境变量")
    
    try:
        return [pair.split(',') for pair in accounts.split(';') if pair]
    except Exception as e:
        raise ValueError(f"账户格式错误: {str(e)}")

def modify_steps(account: str, password: str, sendkey: str) -> str:
    """修改步数并发送通知"""
    min_steps = int(os.getenv('MIN_STEPS', 50000))
    max_steps = int(os.getenv('MAX_STEPS', 80000))
    attempts = int(os.getenv('MAX_ATTEMPTS', 3))
    
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
            data = resp.json()

            if data.get('status') == 'success':
                msg = f"✅ 账号 {masked_account} 修改成功\n步数: {steps}"
                sc_send(sendkey, "步数修改成功", msg)
                return msg
            
            last_error = data.get('message', '未知错误')
        except Exception as e:
            last_error = str(e)
        
        print(f"尝试 {attempt}/{attempts} 失败: {last_error}")

    # 全部尝试失败后发送告警
    error_msg = f"❌ 账号 {masked_account} 修改失败\n错误: {last_error}"
    sc_send(sendkey, "步数修改失败", error_msg)
    return error_msg

def main():
    try:
        sendkey = os.getenv('SENDKEY')
        if not sendkey:
            raise ValueError("未配置Server酱SENDKEY")
        
        accounts = load_accounts()
        print(f"🔍 加载到 {len(accounts)} 个账户")

        for acc, pwd in accounts:
            result = modify_steps(acc, pwd, sendkey)
            print(result)
            
    except Exception as e:
        sc_send(os.getenv('SENDKEY'), "步数修改脚本崩溃", f"错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()
