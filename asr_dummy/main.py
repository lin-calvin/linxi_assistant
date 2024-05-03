from prompt_toolkit import Application, prompt
import asyncio
import aiohttp
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import VSplit
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.widgets import Button,TextArea

from sdbus import (DbusInterfaceCommonAsync, dbus_method_async,
                   dbus_property_async, dbus_signal_async)
loop=asyncio.get_event_loop()

def async_wrapper(func):
    """used to convert async function to normal function"""
    def wrapper(*args):
        return asyncio.ensure_future(func(*args))
    return wrapper

class ASRInterface(
    DbusInterfaceCommonAsync,
    interface_name='org.agentserver.asr',serving_enabled=True
):
    @dbus_signal_async(signal_signature='s')
    def input(self):
        pass
    @dbus_signal_async(signal_signature='b')
    def active(self):
        pass
    @dbus_signal_async(signal_signature='b')
    def finished(self):
        pass

from asyncio import new_event_loop, sleep
from random import randint
from time import time


from sdbus import request_default_bus_name_async

#loop = new_event_loop()

export_object = ASRInterface()

async def startup() -> None:
    await request_default_bus_name_async('org.agentserver.asr')
# Export the object to D-Bus
    export_object.export_to_dbus('/org/agentserver/dummyasr')

    @async_wrapper
    async def active():
        export_object.active.emit(True)
    @async_wrapper 
    async def submit(document):
        t=document.text
        export_object.finished.emit(False)
        export_object.input.emit(t)
        export_object.finished.emit(True)

#        export_object.input.emit(document.text)
        #print(document.text)
    app=Application(full_screen=False,layout=Layout(VSplit([Button("Active",handler=active),TextArea(accept_handler=submit,prompt="" ,multiline=False)])))
    kb = KeyBindings()
    kb.add("tab")(focus_next)

    @kb.add('c-c')
    def exit_(event):
        event.app.exit()
    app.key_bindings=kb
    # Acquire a known name on the bus
    # Clients will use that name to address this s
    await app.run_async()
if __name__=="__main__":
    loop.run_until_complete(startup())
    loop.run_forever()
