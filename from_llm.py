from ollama import embeddings,chat,Message,generate
import base64

stream_out = 1
if stream_out == 0:
    messages = []
    while True:
        ask = input('请输入问题: ')
        messages.append(Message(role='user', content=ask, images=None, tool_calls=None))
        response = chat('deepseek-r1:8b',messages=messages)
        print(response['message']['content'])
elif stream_out == 1:
    messages = []
    while True:
        ask = input('\n请输入问题: ')
        messages.append(Message(role='user', content=ask, images=None, tool_calls=None))
        stream = chat('deepseek-r1:8b', messages=messages, stream=True)
        # 逐块打印响应内容
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)