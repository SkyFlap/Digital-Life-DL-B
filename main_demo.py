import os
import platform
from transformers import AutoConfig, AutoModel, AutoTokenizer
import pyttsx3
from os import listdir, path
import numpy as np
import scipy, cv2, os, sys, argparse, audio
import json, subprocess, random, string
from tqdm import tqdm
from glob import glob
import torch, face_detection
from models import Wav2Lip
import shutil
import time
import sys
import vlc
import librosa
import librosa.filters
# import tensorflow as tf
from scipy import signal
from scipy.io import wavfile
from hparams import hparams as hp

os.environ['PYTHON_VLC_MODULE_PATH'] = "./vlc-3.0.18"


#LLM
##GLM
tokenizer = AutoTokenizer.from_pretrained(".\module\chatglm-6b", trust_remote_code=True)
config = AutoConfig.from_pretrained(".\module\chatglm-6b", trust_remote_code=True, pre_seq_len=64)
model_nlp = AutoModel.from_pretrained(".\module\chatglm-6b", config=config, trust_remote_code=True)
prefix_state_dict = torch.load(os.path.join(CHECKPOINT_PATH, "pytorch_model.bin"))
new_prefix_state_dict = {}
for k, v in prefix_state_dict.items():
    if k.startswith("transformer.prefix_encoder."):
        new_prefix_state_dict[k[len("transformer.prefix_encoder."):]] = v
model_nlp.transformer.prefix_encoder.load_state_dict(new_prefix_state_dict)

model_nlp = model_nlp.quantize(4)
model_nlp = model_nlp.half().cuda()
model_nlp.transformer.prefix_encoder.float()
model_nlp = model_nlp.eval()
os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'
stop_stream = False

def build_prompt(history):
    prompt = "数字生命DL-B，输入内容即可进行对话，clear 清空对话历史，stop 终止程序。"
    for query, response in history:
        prompt += f"\n\n用户:{query}"
        prompt += f"\n\n数字备份:{response}"
        py_tts(response)
    return prompt

def signal_handler(signal, frame):
    global stop_stream
    stop_stream = True


#TTS
##pyttsx3
def py_tts(text):
    tts = pyttsx3.init()
    voices = tts.getProperty('voices')
    tts.setProperty('voice', voices.id)
    tts.save_to_file(text, "./raw_temp/res.mp3")
    tts.runAndWait()

#文件清除
def delet_file():
    os.remove('./raw_temp/res.mp3')
    os.remove('./raw_temp/res.wav')
    os.remove('./raw_temp/temp.wav')
    os.remove('./raw_temp/result.avi')
    os.remove('./raw_temp/audio.mp3')


def main():
    history = []
    global stop_stream
    print("数字生命DL-B，输入内容即可进行对话，clear 清空对话历史，stop 终止程序。")
    while True:
        query = input("\n用户:")
        if query.strip() == "stop":
            break
        if query.strip() == "clear":
            history = []
            os.system(clear_command)
            print("数字生命DL-B，输入内容即可进行对话，clear 清空对话历史，stop 终止程序。")
            continue
        count = 0
        for response, history in model_nlp.stream_chat(tokenizer, query, history=history):
            if stop_stream:
                stop_stream = False
                break
            else:
                count += 1
                if count % 8 == 0:
                    os.system(clear_command)
                    print(build_prompt(history), flush=True)
                    signal.signal(signal.SIGINT, signal_handler)
        os.system(clear_command)
        print(build_prompt(history), flush=True)
        os.system(".\python38\python.exe So-VITS_run.py")
        time.sleep(0.5)
        print("合成视频")
        os.system("python wav2lip_run.py")
        delet_file()


if __name__ == "__main__":
    main()
