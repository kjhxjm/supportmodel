import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


client = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url=os.environ.get("GLM_BASE_URL"),
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=os.environ.get("GLM_API_KEY"),
)



response = client.chat.completions.create(
    # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
    model="glm-4-flash",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "你好"},
            ],
        }
    ],
)


print(response.choices[0])
# Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='好的，我已经准备好回答您的问题或者提供帮助。请告诉我您需要什么帮助。', refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=None))