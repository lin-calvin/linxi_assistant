from agent_server import Assistant
from langchain import hub
from langchain.agents import (
    create_openai_functions_agent,
    create_json_chat_agent,
)
from langchain.agents import AgentExecutor
def react_agent(assistant: Assistant,llm=None,prompt=None):
    tools = assistant.tool_manager.to_list()
    if llm==None:
        llm=assistant.data_keys['llm']
    if prompt==None:
        prompt=hub.pull("calvinlin/react-chat-json-cot")
    agent = create_json_chat_agent(
        llm, tools,prompt
    )

    return AgentExecutor(agent=agent, tools=tools, verbose=True)
