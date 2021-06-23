import os
import sys
from ast import literal_eval
from io import BytesIO
# ESI file is Easy Sampler Instrument
# an ESI file combines a folder of sounds (samples) files
# and a track settings file (not necessary) into one file,
# and need a split message file (ESS file, Easy Sampler Split) to be loaded in
# Easy Sampler or to unzip as a folder of sound files and a track settings file.
# (if there is one text file in ESI file, then it will be handled as a track settings file)
with open('settings.py', encoding='utf-8-sig') as f:
    exec(f.read())
file_path = '../resources/sounds'


def make_esi(file_path, name='untitled'):
    abs_path = os.getcwd()
    filenames = os.listdir(file_path)
    if not filenames:
        print('There are no sound files to make ESI files')
        return
    length_list = []
    with open(f'{name}.esi', 'wb') as file:
        os.chdir(file_path)
        for t in filenames:
            with open(t, 'rb') as f:
                each = f.read()
                length_list.append(len(each))
                file.write(each)
    os.chdir(abs_path)
    with open(f'{name}.ess', 'w', encoding='utf-8-sig') as f:
        f.write(
            str(length_list) + ',' +
            str([os.path.basename(i) for i in filenames]))
    print(
        f'Successfully made ESI file and ESS file: {name}.esi and {name}.ess')


def unzip_esi(file_path, split_file_path, folder_name=None):
    with open(split_file_path, 'r', encoding='utf-8-sig') as f:
        unzip = f.read()
    unzip_ind, filenames = literal_eval(unzip)
    if folder_name is None:
        folder_name = os.path.basename(file_path)
        folder_name = folder_name[:folder_name.rfind('.')]
    if folder_name not in os.listdir():
        os.mkdir(folder_name)
    with open(file_path, 'rb') as file:
        os.chdir(folder_name)
        for each in range(len(filenames)):
            current_filename = filenames[each]
            print(f'Currently unzip file {current_filename}')
            current_length = unzip_ind[each]
            with open(current_filename, 'wb') as f:
                f.write(file.read(current_length))
    print(f'Unzip {os.path.basename(file_path)} successfully')


def load_esi(file_path, split_file_path, mode='pygame'):
    with open(split_file_path, 'r', encoding='utf-8-sig') as f:
        unzip = f.read()
    unzip_ind, filenames = literal_eval(unzip)
    sound_files = []
    track_settings = None
    with open(file_path, 'rb') as file:
        for each in range(len(filenames)):
            current_filename = filenames[each]
            current_length = unzip_ind[each]
            current = file.read(current_length)
            if current_filename[-4:] != '.txt':
                sound_files.append(current)
            else:
                track_settings = current.decode('utf-8-sig')
    if mode == 'pygame':
        import pygame
        pygame.mixer.init(frequency, sound_size, channel, buffer)
        pygame.mixer.set_num_channels(maxinum_channels)
        sound_files = [pygame.mixer.Sound(i) for i in sound_files]
    elif mode == 'pydub':
        from pydub import AudioSegment
        sound_files = [
            AudioSegment.from_file(
                BytesIO(sound_files[i]),
                format=filenames[i][filenames[i].rfind('.') + 1:])
            for i in range(len(sound_files))
        ]
    filenames = [i[:i.rfind('.')] for i in filenames if i[-4:] != '.txt']
    result = {filenames[i]: sound_files[i] for i in range(len(sound_files))}
    return result, track_settings
