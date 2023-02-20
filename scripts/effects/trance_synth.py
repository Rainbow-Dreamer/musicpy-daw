import musicpy as mp
from pydub import AudioSegment
from pydub.generators import SignalGenerator
import math
'''
This synth data structure could be used in musicpy daw as an instrument (wave generator) or effect (used in mixer for each channel).
The function is to either generate a type of sound as raw wave data with given pitch or frequency,
or take raw wave data as input and make some changes and then output the new raw wave data.
'''


class Synth:

    def __init__(self):
        self.name = 'trance synth'
        self.author = 'rainbow'
        self.description = ''
        self.instrument_parameters = {
            'volume level': 0.2,
            'duty cycle': 0.3,
            'change ratio': 2,
            'change remainder': 1.0,
            'fade time': 100,
            'ADSR': [0, 0, 0, 0]
        }
        self.effect_parameters = {}
        self.enabled = True

    def generate_sound(self, current_note, bpm=None) -> AudioSegment:
        current_volume_level = self.instrument_parameters['volume level']
        current_duty_cycle = self.instrument_parameters['duty cycle']
        current_change_ratio = self.instrument_parameters['change ratio']
        current_change_remainder = self.instrument_parameters[
            'change remainder']
        current_fade_time = self.instrument_parameters['fade time']
        current_adsr = self.instrument_parameters['ADSR']
        if not hasattr(current_note, 'synth'):
            current_freq = mp.get_freq(current_note)
            current_duration = mp.bar_to_real_time(current_note.duration,
                                                   bpm,
                                                   mode=1)
            current_volume = velocity_to_db(current_note.volume *
                                            current_volume_level)
        else:
            current_freq, current_duration, current_volume = current_note.synth
        result = Custom_sawtooth(
            freq=current_freq,
            duty_cycle=current_duty_cycle,
            change_ratio=current_change_ratio,
            change_remainder=current_change_remainder).to_audio_segment(
                current_duration, current_volume)
        if current_fade_time > 0:
            result = result.fade_in(current_fade_time).fade_out(
                current_fade_time)
        if not all(i == 0 for i in current_adsr):
            result = adsr_func(result, *current_adsr)
        return result

    def apply_effect(self, data: AudioSegment) -> AudioSegment:
        duration = self.effect_parameters['duration']
        current_sound = data.fade_in(duration)
        return current_sound

    def __repr__(self):
        return f'[Synth]\nname: {self.name}\nauthor: {self.author}\ndescription: {self.description}'


def velocity_to_db(vol):
    if vol == 0:
        return -100
    return math.log(vol / 127, 10) * 20


def percentage_to_db(vol):
    if vol == 0:
        return -100
    return math.log(abs(vol / 100), 10) * 20


def adsr_func(sound, attack, decay, sustain, release):
    change_db = percentage_to_db(sustain)
    result_db = sound.dBFS + change_db
    if attack > 0:
        sound = sound.fade_in(attack)
    if decay > 0:
        sound = sound.fade(to_gain=result_db, start=attack, duration=decay)
    else:
        sound = sound[:attack].append(sound[attack:] + change_db, crossfade=0)
    if release > 0:
        sound = sound.fade_out(release)
    return sound


class Custom_sawtooth(SignalGenerator):

    def __init__(self,
                 freq,
                 duty_cycle=1.0,
                 change_ratio=2,
                 change_remainder=1.0,
                 **kwargs):
        super().__init__(**kwargs)
        self.freq = freq
        self.duty_cycle = duty_cycle
        self.change_ratio = change_ratio
        self.change_remainder = change_remainder

    def generate(self):
        sample_n = 0

        # in samples
        cycle_length = self.sample_rate / float(self.freq)
        midpoint = cycle_length * self.duty_cycle
        ascend_length = midpoint
        descend_length = cycle_length - ascend_length

        while True:
            cycle_position = sample_n % cycle_length
            if cycle_position < midpoint:
                yield (self.change_ratio * cycle_position /
                       ascend_length) - self.change_remainder
            else:
                yield self.change_remainder - (self.change_ratio *
                                               (cycle_position - midpoint) /
                                               descend_length)
            sample_n += 1
