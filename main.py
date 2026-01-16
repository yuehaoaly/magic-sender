import os
import requests
import google.generativeai as genai

# 1. 获取密钥和输入内容
tg_token = os.environ.get("TG_BOT_TOKEN")
chat_id = os.environ.get("TG_CHAT_ID")
google_key = os.environ.get("GOOGLE_API_KEY")
# 获取用户输入的内容，如果没有则使用默认测试文本
user_input = os.environ.get("USER_INPUT", "测试：今天天气不错")

print("正在处理内容...")

try:
    # 2. 调用 Google Gemini 进行美化
    genai.configure(api_key=google_key)
    # 确认使用 gemini-1.5-flash，这是免费版最稳妥的选择
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    请帮我把下面这段话进行排版美化，使其适合发布在 Telegram 频道中。
    要求：
    1. 加上适当的 Emoji 表情，让气氛活跃。
    2. 分段清晰。
    3. 如果内容包含链接，请保留。
    4. 不要改变原意，只是美化格式。
    
    内容如下：
    {user_input}
    """
    
    response = model.generate_content(prompt)
    beautified_text = response.text
    print("Gemini 美化完成！")

    # 3. 发送到 Telegram
    url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": beautified_text,
    }
    
    tg_resp = requests.post(url, json=payload)
    
    if tg_resp.status_code == 200:
        print("发送成功！")
    else:
        print(f"发送失败: {tg_resp.text}")

except Exception as e:
    print(f"发生错误: {e}")
    # 如果出错，尝试发送原始报错信息给 TG
    requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={
        "chat_id": chat_id,
        "text": f"机器人运行出错: {str(e)}"
    })
