## 这是一个基于SCAMPER创新方法的为我们提供创新思维的工具。

![微信截图_20250607130306](https://github.com/user-attachments/assets/b23f459d-8f0c-4860-b383-15a93455641f)

### 以下全是无用之物

conbin_ele 合并元素 即合并element_llm与element_url为element_all 。  
element_url 本意是通过网络爬取一些创新元素，效果不理想。  
element_llm 这里想实现一个从大语言模型通过提问获取的词汇保存在此。  
from_llm 这只是个提问deepseek的模板。  
from_url 这是一个从网络爬取的模板。  
test 无用。  

### 主要程序  

ui 所有代码在此  
element_all 本地获取的灵感元素存储位置，可自由添加

### 使用

1.首先安装 ollama    
2.ollama run deepseek-r1:8b 安装deepseek 8b 可自由更改自己喜欢的模型  
3.安装所需的功能包即可  
4.运行ui.py  如果更改了模型 需要对应更改 ui.py->askllm函数中模型名称
