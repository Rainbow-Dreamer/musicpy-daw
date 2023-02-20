from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter
'''
This synth data structure could be used in musicpy daw as an instrument (wave generator) or effect (used in mixer for each channel).
The function is to either generate a type of sound as raw wave data with given pitch or frequency,
or take raw wave data as input and make some changes and then output the new raw wave data.
'''


class Synth:

    def __init__(self):
        self.name = 'high low pass filter'
        self.author = 'rainbow'
        self.description = ''
        self.instrument_parameters = {}
        self.effect_parameters = {
            'low pass cut off': 5000,
            'high pass cut off': 100
        }
        self.enabled = True

    def generate_sound(self, current_note, bpm=None) -> AudioSegment:
        pass

    def apply_effect(self, data: AudioSegment) -> AudioSegment:
        low_pass_cut_off = self.effect_parameters['low pass cut off']
        high_pass_cut_off = self.effect_parameters['high pass cut off']
        current_sound = low_pass_filter(data, low_pass_cut_off)
        current_sound = high_pass_filter(current_sound, high_pass_cut_off)
        return current_sound

    def __repr__(self):
        return f'[Synth]\nname: {self.name}\nauthor: {self.author}\ndescription: {self.description}'
