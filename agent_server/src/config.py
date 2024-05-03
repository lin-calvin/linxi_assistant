from langchain_openai import ChatOpenAI
from agent_server import Assistant,HttpIO,GradioIO

from langchain.agents import load_tools
import plugins.ha as ha
from configs.presets.agents import react_agent
llm = ChatOpenAI( model="gpt-4")
hass=ha.HomeAssistantControlPlugin(llm,"http://127.0.0.1:8123","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzOWUwYjZhNmE0ZDc0OTZkYjNiYmY4MTI2MTRkOTQ5MCIsImlhdCI6MTcxMTE3MjY0MywiZXhwIjoyMDI2NTMyNjQzfQ.BbOHCoQ226Ank_yGn6-6cZQnWHtblEWrYYJTFNjPi4k").as_lc_tools()
assistant = Assistant()
assistant.data_keys['llm']=llm
assistant.tool_manager.extend(load_tools(["terminal"]))
assistant.tool_manager.extend(hass)
assistant.agent.build_agent(react_agent)
io=GradioIO(assistant)

