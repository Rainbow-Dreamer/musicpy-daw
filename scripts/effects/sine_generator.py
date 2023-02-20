import musicpy as mp
from pydub import AudioSegment
from pydub.generators import Sine
import math
'''
This synth data structure could be used in musicpy daw as an instrument (wave generator) or effect (used in mixer for each channel).
The function is to either generate a type of sound as raw wave data with given pitch or frequency,
or take raw wave data as input and make some changes and then output the new raw wave data.
'''


class Synth:

    def __init__(self):
        self.name = 'sine generator'
        self.author = 'rainbow'
        self.description = ''
        self.instrument_parameters = {'volume level': 0.1}
        self.effect_parameters = {}
        self.enabled = True

    def generate_sound(self, current_note, bpm=None) -> AudioSegment:
        current_volume_level = self.instrument_parameters['volume level']
        if isinstance(current_note, mp.note):
            current_freq = mp.get_freq(current_note)
            current_duration = mp.bar_to_real_time(current_note.duration,
                                                   bpm,
                                                   mode=1)
            current_volume = velocity_to_db(current_note.volume *
                                            current_volume_level)
        else:
            current_freq, current_duration, current_volume
        result = sine(current_freq, current_duration, current_volume)
        return result

    def apply_effect(self, data: AudioSegment) -> AudioSegment:
        duration = self.effect_parameters['duration']
        current_sound = data.fade_in(duration)
        return current_sound

    def __repr__(self):
        return f'[Synth]\nname: {self.name}\nauthor: {self.author}\ndescription: {self.description}'


def sine(freq=440, duration=1000, volume=0):
    return Sine(freq).to_audio_segment(duration, volume)


def velocity_to_db(vol):
    if vol == 0:
        return -100
    return math.log(vol / 127, 10) * 20
