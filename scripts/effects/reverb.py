from pydub import AudioSegment
import numpy as np
import sys

sys.path.append(
    r'C:\Users\andy\AppData\Local\Programs\Python\Python37\Lib\site-packages')
import scipy

scipy.__path__.append(
    r'C:\Users\andy\AppData\Local\Programs\Python\Python37\Lib\site-packages\scipy'
)
from scipy.io import wavfile
import pedalboard
from pedalboard.io import AudioFile
from io import BytesIO
'''
This synth data structure could be used in musicpy daw as an instrument (wave generator) or effect (used in mixer for each channel).
The function is to either generate a type of sound as raw wave data with given pitch or frequency,
or take raw wave data as input and make some changes and then output the new raw wave data.
'''


class Synth:

    def __init__(self):
        self.name = 'reverb'
        self.author = 'rainbow'
        self.description = ''
        self.instrument_parameters = {}
        self.effect_parameters = {
            'room_size': 0.5,
            'damping': 0.5,
            'wet_level': 0.33,
            'dry_level': 0.4,
            'width': 1.0,
            'freeze_mode': 0.0
        }
        self.enabled = True

    def generate_sound(self, current_note, bpm=None) -> AudioSegment:
        pass

    def apply_effect(self, data: AudioSegment) -> AudioSegment:
        current_sound = add_reverb(data, **self.effect_parameters)
        return current_sound

    def __repr__(self):
        return f'[Synth]\nname: {self.name}\nauthor: {self.author}\ndescription: {self.description}'


def add_reverb(audio,
               room_size: float = 0.5,
               damping: float = 0.5,
               wet_level: float = 0.33,
               dry_level: float = 0.4,
               width: float = 1.0,
               freeze_mode: float = 0.0):
    current_reverb = pedalboard.Reverb(room_size=room_size,
                                       damping=damping,
                                       wet_level=wet_level,
                                       dry_level=dry_level,
                                       width=width,
                                       freeze_mode=freeze_mode)
    current_buffer = BytesIO()
    audio.export(current_buffer)
    result = None
    with AudioFile(current_buffer) as f:
        while f.tell() < f.frames:
            chunk = f.read(int(f.samplerate))
            effected = current_reverb(chunk, f.samplerate, reset=False)
            if result is None:
                result = effected
            else:
                result = np.column_stack((result, effected))
    result = result.T
    wav_io = BytesIO()
    wavfile.write(wav_io, 44100, result)
    wav_io.seek(0)
    audio = AudioSegment.from_wav(wav_io)
    audio = audio.set_sample_width(2)
    return audio
