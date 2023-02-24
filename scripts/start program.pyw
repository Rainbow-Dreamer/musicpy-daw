import os
import sys
from PyQt5 import QtGui, QtWidgets, QtCore
import random
import pickle
from copy import deepcopy as copy
import pygame
import mido_fix
from ast import literal_eval
from io import BytesIO
import math
from pydub import AudioSegment
from pydub.generators import Sine, Triangle, Sawtooth, Square, WhiteNoise, Pulse
import librosa
import soundfile
import py
from scipy.io import wavfile
import pedalboard
from pedalboard.io import AudioFile

abs_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(abs_path)
sys.path.append(abs_path)
sys.path.append('scripts')

import sf2_loader as rs
from musicpy import *

with open('scripts/musicpy daw.pyw', encoding='utf-8-sig') as f:
    exec(f.read())
