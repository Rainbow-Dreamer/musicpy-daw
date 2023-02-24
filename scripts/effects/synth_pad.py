import musicpy as mp
from pydub import AudioSegment
from pydub.generators import Sawtooth
import math
'''
This synth data structure could be used in musicpy daw as an instrument (wave generator) or effect (used in mixer for each channel).
The function is to either generate a type of sound as raw wave data with given pitch or frequency,
or take raw wave data as input and make some changes and then output the new raw wave data.
'''


class Synth:

    def __init__(self):
        self.name = 'synth pad'
        self.author = 'Rainbow Dreamer'
        self.description = ''
        self.instrument_parameters = {
            'volume level': 0.2,
            'duty cycle': 1.0,
            'ADSR': [600, 0, 0, 500],
            'pad depth': 5,
            'pitch diff unit': 0.125,
            'shift time unit': 100,
            'fade time': 50
        }
        self.effect_parameters = {}
        self.enabled = True

    def generate_sound(self, current_note, bpm=None) -> AudioSegment:
        current_volume_level = self.instrument_parameters['volume level']
        current_duty_cycle = self.instrument_parameters['duty cycle']
        current_pad_depth = self.instrument_parameters['pad depth']
        current_pitch_diff_unit = self.instrument_parameters['pitch diff unit']
        current_shift_time_unit = self.instrument_parameters['shift time unit']
        current_adsr = self.instrument_parameters['ADSR']
        current_fade_time = self.instrument_parameters['fade time']
        if not hasattr(current_note, 'synth'):
            current_freq = mp.get_freq(current_note)
            current_duration = mp.bar_to_real_time(current_note.duration,
                                                   bpm,
                                                   mode=1)
            current_volume = velocity_to_db(current_note.volume *
                                            current_volume_level)
        else:
            current_freq, current_duration, current_volume = current_note.synth
        pitch_unit = 2**(1 / 12)
        lower_pitch = -current_pitch_diff_unit * (current_pad_depth // 2)
        current_sounds = []
        for i in range(current_pad_depth):
            current_pad_freq = current_freq * (pitch_unit**(
                lower_pitch + current_pitch_diff_unit * i))
            current_sound = Sawtooth(
                freq=current_pad_freq,
                duty_cycle=current_duty_cycle).to_audio_segment(
                    current_duration, current_volume)
            if current_fade_time > 0:
                current_sound = current_sound.fade_in(
                    current_fade_time).fade_out(current_fade_time)
            current_sounds.append(current_sound)
        result = None
        for i, each in enumerate(current_sounds):
            current_start_time = i * current_shift_time_unit
            result = overlay_append(result, each, current_start_time)
        if not all(i == 0 for i in current_adsr):
            result = adsr_func(result, *current_adsr)
        return result

    def apply_effect(self, data: AudioSegment) -> AudioSegment:
        pass

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
        if sustain > 0:
            sound = sound[:attack].append(sound[attack:] + change_db,
                                          crossfade=0)
    if release > 0:
        sound = sound.fade_out(release)
    return sound


def overlay_append(silent_audio, current_silent_audio, current_start_time):
    current_audio_duration = current_start_time + len(current_silent_audio)
    if silent_audio is None:
        new_whole_duration = current_audio_duration
        silent_audio = AudioSegment.silent(duration=new_whole_duration)
        silent_audio = silent_audio.overlay(current_silent_audio,
                                            position=current_start_time)
    else:
        silent_audio_duration = len(silent_audio)
        new_whole_duration = max(current_audio_duration, silent_audio_duration)
        new_silent_audio = AudioSegment.silent(duration=new_whole_duration)
        new_silent_audio = new_silent_audio.overlay(silent_audio)
        new_silent_audio = new_silent_audio.overlay(
            current_silent_audio, position=current_start_time)
        silent_audio = new_silent_audio
    return silent_audio
