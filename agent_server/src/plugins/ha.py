import os
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__9668950738c34790aa2ba9f977007e6b"
os.environ["LANGCHAIN_PROJECT"] = "tracking"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
import json
from langchain_core.language_models.chat_models import BaseChatModel as ChatModel
from langchain_core.runnables import RunnablePassthrough
from langchain import hub
from aiohttp import ClientSession
from langchain.tools import tool
import yaml
from langchain_core.output_parsers import JsonOutputParser

intent_yaml="""
# -----------------------------------------------------------------------------
# homassistant
# -----------------------------------------------------------------------------

HassTurnOn:
  supported: true
  domain: homeassistant
  description: "Turns on a device or entity"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
    domain:
      description: "Domain of devices/entities in an area"
      required: false
    device_class:
      description: "Device class of devices/entities in an area"
      required: false
  slot_combinations:
    name_only:
      - "name"
    area_only:
      - "area"
    domain_only:
      - "domain"
    area_name:
      - "name"
      - "area"
    area_domain:
      - "area"
      - "domain"
    area_device_class:
      - "area"
      - "device_class"
    domain_device_class:
      - "domain"
      - "device_class"

HassTurnOff:
  supported: true
  domain: homeassistant
  description: "Turns off a device or entity"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
    domain:
      description: "Domain of devices/entities in an area"
      required: false
    device_class:
      description: "Device class of devices/entities in an area"
      required: false
  slot_combinations:
    name_only:
      - "name"
    area_only:
      - "area"
    domain_only:
      - "domain"
    area_name:
      - "name"
      - "area"
    area_domain:
      - "area"
      - "domain"
    area_device_class:
      - "area"
      - "device_class"
    domain_device_class:
      - "domain"
      - "device_class"

HassGetState:
  supported: true
  domain: homeassistant
  description: "Gets or checks the state of an entity"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
    domain:
      description: "Domain of devices/entities in an area"
      required: false
    device_class:
      description: "Device class of devices/entities in an area"
      required: false
    state:
      description: "Name of state to match"
      required: false
  response_variables:
    state:
      description: "State of the first entity matched"
    query.matched:
      description: "List of states that matched the query and state name"
    query.unmatched:
      description: "List of states that matched everything except state name"

HassNevermind:
  supported: true
  domain: homeassistant
  description: "Does nothing. Used to cancel a request"

HassSetPosition:
  supported: true
  domain: homeassistant
  description: "Sets the position of an entity"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
    domain:
      description: "Domain of devices/entities in an area"
      required: false
    device_class:
      description: "Device class of devices/entities in an area"
      required: false
    position:
      description: "Position from 0 to 100"
      required: true
  slot_combinations:
    name_only:
      - "name"
    area_only:
      - "area"
    domain_only:
      - "domain"
    area_name:
      - "name"
      - "area"
    area_domain:
      - "area"
      - "domain"
    area_device_class:
      - "area"
      - "device_class"
    domain_device_class:
      - "domain"
      - "device_class"

# -----------------------------------------------------------------------------
# light
# -----------------------------------------------------------------------------

HassLightSet:
  supported: true
  domain: light
  description: "Sets the brightness or color of a light"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
    brightness:
      description: "Brightness percentage from 0 to 100"
      required: false
    color:
      description: "Name of color"
      required: false

# -----------------------------------------------------------------------------
# climate
# -----------------------------------------------------------------------------

#HassClimateSetTemperature:
#  supported: true
#  domain: climate
#  description: "Sets the desired temperature of a climate device or entity"
#  slots:
#    name:
#      description: "Name of a device or entity"
#      required: false
#    area:
#      description: "Name of an area"
#      required: false
#    temperature:
#      description: "Temperature in degrees"
#      required: false
#    temperature_unit:
#      description: "Temperature unit"
#      required: false

HassClimateGetTemperature:
  supported: true
  domain: climate
  description: "Gets the current temperature of a climate device or entity"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
  response_variables:
    state:
      description: "State of the entity that contains the temperature"

# -----------------------------------------------------------------------------
# shopping_list
# -----------------------------------------------------------------------------

HassShoppingListAddItem:
  supported: true
  domain: shopping_list
  description: "Adds an item to the shopping list"
  slots:
    item:
      description: "Item to add"
      required: true

# -----------------------------------------------------------------------------
# weather
# -----------------------------------------------------------------------------

HassGetWeather:
  supported: true
  domain: weather
  description: "Gets the current weather"
  slots:
    name:
      description: "Name of the weather entity to use"
      required: false

# -----------------------------------------------------------------------------
# todo
# -----------------------------------------------------------------------------

HassListAddItem:
  supported: true
  domain: todo
  description: "Adds an item to a todo list"
  slots:
    item:
      description: "Item to add"
      required: true
    name:
      description: "Name of the list"
      required: true

# -----------------------------------------------------------------------------
# vacuum
# -----------------------------------------------------------------------------

HassVacuumStart:
  supported: true
  domain: vacuum
  description: "Starts a vacuum"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
  slot_combinations:
    name_only:
      - "name"
    area_only:
      - "area"
    area_name:
      - "name"
      - "area"

HassVacuumReturnToBase:
  supported: true
  domain: vacuum
  description: "Returns a vacuum to base"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
  slot_combinations:
    name_only:
      - "name"
    area_only:
      - "area"
    area_name:
      - "name"
      - "area"

# -----------------------------------------------------------------------------
# media_player
# -----------------------------------------------------------------------------

HassMediaPause:
  supported: true
  domain: media_player
  description: "Pauses a media player"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
  slot_combinations:
    name_only:
      - "name"
    area_only:
      - "area"
    area_name:
      - "name"
      - "area"

HassMediaUnpause:
  supported: true
  domain: media_player
  description: "Unpauses a media player"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
  slot_combinations:
    name_only:
      - "name"
    area_only:
      - "area"
    area_name:
      - "name"
      - "area"
TimerIntent:
  supported: true
  domain: timer
  description: "Fire a intent after times,"
  slots:
    time:
      description: "A python datatime.timedelta object,example: timedelta(seconds=1)"
      required: true
    intent:
      description: "The intent you want to fire after times, the slots of the intent should be include in the intent data part"
      required: true

HassMediaNext:
  supported: true
  domain: media_player
  description: "Skips a media player to the next item"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
  slot_combinations:
    name_only:
      - "name"
    area_only:
      - "area"
    area_name:
      - "name"
      - "area"

HassSetVolume:
  supported: true
  domain: media_player
  description: "Sets the volume of a media player"
  slots:
    name:
      description: "Name of a device or entity"
      required: false
    area:
      description: "Name of an area"
      required: false
    volume_level:
      description: "Volume level from 0 to 100"
      required: true
  slot_combinations:
    name_only:
      - "name"
    area_only:
      - "area"
    area_name:
      - "name"
      - "area"

"""
def process_intent_yaml(content):
    table=yaml.load(content,yaml.FullLoader)
    output=""
    for i in table.keys():
        item=table[i]
        if not item['supported'] or i=="HassNevermind" :
            continue
        slots=""
        for slot_key in item['slots']:
            slot=item['slots'][slot_key]

            if not (slot['required'] or slot_key == "name" ):
                continue
            slots+=f"""        {slot_key}: {slot['description']}\n"""

        output+=(
            f"""{i}:
        Description: {item['description']}
        Slots:
    {slots}
            """)
    return output

class HomeAssistantControlPlugin:
    def __init__(self,chat_model:ChatModel,ha_url,ha_token,prompt=None):
        self.ha_url=ha_url
        self.aiohttp_session=None
        self.ha_token=ha_token
        if prompt==None:
            prompt = hub.pull("calvinlin/hass_intent")
        self.chain={"input":RunnablePassthrough(),"intent_table":lambda x:process_intent_yaml(intent_yaml)}|prompt|chat_model|JsonOutputParser()
    async def procress(self,input):
        """Control homeassistant smart home device"""
        if self.aiohttp_session==None:
            self.aiohttp_session=ClientSession(base_url=self.ha_url,headers={"Authorization":"Bearer "+self.ha_token})
        intent=await self.chain.ainvoke(input)
        print(intent)
        async with self.aiohttp_session.post("/api/intent/handle",data=json.dumps(intent)) as request:
            print(await request.text())
    def as_lc_tools(self):
        async def home_assistant(input):
            """Control homeassistant smart home device, input is natural language command,use the name as user's word by word,Delay/timed control is supported"""
            return await self.procress(input)
        t=tool(home_assistant)
        t.name="home_assistant"
        return [t]

