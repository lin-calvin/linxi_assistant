from asyncio import new_event_loop, sleep
from random import randint
from time import time

#from example_interface import ExampleInterface
from main import  AgentInterface as ExampleInterface
from sdbus import request_default_bus_name_async

loop = new_event_loop()

export_object = ExampleInterface("http://localhost:8000")


async def clock() -> None:
    """
    This coroutine will sleep a random time and emit
    a signal with current clock
    """
    while True:
        await sleep(randint(2, 7))  # Sleep a random time
        current_time = int(time())  # The interface we defined uses integers
        export_object.clock.emit(current_time)


async def startup() -> None:
    """Perform async startup actions"""
    # Acquire a known name on the bus
    # Clients will use that name to address this server
    await request_default_bus_name_async('org.example.test')
    # Export the object to D-Bus
    export_object.export_to_dbus('/')


loop.run_until_complete(startup())
task_clock = loop.create_task(clock())
loop.run_forever()
