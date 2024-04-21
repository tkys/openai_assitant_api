import base64
import io
import os

from openai import OpenAI
import requests
import streamlit as st

import json
import time

# 認証情報の読み込み
secrets = st.secrets["openai"]
os.environ["OPENAI_API_KEY"] = secrets['OPENAI_API_KEY']
MATH_ASSISTANT_ID = secrets['MATH_ASSISTANT_ID']  # 予め作ったお嬢様口調assistant

client = OpenAI()

def show_json(obj):
    display(json.loads(obj.model_dump_json()))

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

# thread作成と初回user側メッセージ送信
def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(MATH_ASSISTANT_ID, thread, user_input)
    return thread, run

# 既存作成済みthreadに追加のuserメッセージ送信
def run_for_created_thread(thread, user_input):
    run = submit_message(MATH_ASSISTANT_ID, thread, user_input)
    return run

# 表示用
def pretty_print(messages):
    #print("# Messages")
    #for m in messages:
    #    print(f"{m.role}: {m.content[0].text.value}")
    #print()
    st.write("# 質問と回答")
    for m in messages:
        if m.role == "user":
            st.write(f"【質問】： {m.content[0].text.value}")
        if m.role == "assistant":
            st.write(f"【AIからの回答】： {m.content[0].text.value}")
    


# 回答生成中なら待つ
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

# ページ表示設定
st.set_page_config(
    page_title="AssistantAPI TEST", 
    layout="wide", 
    initial_sidebar_state="auto"
)

hide_footer_style = """
    <style>
    footer {
        visibility: hidden;
    }
    </style>
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)

# ボタン保持Session
if "button1" not in st.session_state:
    st.session_state["button1"] = False

# ページ表示
st.title("OpenAI AssistantsAPI test")

ask = st.text_input("AIに聞いてみよう",placeholder="質問をこちらにどうぞ")

if st.button("質問"):
    if ask != "":
        st.session_state["button1"] = not st.session_state["button1"]
        progress_text = st.empty()
        progress_text.write("回答待ち")
        progress_text.image('./img/loading.gif')
        thread1, run1 = create_thread_and_run(ask)
        
        ## 回答の表示
        # Wait for Run 1
        run1 = wait_on_run(run1, thread1)
        progress_text.empty()
        pretty_print(get_response(thread1))
        st.session_state["thread1"] = thread1
        
        
if st.session_state["button1"]:
    ask_second = st.text_input("追加でAIに聞いてみよう",placeholder="質問をこちらにどうぞ")
    if st.button("さらに質問"):
        if ask_second != "":
            thread1 = st.session_state["thread1"]
            progress_text_2 = st.empty()
            progress_text_2.write("回答待ち")
            progress_text_2.image('./img/loading.gif')
            run2 = run_for_created_thread(thread1, ask_second)
            
            ## 回答の表示
            # Wait for Run 1
            run2 = wait_on_run(run2, thread1)
            progress_text_2.empty()
            pretty_print(get_response(thread1))