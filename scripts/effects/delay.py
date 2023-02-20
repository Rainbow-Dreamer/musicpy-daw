from pydub import AudioSegment
import math
'''
This synth data structure could be used in musicpy daw as an instrument (wave generator) or effect (used in mixer for each channel).
The function is to either generate a type of sound as raw wave data with given pitch or frequency,
or take raw wave data as input and make some changes and then output the new raw wave data.
'''


class Synth:

    def __init__(self):
        self.name = 'delay'
        self.author = 'rainbow'
        self.description = ''
        self.instrument_parameters = {}
        self.effect_parameters = {
            'interval': 0.5,
            'unit': 6,
            'volumes': None,
            'decrease_unit': None,
            'bar_interval': None,
            'bpm': None
        }
        self.enabled = True

    def generate_sound(self, current_note, bpm=None) -> AudioSegment:
        pass

    def apply_effect(self, data: AudioSegment) -> AudioSegment:
        interval = self.effect_parameters['interval']
        unit = self.effect_parameters['unit']
        volumes = self.effect_parameters['volumes']
        decrease_unit = self.effect_parameters['decrease_unit']
        bar_interval = self.effect_parameters['bar_interval']
        bpm = self.effect_parameters['bpm']
        if bar_interval is not None and bpm is not None:
            interval = bar_to_real_time(bar_interval, bpm, 1) / 1000
        current_sound = delay(data, interval, unit, volumes, decrease_unit)
        return current_sound

    def __repr__(self):
        return f'[Synth]\nname: {self.name}\nauthor: {self.author}\ndescription: {self.description}'


def percentage_to_db(vol):
    if vol == 0:
        return -100
    return math.log(abs(vol / 100), 10) * 20


def bar_to_real_time(bar, bpm, mode=0):
    return int(
        (60000 / bpm) * (bar * 4)) if mode == 0 else (60000 / bpm) * (bar * 4)


def delay(sound, interval=0.5, unit=6, volumes=None, decrease_unit=None):
    # delay effect using pydub, the delay sounds would be decreasing volume one by one,
    # placing at a interval one after another after the original sound

    # sound: a pydub AudioSegment instance

    # interval: the time between each delay sound in seconds

    # unit: the number of the delay sounds

    # volumes: you can specify the volume of each delay sound using this parameter,
    # could be a list or tuple, the elements are volume percentages (from 0 to 100)

    # decrease_unit: you can specify the decrease unit (in percentages) of the volumes of the delay sounds using this parameter
    '''
    # examples
    
    test_audio = AudioSegment.from_file('C5.wav')
    test_audio_with_delay = delay(test_audio, 0.2, 15)
    play_sound(test_audio_with_delay)
    # test_audio_with_delay.export('C5 with delay.wav')
    
    '''
    if volumes:
        unit = len(volumes)
    whole_length = (unit * interval * 1000) + len(sound)
    result = AudioSegment.silent(duration=whole_length)
    result = result.overlay(sound, position=0)
    if not volumes:
        volume_unit = 100 / unit if decrease_unit is None else decrease_unit
        volumes = [100 - i * volume_unit for i in range(1, unit + 1)]
        volumes = [i if i >= 0 else 0 for i in volumes]
        volumes = [percentage_to_db(i) for i in volumes]
    else:
        volumes = [percentage_to_db(i) for i in volumes]
    for i in range(unit):
        current_volume = volumes[i]
        current = sound + current_volume
        result = result.overlay(current, position=interval * (i + 1) * 1000)
    return result
