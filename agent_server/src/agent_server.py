import os


os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__9668950738c34790aa2ba9f977007e6b"
os.environ["LANGCHAIN_PROJECT"] = "tracking"
#os.environ["LANGCHAIN_TRACING_V2"] = "true"
import uvicorn
from functools import reduce
import uuid
from  fastapi import FastAPI,HTTPException,Body
from contextvars import ContextVar

from langchain_core.runnables import Runnable
from typing import Any, Optional
from collections import UserDict, UserList
#from langchain_community.chat_models import ChatOpenAI 
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from jinja2 import Template
from langchain.tools import Tool, tool
import feedparser

session = ContextVar("Session")


class DataSource:
    name: str
    description: str

    def fetch_data(self) -> str:
        pass

    def async_fetch_data(self) -> str:
        return self.fetch_data()


class DataSourceManager:
    def __init__(self):
        self.sources: dict[str, DataSource] = {}

    def add_source(self, datasource: DataSource):
        self.sources[datasource.name] = datasource

    def list_sources(self,t=None):
        "List avaliable datasources and source ids,can be used to get source_id when user asking about datasources"
        return Template(
            """source : description
{% for i in datasources %}
{{i.name}} : {{i.description}}

{% endfor %}"""
        ).render(datasources=list(self.sources.values()))

    def fetch_data(self, source_id: str):
        """fetch data from datasource,the param `source_id` should get from 'list_data_source',not from user driectly"""
        return self.sources[source_id].fetch_data()

    async def async_fetch_data(self, source):
        try:
            return await self.sources[source].async_fetch_data()
        except:
            return "Failed to fetch datas"

    def as_lc_tools(self):
        methods_to_wrap = ["fetch_data", "list_sources"]
        tools = [tool(getattr(self, method_name)) for method_name in methods_to_wrap]
        for tool_obj in tools:
            tool_obj.name = f"datasource.{tool_obj.name}"
        description = Tool.from_function(
            func=lambda *_, **__: "Dont call this directly",
            description="Datasource is where you can fetch datas, when user asking about some news/infomations it is useful.This is only a description,dont call this directly,call datasource.xxx insted",
            name="Datasource toolkits",
        )
        return [*tools, description]


class eachBindSort:
    def __init__(self, name):
        self.name = name
        self.value = None

    def __set__(self, obj, value):
        setattr(value, self.name, obj)
        self.value = value

    def __get__(self, _, __=None):
        return self.value


class Session:
    def __init__(self, assistant):
        self.assistant = assistant
        self.history = []

    def run(self, *args, **kwargs):
        session.set(self)
        return self.assistant.run(*args, **kwargs)
    def session_as_tuple(self):
        return list(map(lambda x:(x.type,x.content),self.history))

class SessionManager:
    def __init__(self):
        self.assistant = None
        self.sessions = {}

    def create_session(self):
        id = str(uuid.uuid4())
        self.sessions[id] = session = Session(self.assistant)
        return id, session

    def get_session(self, id):
        return self.sessions[id]


class ToolManager(UserList):
    def to_list(self):
        return list(self)


class Agent:
    agent: Runnable

    def __init__(self):
        self.assistant: Optional[Assistant] = None

    def build_agent(self, factory):
        self.agent = factory(self.assistant)

    async def run(self, input: str, chat_history=[]):
        return (
            await self.agent.ainvoke({"input": input, "chat_history": chat_history})
        )["output"]


class Assistant:
    agent = eachBindSort("assistant")
    tool_manager = eachBindSort("assistant")
    data_source_manager = eachBindSort("assistant")
    session_mamager = eachBindSort("assistant")

    def __init__(self):
        self.agent = Agent()
        self.tool_manager = ToolManager()
        self.data_source_manager = DataSourceManager()
        self.session_mamager = SessionManager()
        self.tool_manager.extend(self.data_source_manager.as_lc_tools())
        self.data_keys={}
    async def run(self, input):
        current_session = session.get()
        history: list = current_session.history
        output = await self.agent.run(input, history)
        history.extend([HumanMessage(content=input), AIMessage(content=output)])
        return output


class IO:
    pass


import gradio as gr


class GradioIO(IO):
    def __init__(self, assistant):
        self.assistant: Assistant = assistant

        with gr.Blocks() as g:
            state = gr.State("")
            with gr.Column(variant="panel"):
                gr.Markdown("Chat")
                with gr.Group():
                    chatbot = gr.Chatbot()
                    with gr.Group():
                        with gr.Row():
                            msg = gr.Textbox(
                                scale=4,
                                show_label=False,
                                placeholder="",
                                container=False,
                            )
                            button = gr.Button(
                                variant="primary", scale=1, min_width=150
                            )
                clear = gr.ClearButton([msg, chatbot])
            with gr.Column(variant="panel"):
                gr.Markdown("Daily news")
                start = gr.Button()
                news = gr.Textbox()

            async def make_news():
                return await self.assistant.agent.run("总结下今天的新闻 用中文 从多个源总结")

            async def respond(message, chat_history, state):
                if state == "":
                    state, session = self.assistant.session_mamager.create_session()
                else:
                    print(self.assistant.session_mamager.sessions)
                    session = self.assistant.session_mamager.get_session(state)
                session.history = list(
                    reduce(
                        lambda x, y: x + list(y),
                        map(
                            lambda x: (
                                HumanMessage(content=x[0]),
                                AIMessage(content=x[1]),
                            ),
                            chat_history,
                        ),[]
                    )
                )
                chat_history.append((message, await session.run(message)))
                return "", chat_history, state

            button.click(respond, [msg, chatbot,state], [msg, chatbot,state])
            msg.submit(respond, [msg, chatbot, state], [msg, chatbot, state])
            start.click(make_news, outputs=news)
        self.gr = g

    async def chat(self, input, history):
        return await self.assistant.agent.run(input)

    def run(self):
        self.gr.launch()
class HttpIO(IO):
    def __init__(self,assistant:Assistant):
        self.assistant=assistant
        self.app=app=FastAPI()
        app.get("/api/create_session")(self.create_session)
        app.post("/api/run/simple")(self.run_simple)
    def create_session(self):
        return self.assistant.session_mamager.create_session()[0]
    async def run_simple(self,input:str=Body(),session:Optional[str]=Body(None)):
        if session==None:
            sess=self.assistant.session_mamager.create_session()[1]
        else:
            try:
                print(session)
                sess=self.assistant.session_mamager.get_session(session)
            except:
                raise HTTPException(status_code=404,detail="Session not found")
        return {"respond":await sess.run(input),"history":sess.session_as_tuple()}
    def run(self):
        uvicorn.run(self.app)
class RssDataSource:
    def __init__(self, name, url, length=1):
        self.url = url
        self.name = name
        self.length = length
        self.description = f'Rss feed of "{name}"'

    def fetch_data(self):
        feed = feedparser.parse(self.url)["entries"]
        res = ""
        for i in range(self.length):
            if len(feed) < i + 1:
                break
            res += f"{i}. {feed[i]['summary']}\n\n"
        return res


def main():
    import importlib.machinery
    import argparse
    parser=argparse.ArgumentParser(description='Agent server')
    parser.add_argument("config")
    args=parser.parse_args()
    config_path=args.config
    config= loader = importlib.machinery.SourceFileLoader('config',config_path).load_module()
    config.io.run()
if __name__=="__main__":
    main()