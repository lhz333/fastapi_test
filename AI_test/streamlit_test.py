import json
from datetime import datetime

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

# 生成会话标识
def generate_session_name():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return now

# 保存会话信息
def save_session():
    if st.session_state["current_session"]:
        session_data = {
            "nick_name": st.session_state["nick_name"],
            "nature": st.session_state["nature"],
            "current_session": st.session_state["current_session"],
            "messages": st.session_state["messages"]
        }
    if not os.path.exists("sessions"):
        os.mkdir(f"sessions")

    with open(f"sessions/{st.session_state['current_session']}.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=4)

# 加载单个的会话信息
def load_one_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state["nick_name"] = session_data["nick_name"]
                st.session_state["messages"] = session_data["messages"]
                st.session_state["current_session"] = session_name
                st.session_state["nature"] = session_data["nature"]
    except Exception:
        st.error("加载会话信息失败")


# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for file in file_list:
            if file.endswith(".json"):
                session_list.append(file[:-5])
    session_list.sort(reverse=True)
    return session_list

# 删除指定会话
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json") # 删除文件
            if session_name == st.session_state.current_session:
                st.session_state.current_session = generate_session_name()
                st.session_state.messages = []
    except Exception:
        st.error("删除会话失败")

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state["messages"] = []
# 昵称
if "nick_name" not in st.session_state:
    st.session_state["nick_name"] = "Jenny"
# 性格
if "nature" not in st.session_state:
    st.session_state["nature"] = "幽默毒舌小精灵"
# 会话标识
if "current_session" not in st.session_state:
    st.session_state["current_session"] = generate_session_name()

# 侧边栏. with上下文管理器
with st.sidebar:
    # 控制面板
    st.subheader("控制面板")
    if st.button("新建会话", width="stretch", icon="✏️"):
        # 保存当前会话信息
        save_session()
        # 创建新的会话信息
        if st.session_state["messages"]:
            st.session_state["messages"] = []
            st.session_state["current_session"] = generate_session_name()
            save_session()
            st.rerun() # 重新运行当前页面

    # 会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            # 加载会话信息
            if st.button(session, width="stretch", icon="📄", key=f"load_{session}", type="primary" if session == st.session_state["current_session"] else "secondary"):
                load_one_session(session)
                st.rerun()
        with col2:
            # 删除会话信息
            if st.button("", width="stretch", icon="❌️", key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

    st.divider()
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

    # 大模型返回后 保存会话信息
    save_session()