from prompt_toolkit import Application, prompt
import asyncio
import pyaudio
import numpy as np
from sdbus import (DbusInterfaceCommonAsync, dbus_method_async,
                   dbus_property_async, dbus_signal_async)

# Libraries from tencent github repo
from common import credential
from asr import speech_recognizer
import pvporcupine
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
class ASRListener(speech_recognizer.SpeechRecognitionListener):
    def __init__(self,interface:ASRInterface):
        self.interface=interface
    def on_recognition_start(self, response):
        print(123)
        #pass
        #print("%s|%s|OnRecognitionStart\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), response['voice_id']))
    def on_recognition_result_change(self,response):
        self.interface.input.emit(response['result']['voice_text_str'])
        print(asr_running,response['result']['voice_text_str'])
    def on_sentence_end(self, response):
        print(1)
        self.interface.finished.emit(True)
        self.interface.active.emit(False)
        globals()['asr_running']=False
from asyncio import new_event_loop, sleep
from random import randint
from time import time


from sdbus import request_default_bus_name_async

#loop = new_event_loop()

export_object = ASRInterface()
asr_running=False
async def startup() -> None:
    p = pyaudio.PyAudio()
    # Open stream

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=512)
    credential_var = credential.Credential(SECRET_ID, SECRET_KEY)
    listener=ASRListener(export_object)
    recognizer = speech_recognizer.SpeechRecognizer(
        APPID, credential_var, ENGINE_MODEL_TYPE,  listener)
    recognizer.set_filter_modal(0)
    recognizer.set_filter_punc(0)
    recognizer.set_voice_format(1)
    recognizer.set_need_vad(1)
    recognizer.set_vad_silence_time(240)
    await request_default_bus_name_async('org.agentserver.asr')
    # Export the object to D-Bus
    export_object.export_to_dbus('/org/agentserver/tencentasr')
    handle = pvporcupine.create(access_key=access_key, model_path="./porcupine_params_zh.pv",keyword_paths=['./你好灵犀_zh_linux_v3_0_0.ppn'])

    recognizer.start()
    content = stream.read(512)
    
    while content:
        try:
            content = stream.read(512)
        except KeyboardInterrupt:
            break
        print(asr_running)
        if asr_running:
            recognizer.write(content)
#        content = stream.read(512)

        keyword_index = await asyncio.get_running_loop().run_in_executor(None,lambda :handle.process(np.frombuffer(content, dtype=np.int16)))
        if keyword_index >= 0:
            recognizer.start()
            export_object.active.emit(True)
            export_object.input.emit("")
            globals()['asr_running']=True
        #sleep模拟实际实时语音发送间隔
        #time.sleep(0.02)

    recognizer.stop()


if __name__=="__main__":
    import os
    access_key = os.getenv("TENCENTASR_PV_access_key")
    APPID = os.getenv("TENCENTASR_APPID")
    SECRET_ID = os.getenv("TENCENTASR_SECRET_ID")
    SECRET_KEY = os.getenv("TENCENTASR_SECRET_KEY")
    ENGINE_MODEL_TYPE = "16k_zh"
    loop.run_until_complete(startup())
    loop.run_forever()
