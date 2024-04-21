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
            api_key=OPENAI_API_key #OPENAI_API
        )

    def call(self):

        print("実行")

        print("数学アシスタント作成")
        #print("数学計算の質問をしてください: （例）`3x + 11 = 14`. この式を解いて \n")
        users_prompt = Prompt.ask('数学計算の質問をしてください: （例）`3x + 11 = 14`. この式を解いて \n')

        assistant = self.client.beta.assistants.create(
            name="Math Tutor",
            instructions="You are a personal math tutor. Write and run code to answer math questions.",
            tools=[{"type": "code_interpreter"}],
            model="gpt-3.5-turbo-1106"
        )

        thread = self.client.beta.threads.create()

        print("メッセージ作成")
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content= users_prompt #"次の計算をして欲しい `3x + 11 = 14`. この式を解いてください。"
        )

        print("実行")
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Please address the user as Jane Doe. The user has a premium account."
        )

        # Runのステータスが「completed」になるまで繰り返し確認
        while not run.status == "completed":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            time.sleep(1)  # 0.1秒待機
            print(run.status)  # 現在のステータスを表示

        # スレッドに追加されたメッセージ全てを取得
        messages = self.client.beta.threads.messages.list(
            thread_id=thread.id
        )

        role_value = []

        # 各メッセージのroleとcontentを取得
        for thread_message in messages.data:
            role = thread_message.role
            for content in thread_message.content:
                content = content.text.value
                role_value.append((role, content))

        # reverseメソッドでリストの順番を逆にする
        role_value.reverse()

        # メッセージの内容を表示
        for role, value in role_value:
            #print(f"{role} : {value}")
            
            print(f"""[bold magenta]{role}[/bold magenta]\t:\t[italic red]{value}[/italic red]""")



func = AssistantsAPI()
func.call()