from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import time
import random
import keyboard
from copy import deepcopy as copy
import os
import sys
import pygame
import mido
import midiutil
from musicpy import *
from ast import literal_eval
from io import BytesIO
import math
import array
import simpleaudio
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio as play_sound
from pydub.generators import Sine, Triangle, Sawtooth, Square, WhiteNoise, Pulse
import librosa
import soundfile

AudioSegment.converter = "ffmpeg\\bin\\ffmpeg.exe"

abs_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(abs_path)
sys.path.append(abs_path)
with open('scripts/easy sampler.pyw') as f:
    exec(f.read())