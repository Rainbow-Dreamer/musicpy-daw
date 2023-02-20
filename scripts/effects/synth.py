from pydub import AudioSegment
'''
This synth data structure could be used in musicpy daw as an instrument (wave generator) or effect (used in mixer for each channel).
The function is to either generate a type of sound as raw wave data with given pitch or frequency,
or take raw wave data as input and make some changes and then output the new raw wave data.
'''


class Synth:

    def __init__(self):
        self.name = 'untitled'
        self.author = ''
        self.description = ''
        self.instrument_parameters = {}
        self.effect_parameters = {}
        self.enabled = True

    def generate_sound(self, current_note, bpm=None) -> AudioSegment:
        pass

    def apply_effect(self, data: AudioSegment) -> AudioSegment:
        pass

    def __repr__(self):
        return f'[Synth]\nname: {self.name}\nauthor: {self.author}\ndescription: {self.description}'
