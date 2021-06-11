from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import time
import random
import keyboard
from copy import deepcopy as copy
import os, sys
import pygame
import mido
import midiutil
from musicpy import *
from ast import literal_eval
import math
import array
from pydub import AudioSegment

AudioSegment.converter = "ffmpeg\\bin\\ffmpeg.exe"

abs_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(abs_path)
sys.path.append(abs_path)
with open('scripts/easy sampler.pyw') as f:
    exec(f.read())