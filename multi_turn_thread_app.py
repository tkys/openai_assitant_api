from openai import OpenAI
import time

from rich.prompt import Prompt
from rich import print

import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

OPENAI_API_key = os.environ.get("api_key")



class AssistantsAPI:
    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_key # api_key from .env
        )
        
        self.assistant_id = "asst_qKqXRBBM6R6ijMkAYvMiHXpn"
        
        self.thread_id = None  # スレッドIDを保持する変数

 
    def create_or_get_thread(self):
        if self.thread_id is None:
            thread = self.client.beta.threads.create()
            self.thread_id = thread.id
        return self.thread_id


    def create_assitant(self):
        assistant = self.client.beta.assistants.create(
            name="Math Tutor",
            instructions="",#あなたは数学の家庭教師です。コードを書いて実行し、数学の質問に答えてください。",
            tools=[{"type": "code_interpreter"}],
            model="gpt-3.5-turbo-1106"
        )
        return assistant
    
    
    def set_assistant(self):
        if self.assistant_id is None: #アシスタントがいないなら、新規に作成する
            assistant = self.create_assitant()
            self.assistant_id = assistant.id
        return self.assistant_id
        


    def submit_message_and_get_response(self, user_input):
        thread_id = self.create_or_get_thread()
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        # ここでAssistantからの応答を取得する
        assistant_id = self.set_assistant()
        
        assistant_id = assistant_id  # Assistant IDを設定
        
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions="あなたは看護学校の先生ボットです。data_with_id.jsonに書いてある医療単語説明だけを使って質問に回答してください."
        )

        # Runのステータスが「completed」になるまで待機
        while not run.status == "completed":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            time.sleep(1)  # 1秒待機

        # 応答を表示
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id
        )
        
 
        #print(messages.data)
        
        role_content =[]
        
        for message in messages.data:
            role = message.role
            content = message.content[0].text.value
            role_content.append([role, content])
            #print(f"\n[bold magenta]{role}[/bold magenta]: [italic red]{content}[/italic red]")
        
        print(f"""\n💉 {role_content[0][1]}""")

 
 
    def call(self):
        while True:
            users_prompt = Prompt.ask('\n')

            if users_prompt.lower() == 'exit':
                break

            self.submit_message_and_get_response(users_prompt)

        print("""\n💉 またいつでも呼んでください！\n""")


if __name__ == "__main__":
    func = AssistantsAPI()
    print(f"\n💉 こんにちは！ 看護学習AIです。楽しく看護学を身につけましょう。何か質問はありますか？  会話を終えるに`exit`と入力してください。\n")
    func.call()


