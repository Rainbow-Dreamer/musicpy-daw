from pydub import AudioSegment
import numpy as np
import sys

sys.path.append(
    r'C:\Users\andy\AppData\Local\Programs\Python\Python37\Lib\site-packages')
import scipy

scipy.__path__.append(
    r'C:\Users\andy\AppData\Local\Programs\Python\Python37\Lib\site-packages\scipy'
)
import pyroomacoustics as pra
'''
This synth data structure could be used in musicpy daw as an instrument (wave generator) or effect (used in mixer for each channel).
The function is to either generate a type of sound as raw wave data with given pitch or frequency,
or take raw wave data as input and make some changes and then output the new raw wave data.
'''


class Synth:

    def __init__(self):
        self.name = 'reverb2'
        self.author = 'rainbow'
        self.description = ''
        self.instrument_parameters = {}
        self.effect_parameters = dict(reverb_seconds=0.5,
                                      room_size=[9, 7.5, 3.5],
                                      source_location=[2.5, 3.73, 1.76],
                                      source_delay=0.3,
                                      microphone_locations=[[6.3, 4.87, 1.2],
                                                            [6.3, 4.93, 1.2]])
        self.enabled = True

    def generate_sound(self, current_note, bpm=None) -> AudioSegment:
        pass

    def apply_effect(self, data: AudioSegment) -> AudioSegment:
        current_sound = add_reverb(data, **self.effect_parameters)
        return current_sound

    def __repr__(self):
        return f'[Synth]\nname: {self.name}\nauthor: {self.author}\ndescription: {self.description}'


def audio_to_array(audio):
    result = np.array(audio.get_array_of_samples())
    return result


def array_to_audio(array, sample_width=4, sample_rate=44100, num_channels=1):
    result = AudioSegment(array.tobytes(),
                          sample_width=sample_width,
                          frame_rate=sample_rate,
                          channels=num_channels)
    result = result.set_sample_width(2)
    return result


def add_reverb(audio,
               reverb_seconds=0.5,
               room_size=[9, 7.5, 3.5],
               source_location=[2.5, 3.73, 1.76],
               source_delay=0.3,
               microphone_locations=[[6.3, 4.87, 1.2], [6.3, 4.93, 1.2]]):
    current_array = audio_to_array(audio)
    e_absorption, max_order = pra.inverse_sabine(reverb_seconds, room_size)
    room = pra.ShoeBox(room_size,
                       fs=audio.frame_rate,
                       materials=pra.Material(e_absorption),
                       max_order=max_order)
    room.add_source(source_location, signal=current_array, delay=source_delay)
    mic_locs = np.array(microphone_locations).T
    room.add_microphone_array(mic_locs)
    room.compute_rir()
    room.simulate()
    current_result = room.mic_array.signals
    current_result = current_result.astype(current_array.dtype)
    current_result = current_result[:len(current_result) // 2]
    result = array_to_audio(current_result,
                            sample_width=audio.sample_width,
                            sample_rate=audio.frame_rate,
                            num_channels=audio.channels)
    return result
