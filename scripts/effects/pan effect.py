from pydub import AudioSegment
from pydub.effects import pan
'''
This synth data structure could be used in musicpy daw as an instrument (wave generator) or effect (used in mixer for each channel).
The function is to either generate a type of sound as raw wave data with given pitch or frequency,
or take raw wave data as input and make some changes and then output the new raw wave data.
'''


class Synth:

    def __init__(self):
        self.name = 'pan effect'
        self.author = 'Rainbow Dreamer'
        self.description = ''
        self.instrument_parameters = {}
        self.effect_parameters = {'pan amount': 0}
        self.enabled = True

    def generate_sound(self, current_note, bpm=None) -> AudioSegment:
        pass

    def apply_effect(self, data: AudioSegment) -> AudioSegment:
        pan_amount = self.effect_parameters['pan amount']
        current_sound = pan(data, pan_amount)
        return current_sound

    def __repr__(self):
        return f'[Synth]\nname: {self.name}\nauthor: {self.author}\ndescription: {self.description}'
