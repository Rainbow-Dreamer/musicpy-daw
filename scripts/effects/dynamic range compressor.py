from pydub import AudioSegment
from pydub.effects import compress_dynamic_range
'''
This synth data structure could be used in musicpy daw as an instrument (wave generator) or effect (used in mixer for each channel).
The function is to either generate a type of sound as raw wave data with given pitch or frequency,
or take raw wave data as input and make some changes and then output the new raw wave data.
'''


class Synth:

    def __init__(self):
        self.name = 'dynamic range compressor'
        self.author = 'rainbow'
        self.description = ''
        self.instrument_parameters = {}
        self.effect_parameters = dict(threshold=-20.0,
                                      ratio=4.0,
                                      attack=5.0,
                                      release=50.0)
        self.enabled = True

    def generate_sound(self, current_note, bpm=None) -> AudioSegment:
        pass

    def apply_effect(self, data: AudioSegment) -> AudioSegment:
        current_sound = compress_dynamic_range(data, **self.effect_parameters)
        return current_sound

    def __repr__(self):
        return f'[Synth]\nname: {self.name}\nauthor: {self.author}\ndescription: {self.description}'
