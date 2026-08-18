import streamlit as st
import os
from openai import OpenAI

st.set_page_config(
    page_title="AI Test",
    # 布局
    layout="wide",
    # 控制的是侧边栏的状态
    initial_sidebar_state="expanded",
    menu_items={}
)

st.title("AI Test")

# 创建与AI大模型交互的客户端对象
client = OpenAI(api_key="sk-1ea64bffc7a5450bbed6e72765d297bf", base_url="https://api.deepseek.com")

system_promat = "你叫 %s，你是一名资深的全栈开发工程师，你的性格是 %s"

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "nick_name" not in st.session_state:
    st.session_state["nick_name"] = "Jenny"

if "nature" not in st.session_state:
    st.session_state["nature"] = "幽默毒舌小精灵"

# 侧边栏
with st.sidebar:
    st.subheader("AI信息")
    # 昵称输入框
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state["nick_name"])
    if nick_name:
        st.session_state["nick_name"] = nick_name

    # 性格输入框
    nature = st.text_area("性格", placeholder="请输入性格,",value=st.session_state["nature"])
    if nature:
        st.session_state["nature"] = nature

# 展示聊天信息
for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])
    # if message["role"] == "user":
    #     st.chat_message("user").write(message["content"])
    # else:
    #     st.chat_message["assistant"].write(message["content"])


promat = st.chat_input("请输入您要问的问题")

if promat:
    st.chat_message("user").write(promat)
    print("-----调用AI大模型", promat)

    # 保存用户输入的提示词
    st.session_state["messages"].append({"role": "user", "content": promat})

    # 调用AI大模型
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_promat % (st.session_state["nick_name"], st.session_state["nature"])},
            # {"role": "user", "content": promat},
            *st.session_state["messages"]
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    # 非流式输出
    # content = response.choices[0].message.content
    # print('大模型返回的结果：---->', content)
    # st.chat_message("assistant").write(content)
    # # 保存大模型返回的信息
    # st.session_state["messages"].append({"role": "assistant", "content": content})


    # 流式输出结果时
    response_message = st.empty()

    full_content = ""

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_content += content
            response_message.chat_message("assistant").write(full_content)

    # 保存大模型返回的信息
    st.session_state["messages"].append({"role": "assistant", "content": full_content})