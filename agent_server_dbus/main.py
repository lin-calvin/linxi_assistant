import asyncio
import aiohttp
from sdbus import (DbusInterfaceCommonAsync, dbus_method_async,
                   dbus_property_async, dbus_signal_async)
loop=asyncio.get_event_loop()

class AgentInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.agentserver.agent',serving_enabled=True
):
    def __init__(self,url):
        super().__init__()
        print(asyncio.get_event_loop())
        asyncio.get_event_loop().run_until_complete(self.create_session(url))
    async def create_session(self,base):
        self.session=aiohttp.ClientSession(base_url=base)
    @dbus_method_async(
        input_signature='ss',
        result_signature='s',
        input_args_names=("input","session"),
        result_args_names=("result",)
    )
    async def call(self,input,session):
        print(1)
        #self.session=aiohttp.ClientSession(base_url=url)
        #async def inner(input,session):
        try:
            print(asyncio.current_task())
            async with self.session.post("/api/run/simple",json={"input":input,"session":session if session!="" else None},) as request:
                res=await request.json()
                return res["respond"]
        except:
            import traceback
            traceback.print_exc()
        
from asyncio import new_event_loop, sleep
from random import randint
from time import time


from sdbus import request_default_bus_name_async

#loop = new_event_loop()

export_object = AgentInterface("http://localhost:8000/")

async def startup() -> None:
    """Perform async startup actions"""
    # Acquire a known name on the bus
    # Clients will use that name to address this server
    await request_default_bus_name_async('org.agentserver.httpagent')
    # Export the object to D-Bus
    export_object.export_to_dbus('/org/agentserver/httpagent')

if __name__=="__main__":
    loop.run_until_complete(startup())
    loop.run_forever()
