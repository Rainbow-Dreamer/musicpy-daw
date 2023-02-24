from pydub import AudioSegment
import numpy as np
from io import BytesIO
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

    def vst_apply_effect(self, data: AudioSegment):
        from pedalboard.io import AudioFile
        from scipy.io import wavfile
        current_buffer = BytesIO()
        data.export(current_buffer)
        result = None
        self.vst.reset()
        with AudioFile(current_buffer) as f:
            while f.tell() < f.frames:
                chunk = f.read(int(f.samplerate))
                effected = self.vst(chunk, f.samplerate, reset=False)
                if result is None:
                    result = effected
                else:
                    result = np.column_stack((result, effected))
        result = result.T
        wav_io = BytesIO()
        wavfile.write(wav_io, data.frame_rate, result)
        wav_io.seek(0)
        audio = AudioSegment.from_wav(wav_io)
        audio = audio.set_sample_width(2)
        return audio

    def vst_get_parameters(self):
        result = {i: getattr(self.vst, i) for i in self.vst.parameters}
        for i, j in result.items():
            result[i] = j.type(j)
        return result

    def vst_get_parameter_valid_values(self):
        result = {i: j.valid_values for i, j in self.vst.parameters.items()}
        return result

    def vst_update_parameters(self, current_parameters):
        for i, j in current_parameters.items():
            try:
                setattr(self.vst, i, j)
            except:
                pass


def vst_to_synth(sound_path):
    import pedalboard
    current_vst = pedalboard.load_plugin(sound_path)
    current_parameters = list(current_vst.parameters.keys())
    current_synth = Synth()
    current_synth.vst = current_vst
    current_synth.apply_effect = current_synth.vst_apply_effect
    current_synth.name = current_vst.name
    return current_synth
