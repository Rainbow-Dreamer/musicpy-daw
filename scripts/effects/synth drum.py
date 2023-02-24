import musicpy as mp
from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise, Sawtooth
from pydub.effects import low_pass_filter, high_pass_filter
import math
'''
This synth data structure could be used in musicpy daw as an instrument (wave generator) or effect (used in mixer for each channel).
The function is to either generate a type of sound as raw wave data with given pitch or frequency,
or take raw wave data as input and make some changes and then output the new raw wave data.
'''


class Synth:

    def __init__(self):
        self.name = 'synth drum'
        self.author = 'Rainbow Dreamer'
        self.description = ''
        self.instrument_parameters = {
            'volume level': 0.05,
            'snare drum duration': 100,
            'fade time': 80,
            'snare drum pitch volume diff': 7,
            'snare drum pitch': 'A3',
            'hi-hat frequency': 7000,
            'bass drum duration': 200,
            'bass drum unit': 20,
            'bass drum start pitch': 'A4',
            'bass drum pitch shift unit': 3
        }
        self.effect_parameters = {}
        self.enabled = True

    def generate_sound(self, current_note, bpm=None) -> AudioSegment:
        current_volume_level = self.instrument_parameters['volume level']
        current_volume = velocity_to_db(current_note.volume *
                                        current_volume_level)
        if isinstance(current_note, mp.note):
            if str(current_note) == 'C2':
                result = bass_drum(current_volume, self.instrument_parameters)
            elif str(current_note) == 'E2':
                current_snare_drum_duration = self.instrument_parameters[
                    'snare drum duration']
                current_snare_drum_pitch_volume_diff = self.instrument_parameters[
                    'snare drum pitch volume diff']
                current_snare_drum_pitch = self.instrument_parameters[
                    'snare drum pitch']

                part1 = WhiteNoise().to_audio_segment(
                    current_snare_drum_duration, current_volume)
                part2 = Sawtooth(mp.get_freq(
                    mp.N(current_snare_drum_pitch))).to_audio_segment(
                        current_snare_drum_duration,
                        current_volume - current_snare_drum_pitch_volume_diff)
                result = part1.overlay(part2)
                current_fade_time = self.instrument_parameters['fade time']
                result = result.fade_out(current_fade_time)
            elif str(current_note) == 'F#2':
                current_snare_drum_duration = self.instrument_parameters[
                    'snare drum duration']
                result = WhiteNoise().to_audio_segment(
                    current_snare_drum_duration, current_volume)
                result = high_pass_filter(
                    result, self.instrument_parameters['hi-hat frequency'])
                current_fade_time = self.instrument_parameters['fade time']
                result = result.fade_out(current_fade_time)
            else:
                return
        else:
            return
        return result

    def apply_effect(self, data: AudioSegment) -> AudioSegment:
        pass

    def __repr__(self):
        return f'[Synth]\nname: {self.name}\nauthor: {self.author}\ndescription: {self.description}'


def sine(freq=440, duration=1000, volume=0):
    return Sine(freq).to_audio_segment(duration, volume)


def velocity_to_db(vol):
    if vol == 0:
        return -100
    return math.log(vol / 127, 10) * 20


def bass_drum(volume, parameters):
    current_duration = parameters['bass drum duration']
    current_unit = parameters['bass drum unit']
    current_pitch = parameters['bass drum start pitch']
    current_freq = mp.get_freq(current_pitch)
    current_pitch_shift_unit = (2**(
        1 / 12))**parameters['bass drum pitch shift unit']
    volume -= 5
    result = None
    for i in range(current_duration // current_unit):
        if result is None:
            result = Sawtooth(current_freq).to_audio_segment(
                current_unit, volume)
        else:
            current_result = Sawtooth(current_freq).to_audio_segment(
                current_unit, volume)
            result = result.append(current_result, crossfade=0)
        current_freq /= current_pitch_shift_unit
    result = result.fade_out(20)
    return result
