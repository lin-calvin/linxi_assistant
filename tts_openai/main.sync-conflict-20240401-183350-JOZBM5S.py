from prompt_toolkit import Application, prompt
import asyncio
import aiohttp
import openai
import pyaudio
import traceback
from prompt_toolkit.shortcuts import input_dialog
from sdbus import (DbusInterfaceCommonAsync, dbus_method_async,
                   dbus_property_async, dbus_signal_async)
loop=asyncio.get_event_loop()

def async_wrapper(func):
    """used to convert async function to normal function"""
    def wrapper(*args):
        return asyncio.ensure_future(func(*args))
    return wrapper

class TTSInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.agentserver.tts',serving_enabled=True
):
    def __init__(self,client:openai.AsyncClient):
        super().__init__()
        self.client=client
        self.audio=pyaudio.PyAudio()
    @dbus_method_async(input_signature='s',result_signature="i")
    async def speech(self,content):
        print(content)
        try:
            resp_=self.client.audio.with_streaming_response.speech.create(  model="tts-1",voice="alloy",input=content,response_format="pcm") 
            async  with resp_ as resp:
                stream=self.audio.open(format=self.audio.get_format_from_width(2),channels=1,rate=24000,output=True)
                async for data in resp.iter_bytes(24000):
                    stream.write(data)
        except:
            traceback.print_exc()
        return 1
from asyncio import new_event_loop, sleep
from random import randint
from time import time


from sdbus import request_default_bus_name_async

#loop = new_event_loop()

export_object = TTSInterface(openai.AsyncClient(api_key="sk-PoN1CGpLjkBOFrUH06D38c4bCd724c32BeB9D66bDc0a703d",base_url="https://openai.qiheweb.com/v1"))
async def startup() -> None:
    await request_default_bus_name_async('org.agentserver.tts')
# Export the object to D-Bus
    export_object.export_to_dbus('/org/agentserver/openaitts')
if __name__=="__main__":
    loop.run_until_complete(startup())
    loop.run_forever()
