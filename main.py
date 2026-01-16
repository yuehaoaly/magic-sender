import os
import requests
import google.generativeai as genai

# 1. 配置基础信息
tg_token = os.environ.get("TG_BOT_TOKEN")
chat_id = os.environ.get("TG_CHAT_ID")
google_key = os.environ.get("GOOGLE_API_KEY")
user_input = os.environ.get("USER_INPUT", "测试：今天天气不错")

print("正在初始化...")

try:
    genai.configure(api_key=google_key)
    
    # --- 核心修改：自动寻找可用模型 ---
    print("正在查询可用模型列表...")
    available_model = None
    
    # 遍历所有模型
    for m in genai.list_models():
        # 寻找支持 'generateContent' 方法的模型
        if 'generateContent' in m.supported_generation_methods:
            # 优先找名字里带 gemini 的
            if 'gemini' in m.name:
                available_model = m.name
                print(f"找到可用模型: {available_model}")
                break
    
    # 如果没找到 gemini，就用找到的第一个支持生成的模型兜底
    if not available_model:
        for m in genai.list_models():
             if 'generateContent' in m.supported_generation_methods:
                available_model = m.name
                print(f"未找到Gemini系列，降级使用: {available_model}")
                break

    if not available_model:
        raise Exception("未找到任何可用的文本生成模型！")
    # --------------------------------

    # 使用找到的模型
    model = genai.GenerativeModel(available_model)
    
    prompt = f"""
    请帮我把下面这段话进行排版美化，使其适合发布在 Telegram 频道中。
    要求：
    1. 加上适当的 Emoji 表情。
    2. 分段清晰。
    3. 保留链接。
    
    内容如下：
    {user_input}
    """
    
    response = model.generate_content(prompt)
    beautified_text = response.text
    print("Gemini 美化完成！")

    # 发送到 Telegram
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
    # 报错通知
    requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={
        "chat_id": chat_id,
        "text": f"机器人运行出错: {str(e)}"
    })
