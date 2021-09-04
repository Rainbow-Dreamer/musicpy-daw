with open('scripts/settings.py', encoding='utf-8-sig') as f:
    exec(f.read())


class esi:
    def __init__(self,
                 samples,
                 settings=None,
                 info=None,
                 others=None,
                 name_dict=None):
        self.samples = samples
        self.settings = settings
        self.info = info
        self.others = others
        self.name_dict = name_dict


class custom_channel:
    def __init__(self, channel):
        self.channel = channel


class pitch:
    def __init__(self, path, note='C5'):
        self.note = N(note) if type(note) == str else note
        audio_load = False
        if type(path) != AudioSegment:
            self.file_path = path
            current_format = path[path.rfind('.') + 1:]
            try:
                self.sounds = AudioSegment.from_file(path,
                                                     format=current_format)

            except:
                with open(path, 'rb') as f:
                    current_data = f.read()
                current_file = BytesIO(current_data)
                self.sounds = AudioSegment.from_file(current_file,
                                                     format=current_format)
                os.chdir(abs_path)
                self.sounds.export('scripts/temp.wav', format='wav')
                self.audio = librosa.load('scripts/temp.wav',
                                          sr=self.sounds.frame_rate)[0]
                os.remove('scripts/temp.wav')
                audio_load = True

        else:
            self.sounds = path
            self.file_path = None
        self.sample_rate = self.sounds.frame_rate
        self.channels = self.sounds.channels
        self.sample_width = self.sounds.sample_width
        if not audio_load:
            self.audio = librosa.load(path, sr=self.sample_rate)[0]

    def pitch_shift(self, semitones=1, mode='librosa'):
        if mode == 'librosa':
            data_shifted = librosa.effects.pitch_shift(self.audio,
                                                       self.sample_rate,
                                                       n_steps=semitones)
            current_sound = BytesIO()
            soundfile.write(current_sound,
                            data_shifted,
                            self.sample_rate,
                            format='wav')
            result = AudioSegment.from_wav(current_sound)
        elif mode == 'pydub':
            new_sample_rate = int(self.sample_rate * (2**(semitones / 12)))
            result = self.sounds._spawn(
                self.sounds.raw_data,
                overrides={'frame_rate': new_sample_rate})
        return result

    def np_array_to_audio(self, np, sample_rate):
        current_sound = BytesIO()
        soundfile.write(current_sound, np, sample_rate, format='wav')
        result = AudioSegment.from_wav(current_sound)
        return result

    def __add__(self, semitones):
        return self.pitch_shift(semitones)

    def __sub__(self, semitones):
        return self.pitch_shift(-semitones)

    def get(self, pitch):
        if type(pitch) != note:
            pitch = N(pitch)
        semitones = pitch.degree - self.note.degree
        return self + semitones

    def set_note(self, pitch):
        if type(pitch) != note:
            pitch = N(pitch)
        self.note = pitch

    def generate_dict(self,
                      start='A0',
                      end='C8',
                      mode='librosa',
                      pitch_shifter=False):
        if type(start) != note:
            start = N(start)
        if type(end) != note:
            end = N(end)
        degree = self.note.degree
        result = {}
        for i in range(end.degree - start.degree + 1):
            current_note_name = str(start + i)
            converting_note = root.language_dict['Converting note']
            if pitch_shifter:
                root.pitch_msg(f'{converting_note} {current_note_name} ...')
                root.pitch_shifter_window.msg.update()
            else:
                root.show_msg(f'{converting_note} {current_note_name} ...')
                root.msg.update()
            result[current_note_name] = self.pitch_shift(start.degree + i -
                                                         degree,
                                                         mode=mode)
        return result

    def export_sound_files(self,
                           path='.',
                           folder_name=None,
                           start='A0',
                           end='C8',
                           format='wav',
                           mode='librosa',
                           pitch_shifter=False):
        if folder_name is None:
            folder_name = self.language_dict['Untitled']
        os.chdir(path)
        if folder_name not in os.listdir():
            os.mkdir(folder_name)
        os.chdir(folder_name)
        current_dict = self.generate_dict(start,
                                          end,
                                          mode=mode,
                                          pitch_shifter=pitch_shifter)
        Exporting = root.language_dict['Exporting']
        for each in current_dict:
            if pitch_shifter:
                root.pitch_msg(f'{Exporting} {each} ...')
                root.pitch_shifter_window.msg.update()
            current_dict[each].export(f'{each}.{format}', format=format)
        os.chdir(abs_path)

    def __len__(self):
        return len(self.sounds)

    def play(self):
        play_audio(self)

    def stop(self):
        simpleaudio.stop_all()


class sound:
    def __init__(self, path):
        if type(path) != AudioSegment:
            self.sounds = AudioSegment.from_file(path,
                                                 format=path[path.rfind('.') +
                                                             1:])
            self.file_path = path
        else:
            self.sounds = path
            self.file_path = None
        self.sample_rate = self.sounds.frame_rate
        self.channels = self.sounds.channels
        self.sample_width = self.sounds.sample_width

    def __len__(self):
        return len(self.sounds)

    def play(self):
        play_audio(self)


def play_audio(audio):
    if type(audio) in [pitch, sound]:
        play_sound(audio.sounds)
    else:
        play_sound(audio)


def load(dic, path, volume):
    wavedict = {}
    files = os.listdir(path)
    filenames_only = [i[:i.rfind('.')] for i in files]
    current_path = path + '/'
    for i in dic:
        try:
            current_sound = pygame.mixer.Sound(
                current_path + files[filenames_only.index(dic[i])])
            wavedict[i] = current_sound
        except:
            wavedict[i] = None
        root.update()
    if volume != None:
        [wavedict[x].set_volume(volume) for x in wavedict if wavedict[x]]
    return wavedict


def load_audiosegments(current_dict, current_sound_path):
    current_sounds = {}
    current_sound_files = os.listdir(current_sound_path)
    current_sound_path += '/'
    current_sound_filenames = [i[:i.rfind('.')] for i in current_sound_files]
    for i in current_dict:
        current_sound_obj = current_dict[i]
        if current_sound_obj in current_sound_filenames:
            current_filename = current_sound_files[
                current_sound_filenames.index(current_sound_obj)]
            current_sound_obj_path = current_sound_path + current_filename
            current_sound_format = current_filename[current_filename.
                                                    rfind('.') + 1:]
            try:
                current_sounds[i] = AudioSegment.from_file(
                    current_sound_obj_path, format=current_sound_format)
            except:
                with open(current_sound_obj_path, 'rb') as f:
                    current_data = f.read()
                current_sounds[i] = AudioSegment.from_file(
                    BytesIO(current_data), format=current_sound_format)
        else:
            current_sounds[i] = None
        root.update()
    return current_sounds


def load_sounds(dic):
    wavedict = {i: (dic[i].get_raw() if dic[i] else None) for i in dic}
    return wavedict


def play_note(name):
    if name in note_sounds:
        current_sound = note_sounds[name]
        if current_sound:
            current_sound.play(maxtime=note_play_last_time)


def standardize_note(i):
    if i in standard_dict:
        i = standard_dict[i]
    return i


def velocity_to_db(vol):
    if vol == 0:
        return -100
    return math.log(vol / 127, 10) * 20


def percentage_to_db(vol):
    if vol == 0:
        return -100
    return math.log(abs(vol / 100), 10) * 20


def reverse(sound):
    sound.reverse_audio = True
    return sound


def offset(sound, bar):
    sound.offset = bar
    return sound


def fade_in(sound, duration):
    sound.fade_in_time = duration
    if not hasattr(sound, 'fade_out_time'):
        sound.fade_out_time = 0
    return sound


def fade_out(sound, duration):
    sound.fade_out_time = duration
    if not hasattr(sound, 'fade_in_time'):
        sound.fade_in_time = 0
    return sound


def fade(sound, fade_in, fade_out=0):
    sound.fade_in_time = fade_in
    sound.fade_out_time = fade_out
    return sound


def adsr(sound, attack, decay, sustain, release):
    sound.adsr = [attack, decay, sustain, release]
    return sound


ADSR = adsr


def check_reverse(sound):
    return hasattr(sound, 'reverse_audio')


def check_offset(sound):
    return hasattr(sound, 'offset')


def check_reverse_all(sound):
    types = type(sound)
    if types == chord:
        return check_reverse(sound) or any(check_reverse(i) for i in sound)
    elif types == piece:
        return check_reverse(sound) or any(
            check_reverse_all(i) for i in sound.tracks)


def check_offset_all(sound):
    types = type(sound)
    if types == chord:
        return check_offset(sound) or any(check_offset(i) for i in sound)
    elif types == piece:
        return check_offset(sound) or any(
            check_offset_all(i) for i in sound.tracks)


def check_pan_or_volume(sound):
    return type(sound) == piece and (any(i for i in sound.pan)
                                     or any(i for i in sound.volume))


def check_fade(sound):
    return hasattr(sound, 'fade_in_time') or hasattr(sound, 'fade_out_time')


def check_fade_all(sound):
    types = type(sound)
    if types == chord:
        return check_fade(sound) or any(check_fade(i) for i in sound)
    elif types == piece:
        return check_fade(sound) or any(
            check_fade_all(i) for i in sound.tracks)


def check_adsr(sound):
    return hasattr(sound, 'adsr')


def check_adsr_all(sound):
    types = type(sound)
    if types == chord:
        return check_adsr(sound) or any(check_adsr(i) for i in sound)
    elif types == piece:
        return check_adsr(sound) or any(
            check_adsr_all(i) for i in sound.tracks)


def has_audio(sound):
    types = type(sound)
    if types == chord:
        return any(type(i) == AudioSegment for i in sound.notes)
    elif types == piece:
        return any(has_audio(i) for i in sound.tracks)


def check_special(sound):
    return check_pan_or_volume(sound) or check_reverse_all(
        sound) or check_offset_all(sound) or check_fade_all(
            sound) or check_adsr_all(sound) or has_audio(sound)


def sine(freq=440, duration=1000, volume=0):
    if type(freq) in [str, note]:
        freq = get_freq(freq)
    return Sine(freq).to_audio_segment(duration, volume)


def triangle(freq=440, duration=1000, volume=0):
    if type(freq) in [str, note]:
        freq = get_freq(freq)
    return Triangle(freq).to_audio_segment(duration, volume)


def sawtooth(freq=440, duration=1000, volume=0):
    if type(freq) in [str, note]:
        freq = get_freq(freq)
    return Sawtooth(freq).to_audio_segment(duration, volume)


def square(freq=440, duration=1000, volume=0):
    if type(freq) in [str, note]:
        freq = get_freq(freq)
    return Square(freq).to_audio_segment(duration, volume)


def white_noise(duration=1000, volume=0):
    return WhiteNoise().to_audio_segment(duration, volume)


def pulse(freq=440, duty_cycle=0.5, duration=1000, volume=0):
    return Pulse(freq, duty_cycle).to_audio_segment(duration, volume)


def get_wave(sound, mode='sine', bpm=120, volume=None):
    # volume: percentage, from 0% to 100%
    temp = copy(sound)
    if volume is None:
        volume = [velocity_to_db(i) for i in temp.get_volume()]
    else:
        volume = [volume for i in range(len(temp))
                  ] if type(volume) != list else volume
        volume = [percentage_to_db(i) for i in volume]
    for i in range(1, len(temp) + 1):
        current_note = temp[i]
        if type(current_note) == note:
            if mode == 'sine':
                temp[i] = sine(
                    get_freq(current_note),
                    root.bar_to_real_time(current_note.duration, bpm, 1),
                    volume[i - 1])
            elif mode == 'triangle':
                temp[i] = triangle(
                    get_freq(current_note),
                    root.bar_to_real_time(current_note.duration, bpm, 1),
                    volume[i - 1])
            elif mode == 'sawtooth':
                temp[i] = sawtooth(
                    get_freq(current_note),
                    root.bar_to_real_time(current_note.duration, bpm, 1),
                    volume[i - 1])
            elif mode == 'square':
                temp[i] = square(
                    get_freq(current_note),
                    root.bar_to_real_time(current_note.duration, bpm, 1),
                    volume[i - 1])
            else:
                temp[i] = mode(
                    get_freq(current_note),
                    root.bar_to_real_time(current_note.duration, bpm, 1),
                    volume[i - 1])
    return temp


def audio(obj, channel_num=1):
    if channel_num > 0:
        channel_num -= 1
    if type(obj) == note:
        obj = chord([obj])
    elif type(obj) == track:
        obj = build(obj, bpm=obj.tempo, name=obj.name)
    result = root.export_audio_file(obj, action='get', channel_num=channel_num)
    return result


def audio_chord(audio_list, interval=0, duration=1 / 4, volume=127):
    result = chord([])
    result.notes = audio_list
    result.interval = interval if type(interval) == list else [
        interval for i in range(len(audio_list))
    ]
    durations = duration if type(duration) == list else [
        duration for i in range(len(audio_list))
    ]
    volumes = volume if type(volume) == list else [
        volume for i in range(len(audio_list))
    ]
    for i in range(len(result.notes)):
        result.notes[i].duration = durations[i]
        result.notes[i].volume = volumes[i]
    return result


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Easy Sampler")
        self.minsize(1100, 650)
        self.configure(bg=background_color)
        self.icon_image = PhotoImage(file='resources/images/easy_sampler.png')
        self.iconphoto(False, self.icon_image)

        self.default_load = False

        style = ttk.Style()
        style.theme_use('alt')
        style.configure('TButton',
                        font=(font_type, font_size),
                        background=button_background_color,
                        foreground=foreground_color,
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor='none')
        style.configure('TLabel',
                        background=background_color,
                        foreground=foreground_color,
                        font=(font_type, font_size))
        style.map('TButton',
                  background=[('active', active_background_color)],
                  foreground=[('active', active_foreground_color)])

        self.set_chord_button = ttk.Button(self,
                                           text='Play Notes',
                                           command=self.play_current_chord)
        self.set_chord_button.place(x=0, y=350)
        self.set_chord_text = Text(self,
                                   width=50,
                                   height=5,
                                   wrap='none',
                                   undo=True,
                                   autoseparators=True,
                                   maxundo=-1,
                                   font=(font_type, font_size))
        self.set_chord_text.place(x=100, y=350)

        self.set_musicpy_code_button = ttk.Button(
            self,
            text='Play Musicpy Code',
            command=self.play_current_musicpy_code)
        self.set_musicpy_code_button.place(x=0, y=450)
        self.set_musicpy_code_text = Text(self,
                                          width=115,
                                          height=10,
                                          wrap='none',
                                          undo=True,
                                          autoseparators=True,
                                          maxundo=-1,
                                          font=(font_type, font_size))
        self.set_musicpy_code_text.place(x=150, y=450, height=135)
        self.bind('<Control-r>', lambda e: self.play_current_musicpy_code())
        self.bind('<Control-e>', lambda e: self.stop_playing())
        self.bind('<Control-w>', lambda e: self.open_project_file())
        self.bind('<Control-s>', lambda e: self.save_as_project_file())
        self.bind('<Control-b>', lambda e: self.save_as_project_file(new=True))
        self.bind('<Control-f>', lambda e: self.load_musicpy_code())
        self.bind('<Control-d>', lambda e: self.save_current_musicpy_code())
        self.bind('<Control-g>', lambda e: self.open_export_menu())
        self.bind('<Control-h>', lambda e: self.load_midi_file_func())
        self.bind('<Control-q>', lambda e: self.destroy())
        self.set_musicpy_code_text.bind("<Button-3>",
                                        lambda e: self.rightKey(e))

        self.stop_button = ttk.Button(self,
                                      text='Stop',
                                      command=self.stop_playing)
        self.stop_button.place(x=0, y=500)

        self.change_current_bpm_button = ttk.Button(
            self, text='Change BPM', command=self.change_current_bpm)
        self.change_current_bpm_button.place(x=0, y=300)
        self.change_current_bpm_entry = ttk.Entry(self,
                                                  width=10,
                                                  font=(font_type, font_size))
        self.change_current_bpm_entry.insert(END, '120')
        self.change_current_bpm_entry.place(x=100, y=300)
        self.current_bpm = 120
        self.current_playing = []

        self.msg = ttk.Label(self, text='')
        self.msg.place(x=130, y=600)

        self.change_current_sound_path_button = ttk.Button(
            self,
            text='Change Sound Path',
            command=self.change_current_sound_path)
        self.change_current_sound_path_button.place(x=550, y=300)

        self.load_midi_file_button = ttk.Button(
            self, text='Import MIDI File', command=self.load_midi_file_func)
        self.load_midi_file_button.place(x=500, y=350)
        self.load_midi_file_entry = ttk.Entry(self,
                                              width=50,
                                              font=(font_type, font_size))
        self.load_midi_file_entry.insert(END, '')
        self.load_midi_file_entry.bind(
            '<Return>', lambda e: self.load_midi_file_func(mode=1))
        self.load_midi_file_entry.place(x=630, y=350)

        self.change_settings_button = ttk.Button(
            self, text='Change Settings', command=self.open_change_settings)
        self.change_settings_button.place(x=0, y=600)
        self.open_settings = False

        self.choose_channels_bar = Scrollbar(self)
        self.choose_channels_bar.place(x=227, y=215, height=125, anchor=CENTER)
        self.choose_channels = Listbox(
            self,
            yscrollcommand=self.choose_channels_bar.set,
            height=7,
            exportselection=False,
            font=(font_type, font_size))
        self.choose_channels.config(activestyle='none')
        self.choose_channels.bind('<<ListboxSelect>>',
                                  lambda e: self.show_current_channel())
        self.choose_channels.bind('<z>', lambda e: self.add_new_channel())
        self.choose_channels.bind('<x>', lambda e: self.delete_channel())
        self.choose_channels.bind('<c>',
                                  lambda e: self.clear_current_channel())
        self.choose_channels.bind('<v>', lambda e: self.clear_all_channels())
        self.choose_channels.bind('<Button-3>',
                                  lambda e: self.cancel_choose_channels())
        self.choose_channels.place(x=0, y=152, width=220, height=125)
        self.choose_channels_bar.config(command=self.choose_channels.yview)

        self.current_channel_name_label = ttk.Label(self, text='Channel Name')
        self.current_channel_name_entry = ttk.Entry(self,
                                                    width=30,
                                                    font=(font_type,
                                                          font_size))
        self.current_channel_name_label.place(x=250, y=150)
        self.current_channel_name_entry.place(x=350, y=150)
        self.current_channel_name_entry.bind(
            '<Return>', lambda e: self.change_current_channel_name())
        self.current_channel_sound_modules_label = ttk.Label(
            self, text='Channel Sound Modules')
        self.current_channel_sound_modules_entry = ttk.Entry(self,
                                                             width=80,
                                                             font=(font_type,
                                                                   font_size))
        self.current_channel_sound_modules_entry.bind(
            '<Return>', lambda e: self.change_current_sound_path_func())
        self.current_channel_sound_modules_label.place(x=250, y=200)
        self.current_channel_sound_modules_entry.place(x=410, y=200)

        self.change_current_channel_name_button = ttk.Button(
            self,
            text='Change Channel Name',
            command=self.change_current_channel_name)
        self.change_current_channel_name_button.place(x=550, y=250)

        self.add_new_channel_button = ttk.Button(self,
                                                 text='Add New Channel',
                                                 command=self.add_new_channel)
        self.add_new_channel_button.place(x=250, y=250)

        self.delete_new_channel_button = ttk.Button(
            self, text='Delete Channel', command=self.delete_channel)
        self.delete_new_channel_button.place(x=400, y=250)

        self.clear_all_channels_button = ttk.Button(
            self, text='Clear All Channels', command=self.clear_all_channels)
        self.clear_all_channels_button.place(x=250, y=300)

        self.clear_channel_button = ttk.Button(
            self, text='Clear Channel', command=self.clear_current_channel)
        self.clear_channel_button.place(x=400, y=300)

        self.change_channel_dict_button = ttk.Button(
            self, text='Change Channel Dict', command=self.change_channel_dict)
        self.change_channel_dict_button.place(x=700, y=250)

        self.load_channel_settings_button = ttk.Button(
            self,
            text='Load Channel Settings',
            command=self.load_channel_settings)
        self.load_channel_settings_button.place(x=700, y=300)

        self.configure_sf2_button = ttk.Button(self,
                                               text='Configure Soundfonts',
                                               command=self.configure_sf2_file)
        self.configure_sf2_button.place(x=870, y=300)

        self.load_sf2_button = ttk.Button(self,
                                          text='Load Soundfonts',
                                          command=self.load_sf2_file)
        self.load_sf2_button.place(x=870, y=250)

        self.piece_playing = []

        self.open_change_channel_dict = False
        self.open_pitch_shifter_window = False
        self.open_configure_sf2_file = False

        self.export_button = ttk.Button(self,
                                        text='Export',
                                        command=self.open_export_menu)
        self.export_button.place(x=500, y=400)

        self.current_project_name = ttk.Label(self, text='new.esp')
        self.current_project_name.place(x=0, y=30)
        self.project_name = 'new.esp'
        self.opening_project_name = None

        self.load_musicpy_code_button = ttk.Button(
            self, text='Import musicpy code', command=self.load_musicpy_code)
        self.load_musicpy_code_button.place(x=0, y=550)

        try:
            with open('browse memory.txt', encoding='utf-8-sig') as f:
                self.last_place = f.read()
        except:
            self.last_place = "."

        self.file_top = ttk.Button(
            self,
            text='File',
            command=lambda: self.file_top_make_menu(mode='file'))

        self.file_top_options = ttk.Button(
            self,
            text='Options',
            command=lambda: self.file_top_make_menu(mode='options'))

        self.file_top_tools = ttk.Button(
            self,
            text='Tools',
            command=lambda: self.file_top_make_menu(mode='tools'))

        self.change_language(default_language)

        self.initialize_menu()

        self.choose_channels.insert(END, self.language_dict['init'][0])
        self.channel_names = [self.language_dict['init'][0]]
        self.channel_sound_modules_name = [sound_path]
        self.channel_num = 1
        self.channel_list_focus = True

        self.after(10, self.initialize)

    def initialize_menu(self):
        self.menubar = Menu(self,
                            tearoff=False,
                            bg=background_color,
                            activebackground=active_background_color,
                            activeforeground=active_foreground_color,
                            disabledforeground=disabled_foreground_color,
                            font=(font_type, font_size))
        self.menubar.add_command(label=self.language_dict['right key'][0],
                                 command=self.cut,
                                 foreground=foreground_color)
        self.menubar.add_command(label=self.language_dict['right key'][1],
                                 command=self.copy,
                                 foreground=foreground_color)
        self.menubar.add_command(label=self.language_dict['right key'][2],
                                 command=self.paste,
                                 foreground=foreground_color)
        self.menubar.add_command(label=self.language_dict['right key'][3],
                                 command=self.choose_all,
                                 foreground=foreground_color)
        self.menubar.add_command(label=self.language_dict['right key'][4],
                                 command=self.inputs_undo,
                                 foreground=foreground_color)
        self.menubar.add_command(label=self.language_dict['right key'][5],
                                 command=self.inputs_redo,
                                 foreground=foreground_color)
        self.menubar.add_command(label=self.language_dict['right key'][6],
                                 command=self.save_current_musicpy_code,
                                 foreground=foreground_color)
        self.menubar.add_command(label=self.language_dict['right key'][7],
                                 command=self.load_musicpy_code,
                                 foreground=foreground_color)

        self.export_menubar = Menu(
            self,
            tearoff=False,
            bg=background_color,
            activebackground=active_background_color,
            activeforeground=active_foreground_color,
            disabledforeground=disabled_foreground_color,
            font=(font_type, font_size))

        self.export_audio_file_menubar = Menu(
            self,
            tearoff=False,
            bg=background_color,
            activebackground=active_background_color,
            activeforeground=active_foreground_color,
            disabledforeground=disabled_foreground_color,
            font=(font_type, font_size))

        self.menubar.add_cascade(label=self.language_dict['right key'][8],
                                 menu=self.export_menubar,
                                 foreground=foreground_color)

        self.menubar.add_command(
            label=self.language_dict['right key'][9],
            command=lambda: self.play_selected_musicpy_code(),
            foreground=foreground_color)

        self.menubar.add_command(label=self.language_dict['right key'][10],
                                 command=lambda: self.play_selected_audio(),
                                 foreground=foreground_color)

        self.export_audio_file_menubar.add_command(
            label=self.language_dict['export audio formats'][0],
            command=lambda: self.export_audio_file(mode='wav'))
        self.export_audio_file_menubar.add_command(
            label=self.language_dict['export audio formats'][1],
            command=lambda: self.export_audio_file(mode='mp3'))
        self.export_audio_file_menubar.add_command(
            label=self.language_dict['export audio formats'][2],
            command=lambda: self.export_audio_file(mode='ogg'))
        self.export_audio_file_menubar.add_command(
            label=self.language_dict['export audio formats'][3],
            command=lambda: self.export_audio_file(mode='other'))

        self.export_menubar.add_cascade(
            label=self.language_dict['export audio formats'][4],
            menu=self.export_audio_file_menubar)
        self.export_menubar.add_command(
            label=self.language_dict['export audio formats'][5],
            command=self.export_midi_file)

        self.file_menu = Menu(self,
                              tearoff=False,
                              bg=background_color,
                              activebackground=active_background_color,
                              activeforeground=active_foreground_color,
                              disabledforeground=disabled_foreground_color,
                              font=(font_type, font_size))
        self.file_menu.add_command(label=self.language_dict['file'][0],
                                   command=self.open_project_file)
        self.file_menu.add_command(label=self.language_dict['file'][1],
                                   command=self.save_as_project_file)
        self.file_menu.add_command(
            label=self.language_dict['file'][6],
            command=lambda: self.save_as_project_file(new=True))
        self.file_menu.add_command(label=self.language_dict['file'][2],
                                   command=self.load_midi_file_func)
        self.file_menu.add_command(label=self.language_dict['file'][3],
                                   command=self.save_current_musicpy_code)
        self.file_menu.add_command(label=self.language_dict['file'][4],
                                   command=self.load_musicpy_code)
        self.file_menu.add_cascade(label=self.language_dict['file'][5],
                                   menu=self.export_menubar)
        self.file_top.place(x=0, y=0)

        self.options_menu = Menu(self,
                                 tearoff=False,
                                 bg=background_color,
                                 activebackground=active_background_color,
                                 activeforeground=active_foreground_color,
                                 disabledforeground=disabled_foreground_color,
                                 font=(font_type, font_size))
        self.options_menu.add_command(label=self.language_dict['option'][0],
                                      command=self.open_change_settings)
        self.options_menu.add_command(label=self.language_dict['option'][1],
                                      command=self.change_channel_dict)

        self.change_languages_menu = Menu(
            self,
            tearoff=False,
            bg=background_color,
            activebackground=active_background_color,
            activeforeground=active_foreground_color,
            disabledforeground=disabled_foreground_color,
            font=(font_type, font_size))

        os.chdir(abs_path)
        current_languages = [
            i[:i.rfind('.')] for i in os.listdir('scripts/languages')
        ]
        for each in current_languages:
            self.change_languages_menu.add_command(
                label=each,
                command=lambda each=each: self.change_language(each, 1))

        self.options_menu.add_cascade(label=self.language_dict['option'][2],
                                      menu=self.change_languages_menu)

        self.file_top_options.place(x=82, y=0)

        self.tools_menu = Menu(self,
                               tearoff=False,
                               bg=background_color,
                               activebackground=active_background_color,
                               activeforeground=active_foreground_color,
                               disabledforeground=active_foreground_color,
                               font=(font_type, font_size))
        self.tools_menu.add_command(label=self.language_dict['tool'][0],
                                    command=self.make_esi_file)
        self.tools_menu.add_command(label=self.language_dict['tool'][1],
                                    command=self.load_esi_file)
        self.tools_menu.add_command(label=self.language_dict['tool'][2],
                                    command=self.unzip_esi_file)
        self.tools_menu.add_command(label=self.language_dict['tool'][3],
                                    command=self.load_sound_as_pitch)
        self.tools_menu.add_command(label=self.language_dict['tool'][4],
                                    command=self.open_pitch_shifter)
        self.file_top_tools.place(x=164, y=0)

    def initialize(self):
        global note_sounds
        global note_sounds_path
        self.show_msg(self.language_dict['msg'][0])
        note_sounds = load(notedict, sound_path, global_volume)
        note_sounds_path = load_sounds(note_sounds)
        self.channel_sound_modules = [note_sounds]
        self.channel_sound_audiosegments = [
            load_audiosegments(notedict, sound_path)
        ]
        self.channel_note_sounds_path = [note_sounds_path]
        self.channel_dict = [notedict]
        self.show_msg(self.language_dict['msg'][1])
        self.default_load = True

    def show_msg(self, text=''):
        self.msg.configure(text=text)

    def pitch_msg(self, text=''):
        self.pitch_shifter_window.msg.configure(text=text)

    def change_language(self, language, mode=0):
        os.chdir(abs_path)
        try:
            with open(f'scripts/languages/{language}.py',
                      encoding='utf-8-sig') as f:
                data = f.read()
            current_language_dict, self.language_dict = eval(data)
            for each in current_language_dict:
                each.configure(text=current_language_dict[each])
            if mode == 1:
                self.reload_language()
        except Exception as e:
            print(str(e))
            current_msg = self.language_dict['msg'][2].split('|')
            self.show_msg(f'{current_msg[0]}{language}.py{current_msg[1]}')

    def reload_language(self):
        self.initialize_menu()
        self.show_msg('')

    def load_sound_as_pitch(self):
        file_path = filedialog.askopenfilename(
            initialdir=self.last_place,
            title=self.language_dict['title'][0],
            filetypes=((self.language_dict['title'][1], "*.*"), ))
        if file_path:
            memory = file_path[:file_path.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
            current_text = self.set_musicpy_code_text.get('1.0', 'end-1c')
            if current_text[current_text.rfind('\n') + 1:]:
                self.set_musicpy_code_text.insert(
                    END, f"\nnew_pitch = pitch('{file_path}', note = 'C5')\n")
            else:
                self.set_musicpy_code_text.insert(
                    END, f"new_pitch = pitch('{file_path}', note = 'C5')\n")
        else:
            return

    def open_pitch_shifter(self):
        if self.open_pitch_shifter_window:
            self.pitch_shifter_window.focus_set()
            return
        else:
            self.open_pitch_shifter_window = True
            self.pitch_shifter_window = Toplevel(self)
            self.pitch_shifter_window.iconphoto(False, self.icon_image)
            self.pitch_shifter_window.configure(bg=background_color)
            x = self.winfo_x()
            y = self.winfo_y()
            w = self.pitch_shifter_window.winfo_width()
            h = self.pitch_shifter_window.winfo_height()
            self.pitch_shifter_window.geometry("%dx%d+%d+%d" %
                                               (w, h, x + 200, y + 200))
            self.pitch_shifter_window.protocol("WM_DELETE_WINDOW",
                                               self.close_pitch_shifter_window)
            self.pitch_shifter_window.title(
                self.language_dict['pitch shifter'][0])
            self.pitch_shifter_window.minsize(700, 400)
            self.pitch_shifter_window.focus_set()

            self.pitch_shifter_window.load_current_pitch_label = ttk.Label(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][1])
            self.pitch_shifter_window.load_current_pitch_label.place(x=0, y=50)
            self.pitch_shifter_window.load_current_pitch_button = ttk.Button(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][2],
                command=self.pitch_shifter_load_pitch)
            self.pitch_shifter_window.load_current_pitch_button.place(x=0,
                                                                      y=100)
            self.pitch_shifter_window.msg = ttk.Label(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][3])
            self.pitch_shifter_window.msg.place(x=0, y=350)

            self.pitch_shifter_window.default_pitch_entry = ttk.Entry(
                self.pitch_shifter_window,
                width=10,
                font=(font_type, font_size))
            self.pitch_shifter_window.default_pitch_entry.insert(END, 'C5')
            self.pitch_shifter_window.default_pitch_entry.place(x=150, y=150)
            self.pitch_shifter_window.change_default_pitch_button = ttk.Button(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][4],
                command=self.pitch_shifter_change_default_pitch)
            self.pitch_shifter_window.change_default_pitch_button.place(x=0,
                                                                        y=150)
            self.pitch_shifter_window.change_pitch_button = ttk.Button(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][5],
                command=self.pitch_shifter_change_pitch)
            self.pitch_shifter_window.change_pitch_button.place(x=0, y=200)
            self.pitch_shifter_window.pitch_entry = ttk.Entry(
                self.pitch_shifter_window,
                width=10,
                font=(font_type, font_size))
            self.pitch_shifter_window.pitch_entry.insert(END, 'C5')
            self.pitch_shifter_window.pitch_entry.place(x=150, y=200)
            self.pitch_shifter_window.has_load = False

            self.pitch_shifter_window.play_button = ttk.Button(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][6],
                command=self.pitch_shifter_play)
            self.pitch_shifter_window.stop_button = ttk.Button(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][7],
                command=self.pitch_shifter_stop)
            self.pitch_shifter_window.play_button.place(x=250, y=150)
            self.pitch_shifter_window.stop_button.place(x=350, y=150)
            self.pitch_shifter_window.shifted_play_button = ttk.Button(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][6],
                command=self.pitch_shifter_play_shifted)
            self.pitch_shifter_window.shifted_stop_button = ttk.Button(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][7],
                command=self.pitch_shifter_stop_shifted)
            self.pitch_shifter_window.shifted_play_button.place(x=250, y=200)
            self.pitch_shifter_window.shifted_stop_button.place(x=350, y=200)
            self.pitch_shifter_playing = False
            self.pitch_shifter_shifted_playing = False
            self.current_pitch_note = N('C5')

            self.pitch_shifter_window.shifted_export_button = ttk.Button(
                self.pitch_shifter_window,
                text=self.language_dict['export'],
                command=self.pitch_shifter_export_shifted)
            self.pitch_shifter_window.shifted_export_button.place(x=450, y=200)
            self.pitch_shifter_window.export_sound_files_button = ttk.Button(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][8],
                command=self.pitch_shifter_export_sound_files)
            self.pitch_shifter_window.export_sound_files_button.place(x=0,
                                                                      y=250)

            self.pitch_shifter_window.export_sound_files_from = ttk.Entry(
                self.pitch_shifter_window,
                width=10,
                font=(font_type, font_size))
            self.pitch_shifter_window.export_sound_files_to = ttk.Entry(
                self.pitch_shifter_window,
                width=10,
                font=(font_type, font_size))
            self.pitch_shifter_window.export_sound_files_from.insert(END, 'A0')
            self.pitch_shifter_window.export_sound_files_to.insert(END, 'C8')
            self.pitch_shifter_window.export_sound_files_from.place(x=220,
                                                                    y=250)
            self.pitch_shifter_window.export_sound_files_to.place(x=345, y=250)
            self.pitch_shifter_window.export_sound_files_label = ttk.Label(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][9])
            self.pitch_shifter_window.export_sound_files_label.place(x=310,
                                                                     y=250)

            self.pitch_shifter_window.change_folder_name_button = ttk.Button(
                self.pitch_shifter_window,
                text=self.language_dict['pitch shifter'][10],
                command=self.pitch_shifter_change_folder_name)
            self.pitch_shifter_window.change_folder_name_button.place(x=0,
                                                                      y=300)
            self.pitch_shifter_window.folder_name = ttk.Entry(
                self.pitch_shifter_window,
                width=30,
                font=(font_type, font_size))
            self.pitch_shifter_window.folder_name.insert(
                END, self.language_dict['Untitled'])
            self.pitch_shifter_window.folder_name.place(x=280, y=300)
            self.pitch_shifter_folder_name = self.language_dict['Untitled']

    def pitch_shifter_change_folder_name(self):
        self.pitch_shifter_folder_name = self.pitch_shifter_window.folder_name.get(
        )
        self.pitch_msg(
            f'{self.language_dict["msg"][38]}{self.pitch_shifter_folder_name}')

    def pitch_shifter_export_sound_files(self):
        if not self.pitch_shifter_window.has_load:
            self.pitch_msg(self.language_dict["msg"][39])
            return
        try:
            start = N(self.pitch_shifter_window.export_sound_files_from.get())
            end = N(self.pitch_shifter_window.export_sound_files_to.get())
        except:
            self.pitch_msg(self.language_dict["msg"][40])
            return
        file_path = file_path = filedialog.askdirectory(
            parent=self.pitch_shifter_window,
            initialdir=self.last_place,
            title=self.language_dict['title'][2],
        )
        if not file_path:
            return
        self.current_pitch.export_sound_files(file_path,
                                              self.pitch_shifter_folder_name,
                                              start,
                                              end,
                                              pitch_shifter=True)
        self.pitch_msg(f'{self.language_dict["msg"][24]}{file_path}')

    def pitch_shifter_play(self):
        if self.pitch_shifter_window.has_load:
            if self.pitch_shifter_playing:
                self.pitch_shifter_stop()
            self.current_pitch_shifter_play = play_sound(
                self.current_pitch.sounds)
            self.pitch_shifter_playing = True

    def pitch_shifter_stop(self):
        if self.pitch_shifter_playing:
            self.current_pitch_shifter_play.stop()
            self.pitch_shifter_playing = False

    def pitch_shifter_play_shifted(self):
        if self.pitch_shifter_window.has_load:
            if self.pitch_shifter_shifted_playing:
                self.pitch_shifter_stop_shifted()
            self.current_pitch_shifter_shifted_play = play_sound(
                self.new_pitch)
            self.pitch_shifter_shifted_playing = True

    def pitch_shifter_stop_shifted(self):
        if self.pitch_shifter_shifted_playing:
            self.current_pitch_shifter_shifted_play.stop()
            self.pitch_shifter_shifted_playing = False

    def pitch_shifter_export_shifted(self):
        export_audio_file_menubar = Menu(
            self.pitch_shifter_window,
            tearoff=False,
            bg=background_color,
            activebackground=active_background_color,
            activeforeground=active_foreground_color,
            disabledforeground=disabled_foreground_color,
            font=(font_type, font_size))
        export_audio_file_menubar.add_command(
            label=self.language_dict['export audio formats'][0],
            command=lambda: self.export_pitch_audio_file(mode='wav'))
        export_audio_file_menubar.add_command(
            label=self.language_dict['export audio formats'][1],
            command=lambda: self.export_pitch_audio_file(mode='mp3'))
        export_audio_file_menubar.add_command(
            label=self.language_dict['export audio formats'][2],
            command=lambda: self.export_pitch_audio_file(mode='ogg'))
        export_audio_file_menubar.add_command(
            label=self.language_dict['export audio formats'][3],
            command=lambda: self.export_pitch_audio_file(mode='other'))

        export_audio_file_menubar.tk_popup(x=self.winfo_pointerx(),
                                           y=self.winfo_pointery())

    def export_pitch_audio_file(self, mode='wav'):
        if not self.pitch_shifter_window.has_load:
            self.pitch_msg(self.language_dict["msg"][39])
            return
        if mode == 'other':
            self.ask_other_format(mode=1)
            return
        filename = filedialog.asksaveasfilename(
            parent=self.pitch_shifter_window,
            initialdir=self.last_place,
            title=self.language_dict['title'][3],
            filetypes=((self.language_dict['title'][1], "*.*"), ),
            defaultextension=f".{mode}",
            initialfile=self.language_dict['untitled'])
        if not filename:
            return
        self.pitch_msg(self.language_dict["msg"][41])
        self.pitch_shifter_window.msg.update()
        self.new_pitch.export(filename, format=mode)
        self.pitch_msg(f'{self.language_dict["msg"][24]}{filename}')

    def pitch_shifter_read_other_format(self):
        current_format = self.ask_other_format_entry.get()
        self.ask_other_format_window.destroy()
        if current_format:
            self.export_pitch_audio_file(mode=current_format)

    def pitch_shifter_load_pitch(self):
        file_path = filedialog.askopenfilename(
            initialdir=self.last_place,
            parent=self.pitch_shifter_window,
            title=self.language_dict['title'][0],
            filetypes=((self.language_dict['title'][1], "*.*"), ))
        if file_path:
            self.pitch_msg(self.language_dict["msg"][42])
            self.pitch_shifter_window.msg.update()
            memory = file_path[:file_path.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
            self.pitch_shifter_window.load_current_pitch_label.configure(
                text=f'{self.language_dict["pitch shifter"][1]}{file_path}')

            try:
                default_pitch = self.pitch_shifter_window.default_pitch_entry.get(
                )
            except:
                default_pitch = 'C5'
            self.current_pitch = pitch(file_path, default_pitch)
            self.pitch_msg(self.language_dict["msg"][1])

            self.pitch_shifter_window.has_load = True
            self.new_pitch = self.current_pitch.sounds

    def pitch_shifter_change_default_pitch(self):
        if self.pitch_shifter_window.has_load:
            new_pitch = self.pitch_shifter_window.default_pitch_entry.get()
            try:
                self.current_pitch.set_note(new_pitch)
                self.pitch_msg(f'{self.language_dict["msg"][43]}{new_pitch}')
            except:
                self.pitch_msg(self.language_dict["msg"][37])

    def pitch_shifter_change_pitch(self):
        if not self.pitch_shifter_window.has_load:
            return

        try:
            new_pitch = N(self.pitch_shifter_window.pitch_entry.get())
            current_msg = self.language_dict["msg"][44].split('|')
            self.pitch_msg(f'{current_msg[0]}{new_pitch}{current_msg[1]}')
            self.pitch_shifter_window.msg.update()
            self.new_pitch = self.current_pitch + (
                new_pitch.degree - self.current_pitch.note.degree)
            self.pitch_msg(f'{self.language_dict["msg"][45]}{new_pitch}')
        except Exception as e:
            print(str(e))
            self.pitch_msg(self.language_dict["msg"][40])

    def close_pitch_shifter_window(self):
        self.pitch_shifter_window.destroy()
        self.open_pitch_shifter_window = False

    def play_selected_musicpy_code(self):
        if not self.default_load:
            return
        self.show_msg('')
        if not self.channel_sound_modules:
            self.show_msg(self.language_dict['msg'][3])
            return

        try:
            current_notes = self.set_musicpy_code_text.selection_get()
        except:
            return
        current_codes = self.set_musicpy_code_text.get('1.0', 'end-1c')
        current_channel_num = 0
        current_bpm = self.current_bpm
        if 'current_chord' in globals():
            del globals()['current_chord']
        try:
            lines = current_codes.split('\n')
            for k in range(len(lines)):
                each = lines[k]
                if each.startswith('play '):
                    lines[k] = 'current_chord = ' + each[5:]
            current_codes = '\n'.join(lines)
            exec(current_codes, globals(), globals())
        except:
            pass
        try:
            current_chord = eval(current_notes, globals(), globals())
            length = len(current_chord)
            if type(current_chord) == tuple and length > 1:
                if length == 2:
                    current_chord, current_bpm = current_chord
                elif length == 3:
                    current_chord, current_bpm, current_channel_num = current_chord
                    current_channel_num -= 1
                self.change_current_bpm_entry.delete(0, END)
                self.change_current_bpm_entry.insert(END, current_bpm)
                self.change_current_bpm(1)

        except Exception as e:
            print(str(e))
            self.show_msg(self.language_dict['msg'][4])
            return
        self.stop_playing()
        self.play_musicpy_sounds(current_chord, current_bpm,
                                 current_channel_num)

    def play_selected_audio(self):
        if not self.default_load:
            return
        self.show_msg('')
        try:
            current_notes = self.set_musicpy_code_text.selection_get()
        except:
            return
        current_codes = self.set_musicpy_code_text.get('1.0', 'end-1c')
        try:
            lines = current_codes.split('\n')
            for k in range(len(lines)):
                each = lines[k]
                if each.startswith('play '):
                    lines[k] = 'current_chord = ' + each[5:]
            current_codes = '\n'.join(lines)
            exec(current_codes, globals(), globals())
        except:
            pass
        try:
            current_audio = eval(current_notes, globals(), globals())
            simpleaudio.stop_all()
            play_audio(current_audio)
        except Exception as e:
            print(str(e))
            self.show_msg(self.language_dict['msg'][5])

    def make_esi_file(self):
        self.show_msg('')
        file_path = filedialog.askdirectory(
            initialdir=self.last_place,
            title=self.language_dict['title'][5],
        )
        if file_path:
            memory = file_path
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
        else:
            return
        export_path = filedialog.askdirectory(
            initialdir=self.last_place,
            title=self.language_dict['title'][6],
        )
        if not export_path:
            return
        abs_path = os.getcwd()
        os.chdir(export_path)
        filenames = os.listdir(file_path)
        name = os.path.basename(file_path)
        if not filenames:
            os.chdir(abs_path)
            self.show_msg(self.language_dict['msg'][6])
            return
        os.chdir(file_path)
        current_samples = {}
        current_settings = None
        for t in filenames:
            if os.path.splitext(t)[1] == '.txt':
                with open(t, encoding='utf-8-sig') as f:
                    current_settings = f.read()
            else:
                with open(t, 'rb') as f:
                    current_samples[t] = f.read()
        current_esi = esi(current_samples, current_settings)
        os.chdir(export_path)
        with open(f'{name}.esi', 'wb') as f:
            pickle.dump(current_esi, f)
        current_msg = self.language_dict['msg'][7]
        self.show_msg(f'{current_msg} {name}.esi')
        os.chdir(abs_path)
        return

    def load_esi_file(self):
        self.show_msg('')
        current_ind = self.choose_channels.index(ANCHOR)
        if current_ind >= self.channel_num or not self.channel_list_focus:
            self.show_msg(self.language_dict['msg'][8])
            return

        abs_path = os.getcwd()
        file_path = filedialog.askopenfilename(
            initialdir=self.last_place,
            title=self.language_dict['title'][7],
            filetypes=(("Easy Sampler Instrument", "*.esi"),
                       (self.language_dict['title'][1], "*.*")))
        if file_path:
            memory = file_path[:file_path.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
        else:
            return

        self.show_msg(
            f'{self.language_dict["msg"][9]}{os.path.basename(file_path)} ...')
        self.msg.update()
        with open(file_path, 'rb') as file:
            current_esi = pickle.load(file)
        channel_settings = current_esi.settings
        current_samples = current_esi.samples
        filenames = list(current_samples.keys())
        sound_files = [current_samples[i] for i in filenames]
        sound_files_pygame = []
        os.chdir('scripts')
        for each in sound_files:
            with open('temp', 'wb') as f:
                f.write(each)
            sound_files_pygame.append(pygame.mixer.Sound('temp'))
        os.remove('temp')
        os.chdir('..')
        sound_files_audio = [
            AudioSegment.from_file(BytesIO(current_samples[i]),
                                   format=os.path.splitext(i)[1][1:])
            for i in filenames
        ]
        self.channel_dict[current_ind] = copy(notedict)
        if channel_settings is not None:
            self.load_channel_settings(text=channel_settings)
        current_dict = self.channel_dict[current_ind]
        filenames = [os.path.splitext(i)[0] for i in filenames]
        result_pygame = {
            filenames[i]: sound_files_pygame[i]
            for i in range(len(sound_files))
        }
        result_audio = {
            filenames[i]: sound_files_audio[i]
            for i in range(len(sound_files))
        }
        note_sounds = {
            i: (result_pygame[current_dict[i]]
                if current_dict[i] in result_pygame else None)
            for i in current_dict
        }
        self.channel_sound_modules[current_ind] = note_sounds

        self.channel_sound_audiosegments[current_ind] = {
            i: (result_audio[current_dict[i]]
                if current_dict[i] in result_audio else None)
            for i in current_dict
        }
        self.channel_note_sounds_path[current_ind] = load_sounds(note_sounds)
        self.show_msg(
            f'{self.language_dict["msg"][10]}{os.path.basename(file_path)}')

    def unzip_esi_file(self):
        self.show_msg('')
        abs_path = os.getcwd()
        file_path = filedialog.askopenfilename(
            initialdir=self.last_place,
            title=self.language_dict['title'][7],
            filetypes=(("Easy Sampler Instrument", "*.esi"),
                       (self.language_dict['title'][1], "*.*")))
        if file_path:
            memory = file_path[:file_path.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
        else:
            return

        export_path = filedialog.askdirectory(
            initialdir=self.last_place,
            title=self.language_dict['title'][9],
        )
        if export_path:
            os.chdir(export_path)
        folder_name = os.path.basename(file_path)
        folder_name = folder_name[:folder_name.rfind('.')]
        if folder_name not in os.listdir():
            os.mkdir(folder_name)
        with open(file_path, 'rb') as file:
            current_esi = pickle.load(file)
        os.chdir(folder_name)
        for each in current_esi.samples:
            with open(each, 'wb') as f:
                f.write(current_esi.samples[each])
        current_msg = self.language_dict["msg"][11].split('|')
        self.show_msg(
            f'{current_msg[0]}{os.path.basename(file_path)}{current_msg[1]}')
        os.chdir(abs_path)

    def load_musicpy_code(self):
        filename = filedialog.askopenfilename(
            initialdir=self.last_place,
            title=self.language_dict['title'][10],
            filetypes=((self.language_dict['title'][11], "*.txt"),
                       (self.language_dict['title'][1], "*.*")))
        if filename:
            memory = filename[:filename.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
            try:
                with open(filename, encoding='utf-8-sig',
                          errors='ignore') as f:
                    self.set_musicpy_code_text.delete('1.0', END)
                    self.set_musicpy_code_text.insert(END, f.read())
                    self.set_musicpy_code_text.see(INSERT)
            except:
                self.set_musicpy_code_text.delete('1.0', END)
                self.show_msg(self.language_dict["msg"][12])

    def cut(self):
        self.set_musicpy_code_text.event_generate("<<Cut>>")

    def copy(self):
        self.set_musicpy_code_text.event_generate("<<Copy>>")

    def paste(self):
        self.set_musicpy_code_text.event_generate('<<Paste>>')

    def choose_all(self):
        self.set_musicpy_code_text.tag_add(SEL, '1.0', END)
        self.set_musicpy_code_text.mark_set(INSERT, END)
        self.set_musicpy_code_text.see(INSERT)

    def inputs_undo(self):
        try:
            self.set_musicpy_code_text.edit_undo()
        except:
            pass

    def inputs_redo(self):
        try:
            self.set_musicpy_code_text.edit_redo()
        except:
            pass

    def rightKey(self, event):
        self.menubar.tk_popup(event.x_root, event.y_root)

    def open_project_file(self):
        if not self.default_load:
            return
        self.show_msg('')
        filename = filedialog.askopenfilename(
            initialdir=self.last_place,
            title=self.language_dict['title'][12],
            filetypes=(("Easy Sampler Project",
                        "*.esp"), (self.language_dict['title'][11], "*.txt"),
                       (self.language_dict['title'][1], "*.*")))
        if filename:
            memory = filename[:filename.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
            try:
                with open(filename, encoding='utf-8-sig',
                          errors='ignore') as f:
                    self.project_dict = literal_eval(f.read())
            except:
                self.set_musicpy_code_text.delete('1.0', END)
                self.show_msg(self.language_dict["msg"][13])
                return
        else:
            return
        self.clear_all_channels(1)
        self.channel_num = self.project_dict['channel_num']
        self.init_channels(self.channel_num)
        self.channel_names = self.project_dict['channel_names']
        self.channel_sound_modules_name = self.project_dict[
            'channel_sound_modules_name']
        self.channel_dict = self.project_dict['channel_dict']
        self.current_bpm = self.project_dict['current_bpm']
        self.change_current_bpm_entry.delete(0, END)
        self.change_current_bpm_entry.insert(END, self.current_bpm)
        self.load_midi_file_entry.delete(0, END)
        self.load_midi_file_entry.insert(
            END, self.project_dict['current_midi_file'])
        self.set_musicpy_code_text.delete('1.0', END)
        self.set_musicpy_code_text.insert(
            END, self.project_dict['current_musicpy_code'])
        self.current_channel_name_label.focus_set()
        for current_ind in range(self.channel_num):
            self.choose_channels.delete(current_ind)
            self.choose_channels.insert(current_ind,
                                        self.channel_names[current_ind])
        for i in range(self.channel_num):
            self.reload_channel_sounds(i)
        self.current_channel_sound_modules_entry.delete(0, END)
        self.choose_channels.selection_clear(0, END)
        current_project_name = os.path.basename(filename)
        self.current_project_name.configure(text=current_project_name)
        self.project_name = current_project_name
        self.opening_project_name = filename
        current_soundfonts = self.project_dict['soundfont']
        for each in current_soundfonts:
            self.channel_sound_modules[each].program_select(
                *current_soundfonts[each])
        self.show_msg(self.language_dict["msg"][14])

    def save_as_project_file(self, new=False):
        if not self.default_load:
            return
        self.show_msg('')
        self.project_dict = {}
        self.project_dict['channel_num'] = self.channel_num
        self.project_dict['channel_names'] = self.channel_names
        self.project_dict[
            'channel_sound_modules_name'] = self.channel_sound_modules_name
        self.project_dict['channel_dict'] = self.channel_dict
        self.project_dict['current_bpm'] = self.current_bpm
        self.project_dict['current_midi_file'] = self.load_midi_file_entry.get(
        )
        self.project_dict[
            'current_musicpy_code'] = self.set_musicpy_code_text.get(
                '1.0', 'end-1c')
        current_soundfonts = {
            i: self.channel_sound_modules[i]
            for i in range(len(self.channel_sound_modules))
        }
        self.project_dict['soundfont'] = {}
        for i in range(len(self.channel_sound_modules)):
            current_sound_modules = self.channel_sound_modules[i]
            if type(current_sound_modules) == rs.sf2_loader:
                current_info = [
                    current_sound_modules.current_track,
                    current_sound_modules.current_sfid,
                    current_sound_modules.current_bank_num,
                    current_sound_modules.current_preset_num
                ]
                self.project_dict['soundfont'][i] = current_info
        if not new and self.opening_project_name:
            with open(self.opening_project_name, 'w',
                      encoding='utf-8-sig') as f:
                f.write(str(self.project_dict))
            self.show_msg(self.language_dict["msg"][15])
            return
        filename = filedialog.asksaveasfilename(
            initialdir=self.last_place,
            title=self.language_dict['title'][13],
            filetypes=(("Easy Sampler Project",
                        "*.esp"), (self.language_dict['title'][11], "*.txt"),
                       (self.language_dict['title'][1], "*.*")),
            defaultextension=f".esp",
            initialfile=self.language_dict['untitled'])
        if filename:
            memory = filename[:filename.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(str(self.project_dict))
            self.show_msg(self.language_dict["msg"][15])
            current_project_name = os.path.basename(filename)
            self.current_project_name.configure(text=current_project_name)
            self.project_name = current_project_name
            self.opening_project_name = filename

    def save_current_musicpy_code(self):
        filename = filedialog.asksaveasfilename(
            initialdir=self.last_place,
            title=self.language_dict['title'][14],
            filetypes=((self.language_dict['title'][1], "*.*"), ),
            defaultextension=f".txt",
            initialfile=self.language_dict['untitled'])
        if filename:
            memory = filename[:filename.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(self.set_musicpy_code_text.get('1.0', 'end-1c'))

    def file_top_make_menu(self, mode='file'):
        if mode == 'file':
            self.file_menu.tk_popup(x=self.winfo_pointerx(),
                                    y=self.winfo_pointery())
        elif mode == 'options':
            self.options_menu.tk_popup(x=self.winfo_pointerx(),
                                       y=self.winfo_pointery())
        elif mode == 'tools':
            self.tools_menu.tk_popup(x=self.winfo_pointerx(),
                                     y=self.winfo_pointery())

    def load_channel_settings(self, text=None):
        current_ind = self.choose_channels.index(ANCHOR)
        if current_ind >= self.channel_num or not self.channel_list_focus:
            return
        if text is None:
            filename = filedialog.askopenfilename(
                initialdir=self.last_place,
                title=self.language_dict['title'][15],
                filetypes=((self.language_dict['title'][11], "*.txt"),
                           (self.language_dict['title'][1], "*.*")))
            if filename:
                memory = filename[:filename.rindex('/') + 1]
                with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                    f.write(memory)
                self.last_place = memory
                with open(filename, encoding='utf-8-sig') as f:
                    data = f.read()
            else:
                return
        else:
            data = text
        data = data.split('\n')
        current_dict = self.channel_dict[current_ind]
        for each in data:
            if ',' in each:
                current_key, current_value = each.split(',')
                current_dict[current_key] = current_value
        self.current_channel_dict_num = current_ind
        if text is None:
            self.reload_channel_sounds()
            current_msg = self.language_dict["msg"][16].split('|')
            self.show_msg(
                f'{current_msg[0]}{os.path.basename(filename)}{current_msg[1]}{current_ind+1}'
            )

    def load_sf2_file(self, mode=0, current_ind=None, sound_path=None):
        if current_ind is None:
            current_ind = self.choose_channels.index(ANCHOR)
        if current_ind < self.channel_num and self.channel_list_focus:
            self.show_msg('')
            if sound_path is not None:
                self.channel_sound_modules[current_ind] = rs.sf2_loader(
                    sound_path)
                self.channel_sound_modules_name[current_ind] = sound_path
            else:
                if mode == 0:
                    filename = filedialog.askopenfilename(
                        initialdir=self.last_place,
                        title=self.language_dict['title'][19],
                        filetypes=(("Soundfont", "*.sf2"),
                                   (self.language_dict['title'][1], "*.*")))
                else:
                    filename = self.current_channel_sound_modules_entry.get()
                if filename:
                    memory = filename[:filename.rindex('/') + 1]
                    with open('browse memory.txt', 'w',
                              encoding='utf-8-sig') as f:
                        f.write(memory)
                    self.last_place = memory
                    try:
                        self.show_msg(
                            f'{self.language_dict["msg"][33]}{self.channel_names[current_ind]} ...'
                        )
                        self.msg.update()
                        sound_path = filename
                        self.channel_sound_modules[
                            current_ind] = rs.sf2_loader(sound_path)
                        self.channel_note_sounds_path[current_ind] = None
                        self.channel_sound_modules_name[
                            current_ind] = sound_path
                        self.channel_sound_audiosegments[current_ind] = None

                        self.current_channel_sound_modules_entry.delete(0, END)
                        self.current_channel_sound_modules_entry.insert(
                            END, sound_path)
                        current_msg = self.language_dict["msg"][29].split('|')
                        self.show_msg(
                            f'{current_msg[0]}{self.channel_names[current_ind]}{current_msg[1]}'
                        )
                        self.choose_channels.see(current_ind)
                        self.choose_channels.selection_anchor(current_ind)
                        self.choose_channels.selection_set(current_ind)
                    except Exception as e:
                        print(str(e))
                        self.show_msg(self.language_dict["msg"][30])
        else:
            self.show_msg(self.language_dict['msg'][8])

    def configure_sf2_file(self):
        if self.open_configure_sf2_file:
            self.configure_sf2_file_window.focus_set()
            return
        else:
            current_ind = self.choose_channels.index(ANCHOR)
            if current_ind < self.channel_num and self.channel_list_focus:
                current_sf2 = self.channel_sound_modules[current_ind]
                if type(current_sf2) != rs.sf2_loader:
                    return
                self.open_configure_sf2_file = True
                self.configure_sf2_file_window = Toplevel(self)
                self.configure_sf2_file_window.iconphoto(
                    False, self.icon_image)
                self.configure_sf2_file_window.configure(bg=background_color)
                x = self.winfo_x()
                y = self.winfo_y()
                w = self.configure_sf2_file_window.winfo_width()
                h = self.configure_sf2_file_window.winfo_height()
                self.configure_sf2_file_window.geometry(
                    "%dx%d+%d+%d" % (w, h, x + 200, y + 200))
                self.configure_sf2_file_window.protocol(
                    "WM_DELETE_WINDOW", self.close_configure_sf2_file_window)
                self.configure_sf2_file_window.title(
                    self.language_dict['configure_sf2'][0])
                self.configure_sf2_file_window.minsize(500, 300)
                self.configure_sf2_file_window.focus_set()
                self.preset_configs_bar = Scrollbar(
                    self.configure_sf2_file_window)
                self.preset_configs_bar.place(x=167,
                                              y=90,
                                              height=185,
                                              anchor=CENTER)
                self.preset_configs = Listbox(
                    self.configure_sf2_file_window,
                    yscrollcommand=self.preset_configs_bar.set,
                    exportselection=False,
                    font=(font_type, font_size))
                self.preset_configs.config(activestyle='none')
                self.preset_configs.bind(
                    '<<ListboxSelect>>',
                    lambda e: self.show_current_preset_configs())
                self.preset_configs_bar.config(
                    command=self.preset_configs.yview)
                self.preset_configs.place(x=0, y=0, height=185, width=160)
                try:
                    self.current_preset, self.current_preset_ind = current_sf2.get_all_instrument_names(
                        get_ind=True)
                except:
                    self.current_preset, self.current_preset_ind = [], []
                for each in self.current_preset:
                    self.preset_configs.insert(END, each)
                self.current_bank_num = ttk.Label(
                    self.configure_sf2_file_window,
                    text=self.language_dict['configure_sf2'][1])
                self.current_bank_num.place(x=200, y=0)
                self.current_bank_num_entry = ttk.Entry(
                    self.configure_sf2_file_window,
                    width=10,
                    font=(font_type, font_size))
                self.current_bank_num_entry.insert(
                    END, str(current_sf2.current_bank_num))
                self.current_bank_num_entry.place(x=300, y=0)
                self.current_preset_num = ttk.Label(
                    self.configure_sf2_file_window,
                    text=self.language_dict['configure_sf2'][2])
                self.current_preset_num.place(x=200, y=50)
                self.current_preset_num_entry = ttk.Entry(
                    self.configure_sf2_file_window,
                    width=10,
                    font=(font_type, font_size))
                self.current_preset_num_entry.insert(
                    END, str(current_sf2.current_preset_num + 1))
                self.current_preset_num_entry.place(x=300, y=50)
                if current_sf2.current_preset_num in self.current_preset_ind:
                    current_preset_ind = self.current_preset_ind.index(
                        current_sf2.current_preset_num)
                    self.preset_configs.selection_clear(0, END)
                    self.preset_configs.selection_set(current_preset_ind)
                    self.preset_configs.see(current_preset_ind)
                self.change_current_bank_num_button = ttk.Button(
                    self.configure_sf2_file_window,
                    text=self.language_dict['configure_sf2'][3],
                    command=self.change_current_bank_num)
                self.change_current_preset_num_button = ttk.Button(
                    self.configure_sf2_file_window,
                    text=self.language_dict['configure_sf2'][4],
                    command=self.change_current_preset_num)
                self.listen_preset_button = ttk.Button(
                    self.configure_sf2_file_window,
                    text=self.language_dict['configure_sf2'][5],
                    command=self.listen_preset)
                self.change_current_bank_num_button.place(x=200, y=100)
                self.change_current_preset_num_button.place(x=320, y=100)
                self.listen_preset_button.place(x=200, y=150)
                self.preset_configs.bind(
                    '<Double-1>', lambda e: self.change_current_preset_num(1))

    def change_current_bank_num(self):
        current_ind = self.choose_channels.index(ANCHOR)
        current_bank_num = self.current_bank_num_entry.get()
        current_sf2 = self.channel_sound_modules[current_ind]
        if current_bank_num.isdigit():
            current_bank_num = int(current_bank_num)
            current_sf2.program_select(bank_num=current_bank_num,
                                       preset_num=0,
                                       correct=False)
            try:
                self.current_preset, self.current_preset_ind = current_sf2.get_all_instrument_names(
                    get_ind=True, mode=1)
            except:
                self.current_preset, self.current_preset_ind = [], []
            self.current_preset_num_entry.delete(0, END)
            self.current_preset_num_entry.insert(
                END, '1' if not self.current_preset_ind else
                str(self.current_preset_ind[0] + 1))
            self.preset_configs.delete(0, END)
            for each in self.current_preset:
                self.preset_configs.insert(END, each)
            self.preset_configs.selection_clear(0, END)
            self.preset_configs.selection_set(0)
            self.preset_configs.see(0)

    def change_current_preset_num(self, mode=0):
        current_ind = self.choose_channels.index(ANCHOR)
        if mode == 1:
            current_preset_num = str(self.current_preset_ind[
                self.preset_configs.curselection()[0]] + 1)
        else:
            current_preset_num = self.current_preset_num_entry.get()
        current_sf2 = self.channel_sound_modules[current_ind]
        if current_preset_num.isdigit():
            current_preset_num = int(current_preset_num)
            current_sf2.program_select(preset_num=current_preset_num - 1)
            if current_preset_num - 1 in self.current_preset_ind:
                self.preset_configs.selection_clear(0, END)
                current_preset_ind = self.current_preset_ind.index(
                    current_preset_num - 1)
                self.preset_configs.selection_set(current_preset_ind)
                self.preset_configs.see(current_preset_ind)

    def listen_preset(self):
        current_ind = self.choose_channels.index(ANCHOR)
        current_sf2 = self.channel_sound_modules[current_ind]
        current_sf2.play_note('C5')

    def show_current_preset_configs(self):
        current_ind = self.preset_configs.index(ANCHOR)
        self.current_preset_num_entry.delete(0, END)
        self.current_preset_num_entry.insert(
            END, str(self.current_preset_ind[current_ind] + 1))

    def open_export_menu(self):
        self.export_menubar.tk_popup(x=self.winfo_pointerx(),
                                     y=self.winfo_pointery())

    def ask_other_format(self, mode=0):
        self.ask_other_format_window = Toplevel(self)
        self.ask_other_format_window.iconphoto(False, self.icon_image)
        self.ask_other_format_window.configure(bg=background_color)
        self.ask_other_format_window.minsize(470, 200)
        x = self.winfo_x()
        y = self.winfo_y()
        w = self.ask_other_format_window.winfo_width()
        h = self.ask_other_format_window.winfo_height()
        self.ask_other_format_window.geometry("%dx%d+%d+%d" %
                                              (w, h, x + 200, y + 200))
        self.ask_other_format_window.title(
            self.language_dict['ask other format'][0])
        x = self.winfo_x()
        y = self.winfo_y()
        self.ask_other_format_window.geometry("+%d+%d" % (x + 100, y + 140))
        self.ask_other_format_label = ttk.Label(
            self.ask_other_format_window,
            text=self.language_dict['ask other format'][1])
        self.ask_other_format_label.place(x=0, y=50)
        self.ask_other_format_entry = ttk.Entry(self.ask_other_format_window,
                                                width=20,
                                                font=(font_type, font_size))
        self.ask_other_format_entry.place(x=100, y=100)
        self.ask_other_format_ok_button = ttk.Button(
            self.ask_other_format_window,
            text=self.language_dict['ask other format'][2],
            command=self.read_other_format
            if mode == 0 else self.pitch_shifter_read_other_format)
        self.ask_other_format_cancel_button = ttk.Button(
            self.ask_other_format_window,
            text=self.language_dict['ask other format'][3],
            command=self.ask_other_format_window.destroy)
        self.ask_other_format_ok_button.place(x=60, y=150)
        self.ask_other_format_cancel_button.place(x=200, y=150)

    def read_other_format(self):
        current_format = self.ask_other_format_entry.get()
        self.ask_other_format_window.destroy()
        if current_format:
            self.export_audio_file(mode=current_format)

    def export_audio_file(self,
                          obj=None,
                          mode='wav',
                          action='export',
                          channel_num=0):
        if mode == 'other':
            self.ask_other_format()
            return
        self.show_msg('')
        if not self.channel_sound_modules:
            if action == 'export':
                self.show_msg(self.language_dict["msg"][17])
                return
            elif action == 'play':
                self.show_msg(self.language_dict["msg"][18])
                return
            elif action == 'get':
                self.show_msg(self.language_dict["msg"][19])
                return
        if action == 'export':
            filename = filedialog.asksaveasfilename(
                initialdir=self.last_place,
                title=self.language_dict['title'][3],
                filetypes=((self.language_dict['title'][1], "*.*"), ),
                defaultextension=f".{mode}",
                initialfile=self.language_dict['untitled'])
            if not filename:
                return
        if action == 'get':
            result = obj
            if type(result) == chord:
                result = ['chord', result, channel_num]
            elif type(result) == piece:
                result = ['piece', result]
            else:
                self.show_msg(self.language_dict["msg"][20])
                return
        else:
            result = self.get_current_musicpy_chords()
        if result is None:
            return
        if action == 'export':
            self.show_msg(f'{self.language_dict["msg"][21]}{filename}')
        self.msg.update()
        types = result[0]
        current_chord = result[1]
        self.stop_playing()

        if types == 'chord':
            current_channel_num = result[2]
            current_bpm = self.current_bpm
            for each in current_chord:
                if type(each) == AudioSegment:
                    each.duration = self.real_time_to_bar(
                        len(each), current_bpm)
                    each.volume = 127

            current_sound_modules = self.channel_sound_modules[
                current_channel_num]
            if type(current_sound_modules) == rs.sf2_loader:
                if action == 'export':
                    current_msg = self.language_dict["msg"][27].split('|')
                    self.show_msg(
                        f'{current_msg[0]} {self.language_dict["channel"]} {current_channel_num + 1} (soundfont)'
                    )
                    self.msg.update()
                for k in current_chord.notes:
                    if check_reverse(k) or check_fade(k) or check_offset(
                            k) or check_adsr(k):
                        rs.convert_effect(k, add=True)
                silent_audio = current_sound_modules.export_chord(
                    current_chord,
                    bpm=current_bpm,
                    get_audio=True,
                    other_effects=rs.convert_effect(current_chord))
            else:
                apply_fadeout_obj = self.apply_fadeout(current_chord,
                                                       current_bpm)
                whole_duration = apply_fadeout_obj.eval_time(
                    current_bpm, mode='number', audio_mode=1) * 1000
                current_start_times = 0
                silent_audio = AudioSegment.silent(duration=whole_duration)
                silent_audio = self.channel_to_audio(current_chord,
                                                     current_channel_num,
                                                     silent_audio,
                                                     current_bpm,
                                                     mode=action)
            try:
                if action == 'export':
                    silent_audio.export(filename, format=mode)
                elif action == 'play':
                    self.show_msg(self.language_dict["msg"][22])
                    play_audio(silent_audio)
                elif action == 'get':
                    return silent_audio
            except:
                if action == 'export':
                    self.show_msg(
                        f'{self.language_dict["error"]}{mode}{self.language_dict["msg"][23]}'
                    )
                return
        elif types == 'piece':
            current_name = current_chord.name
            current_bpm = current_chord.tempo
            current_start_times = current_chord.start_times
            current_pan = current_chord.pan
            current_volume = current_chord.volume
            current_tracks = current_chord.tracks
            current_channels = current_chord.channels if current_chord.channels else [
                i for i in range(len(current_chord))
            ]
            for i in range(len(current_chord.tracks)):
                each_channel = current_chord.tracks[i]
                for each in each_channel:
                    if type(each) == AudioSegment:
                        each.duration = self.real_time_to_bar(
                            len(each), current_bpm)
                        each.volume = 127
                current_chord.tracks[i] = each_channel
            apply_fadeout_obj = self.apply_fadeout(current_chord, current_bpm)
            whole_duration = apply_fadeout_obj.eval_time(
                current_bpm, mode='number', audio_mode=1) * 1000
            silent_audio = AudioSegment.silent(duration=whole_duration)
            for i in range(len(current_chord)):
                current_sound_modules = self.channel_sound_modules[
                    current_channels[i]]
                current_track = current_tracks[i]
                if type(current_sound_modules) == rs.sf2_loader:
                    if action == 'export':
                        current_msg = self.language_dict["msg"][27].split('|')
                        self.show_msg(
                            f'{current_msg[0]} {self.language_dict["channel"]} {current_channels[i] + 1} (soundfont)'
                        )
                        self.msg.update()

                    for k in current_track.notes:
                        if check_reverse(k) or check_fade(k) or check_offset(
                                k) or check_adsr(k):
                            rs.convert_effect(k, add=True)

                    current_instrument = current_chord.instruments_numbers[i]
                    # instrument of a track of the piece type could be preset_num or [preset_num, bank_num, (track), (sfid)]
                    if type(current_instrument) == int:
                        current_instrument = [
                            current_instrument - 1,
                            current_sound_modules.current_bank_num
                        ]
                    else:
                        current_instrument = [current_instrument[0] - 1
                                              ] + current_instrument[1:]

                    current_track2 = copy(current_sound_modules.current_track)
                    current_sfid = copy(current_sound_modules.current_sfid)
                    current_bank_num = copy(
                        current_sound_modules.current_bank_num)
                    current_preset_num = copy(
                        current_sound_modules.current_preset_num)

                    current_sound_modules.program_select(
                        track=(current_instrument[2]
                               if len(current_instrument) > 2 else None),
                        sfid=(current_instrument[3]
                              if len(current_instrument) > 3 else None),
                        bank_num=current_instrument[1],
                        preset_num=current_instrument[0])
                    silent_audio = silent_audio.overlay(
                        current_sound_modules.export_chord(
                            current_track,
                            bpm=current_bpm,
                            get_audio=True,
                            other_effects=rs.convert_effect(current_track),
                            pan=current_pan[i],
                            volume=current_volume[i]),
                        position=self.bar_to_real_time(current_start_times[i],
                                                       current_bpm, 1))
                    current_sound_modules.program_select(
                        current_track2, current_sfid, current_bank_num,
                        current_preset_num)
                else:
                    silent_audio = self.channel_to_audio(
                        current_tracks[i],
                        current_channels[i],
                        silent_audio,
                        current_bpm,
                        current_pan[i],
                        current_volume[i],
                        current_start_times[i],
                        mode=action)
            if check_adsr(current_chord):
                current_adsr = current_chord.adsr
                attack, decay, sustain, release = current_adsr
                change_db = percentage_to_db(sustain)
                result_db = silent_audio.dBFS + change_db
                if attack > 0:
                    silent_audio = silent_audio.fade_in(attack)
                if decay > 0:
                    silent_audio = silent_audio.fade(to_gain=result_db,
                                                     start=attack,
                                                     duration=decay)
                else:
                    silent_audio = silent_audio[:attack].append(
                        silent_audio[attack:] + change_db)
                if release > 0:
                    silent_audio = silent_audio.fade_out(release)
            if check_fade(current_chord):
                if current_chord.fade_in_time > 0:
                    silent_audio = silent_audio.fade_in(
                        current_chord.fade_in_time)
                if current_chord.fade_out_time > 0:
                    silent_audio = silent_audio.fade_out(
                        current_chord.fade_out_time)
            if check_offset(current_chord):
                silent_audio = silent_audio[self.bar_to_real_time(
                    current_chord.offset, current_bpm, 1):]
            if check_reverse(current_chord):
                silent_audio = silent_audio.reverse()
            try:
                if action == 'export':
                    silent_audio.export(filename, format=mode)
                elif action == 'play':
                    self.show_msg(self.language_dict["msg"][22])
                    play_audio(silent_audio)
                elif action == 'get':
                    return silent_audio
            except:
                if action == 'export':
                    self.show_msg(
                        f'{self.language_dict["error"]}{mode}{self.language_dict["msg"][23]}'
                    )
                return
        if action == 'export':
            self.show_msg(f'{self.language_dict["msg"][24]}{filename}')

    def apply_fadeout(self, obj, bpm):
        temp = copy(obj)
        if type(temp) == chord:
            for each in temp.notes:
                if type(each) != AudioSegment:
                    if export_fadeout_use_ratio:
                        current_fadeout_time = each.duration * export_audio_fadeout_time_ratio
                    else:
                        current_fadeout_time = self.real_time_to_bar(
                            export_audio_fadeout_time, bpm)
                    each.duration += current_fadeout_time
            return temp
        elif type(temp) == piece:
            temp.tracks = [
                self.apply_fadeout(each, bpm) for each in temp.tracks
            ]
            return temp

    def channel_to_audio(self,
                         current_chord,
                         current_channel_num=0,
                         silent_audio=None,
                         current_bpm=None,
                         current_pan=None,
                         current_volume=None,
                         current_start_time=0,
                         mode='export'):
        if len(self.channel_sound_modules) <= current_channel_num:
            self.show_msg(
                f'{self.language_dict["msg"][25]}{current_channel_num+1}')
            return
        if not self.channel_sound_modules[current_channel_num]:
            self.show_msg(
                f'{self.language_dict["channel"]} {current_channel_num+1} {self.language_dict["msg"][26]}'
            )
            return

        apply_fadeout_obj = self.apply_fadeout(current_chord, current_bpm)
        whole_duration = apply_fadeout_obj.eval_time(
            current_bpm, mode='number', audio_mode=1) * 1000
        current_silent_audio = AudioSegment.silent(duration=whole_duration)
        current_intervals = current_chord.interval
        current_durations = current_chord.get_duration()
        current_volumes = current_chord.get_volume()
        current_dict = self.channel_dict[current_channel_num]
        current_sounds = self.channel_sound_audiosegments[current_channel_num]
        current_sound_path = self.channel_sound_modules_name[
            current_channel_num]
        current_start_time = self.bar_to_real_time(current_start_time,
                                                   current_bpm, 1)
        current_position = 0
        whole_length = len(current_chord)
        if show_convert_progress:
            counter = 1
        current_msg = self.language_dict["msg"][27].split('|')
        for i in range(whole_length):
            if mode == 'export' and show_convert_progress:
                self.show_msg(
                    f'{current_msg[0]}{round((counter / whole_length) * 100, 3):.3f}{current_msg[1]}{current_channel_num + 1}'
                )
                self.msg.update()
                counter += 1
            each = current_chord.notes[i]
            current_type = type(each)
            if current_type == note or current_type == AudioSegment:
                interval = self.bar_to_real_time(current_intervals[i],
                                                 current_bpm, 1)
                duration = self.bar_to_real_time(
                    current_durations[i], current_bpm,
                    1) if type(each) != AudioSegment else len(each)
                volume = velocity_to_db(current_volumes[i])
                current_offset = 0
                if check_offset(each):
                    current_offset = self.bar_to_real_time(
                        each.offset, current_bpm, 1)
                current_fadeout_time = int(
                    duration * export_audio_fadeout_time_ratio
                ) if export_fadeout_use_ratio else int(
                    export_audio_fadeout_time)
                if type(each) == AudioSegment:
                    current_sound = each[current_offset:duration]
                else:
                    each_name = str(each)
                    if each_name not in current_sounds:
                        each_name = str(~each)
                    if each_name not in current_sounds:
                        current_position += interval
                        continue
                    current_sound = current_sounds[each_name]
                    if current_sound is None:
                        current_position += interval
                        continue
                    current_max_time = min(len(current_sound),
                                           duration + current_fadeout_time)
                    current_max_fadeout_time = min(len(current_sound),
                                                   current_fadeout_time)
                    current_sound = current_sound[
                        current_offset:current_max_time]
                if check_adsr(each):
                    current_adsr = each.adsr
                    attack, decay, sustain, release = current_adsr
                    change_db = percentage_to_db(sustain)
                    result_db = current_sound.dBFS + change_db
                    if attack > 0:
                        current_sound = current_sound.fade_in(attack)
                    if decay > 0:
                        current_sound = current_sound.fade(to_gain=result_db,
                                                           start=attack,
                                                           duration=decay)
                    else:
                        current_sound = current_sound[:attack].append(
                            current_sound[attack:] + change_db)
                    if release > 0:
                        current_sound = current_sound.fade_out(release)
                if check_fade(each):
                    if each.fade_in_time > 0:
                        current_sound = current_sound.fade_in(
                            each.fade_in_time)
                    if each.fade_out_time > 0:
                        current_sound = current_sound.fade_out(
                            each.fade_out_time)
                if check_reverse(each):
                    current_sound = current_sound.reverse()

                if current_fadeout_time != 0 and type(each) != AudioSegment:
                    current_sound = current_sound.fade_out(
                        duration=current_max_fadeout_time)
                current_sound += volume
                current_silent_audio = current_silent_audio.overlay(
                    current_sound, position=current_position)
                current_position += interval
        if current_pan:
            pan_ranges = [
                self.bar_to_real_time(i.start_time - 1, current_bpm, 1)
                for i in current_pan
            ]
            pan_values = [i.get_pan_value() for i in current_pan]
            audio_list = []
            for k in range(len(pan_ranges) - 1):
                current_audio = current_silent_audio[
                    pan_ranges[k]:pan_ranges[k + 1]].pan(pan_values[k])
                audio_list.append(current_audio)
            current_audio = current_silent_audio[pan_ranges[-1]:].pan(
                pan_values[-1])
            audio_list.append(current_audio)
            first_audio = audio_list[0]
            for each in audio_list[1:]:
                first_audio = first_audio.append(each, crossfade=0)
            current_silent_audio = first_audio

        if current_volume:
            volume_ranges = [
                self.bar_to_real_time(i.start_time - 1, current_bpm, 1)
                for i in current_volume
            ]
            volume_values = [
                percentage_to_db(i.value_percentage) for i in current_volume
            ]
            audio_list = []
            for k in range(len(volume_ranges) - 1):
                current_audio = current_silent_audio[
                    volume_ranges[k]:volume_ranges[k + 1]] + volume_values[k]
                audio_list.append(current_audio)
            current_audio = current_silent_audio[
                volume_ranges[-1]:] + volume_values[-1]
            audio_list.append(current_audio)
            first_audio = audio_list[0]
            for each in audio_list[1:]:
                first_audio = first_audio.append(each, crossfade=0)
            current_silent_audio = first_audio
        if check_adsr(current_chord):
            current_adsr = current_chord.adsr
            attack, decay, sustain, release = current_adsr
            change_db = percentage_to_db(sustain)
            result_db = current_silent_audio.dBFS + change_db
            if attack > 0:
                current_silent_audio = current_silent_audio.fade_in(attack)
            if decay > 0:
                current_silent_audio = current_silent_audio.fade(
                    to_gain=result_db, start=attack, duration=decay)
            else:
                current_silent_audio = current_silent_audio[:attack].append(
                    current_silent_audio[attack:] + change_db)
            if release > 0:
                current_silent_audio = current_silent_audio.fade_out(release)
        if check_fade(current_chord):
            if current_chord.fade_in_time > 0:
                current_silent_audio = current_silent_audio.fade_in(
                    current_chord.fade_in_time)
            if current_chord.fade_out_time > 0:
                current_silent_audio = current_silent_audio.fade_out(
                    current_chord.fade_out_time)
        if check_offset(current_chord):
            current_silent_audio = current_silent_audio[
                self.bar_to_real_time(current_chord.offset, current_bpm, 1):]
        if check_reverse(current_chord):
            current_silent_audio = current_silent_audio.reverse()
        silent_audio = silent_audio.overlay(current_silent_audio,
                                            position=current_start_time)
        return silent_audio

    def export_midi_file(self):
        self.show_msg('')
        filename = filedialog.asksaveasfilename(
            initialdir=self.last_place,
            title=self.language_dict['title'][17],
            filetypes=((self.language_dict['title'][1], "*.*"), ),
            defaultextension=f".mid",
            initialfile=self.language_dict['untitled'])
        if not filename:
            return
        result = self.get_current_musicpy_chords()
        if result is None:
            return
        current_chord = result[1]
        self.stop_playing()
        self.show_msg(f'{self.language_dict["msg"][21]}{filename}')
        self.msg.update()
        write(filename, current_chord, self.current_bpm)
        self.show_msg(f'{self.language_dict["msg"][24]}{filename}')

    def get_current_musicpy_chords(self):
        current_notes = self.set_musicpy_code_text.get('1.0', 'end-1c')
        current_channel_num = 0
        current_bpm = self.current_bpm
        try:
            current_chord = eval(current_notes, globals(), globals())
        except:
            try:
                lines = current_notes.split('\n')
                for k in range(len(lines)):
                    each = lines[k]
                    if each.startswith('play '):
                        lines[k] = 'current_chord = ' + each[5:]
                current_notes = '\n'.join(lines)
                exec(current_notes, globals(), globals())
                current_chord = globals()['current_chord']
                if type(current_chord) == tuple:
                    length = len(current_chord)
                    if length > 1:
                        if length == 2:
                            current_chord, current_bpm = current_chord
                        elif length == 3:
                            current_chord, current_bpm, current_channel_num = current_chord
                            current_channel_num -= 1
                        self.change_current_bpm_entry.delete(0, END)
                        self.change_current_bpm_entry.insert(END, current_bpm)
                        self.change_current_bpm(1)
            except Exception as e:
                print(str(e))
                self.show_msg(self.language_dict["msg"][4])
                return
        if type(current_chord) == note:
            has_reverse = check_reverse(current_chord)
            has_offset = check_offset(current_chord)
            current_chord = chord([current_chord])
            if has_reverse:
                current_chord.reverse_audio = True
            if has_offset:
                current_chord.offset = has_offset
        elif type(current_chord) == list and all(
                type(i) == chord for i in current_chord):
            current_chord = concat(current_chord, mode='|')
        if type(current_chord) == chord:
            return 'chord', current_chord, current_channel_num
        if type(current_chord) == track:
            has_reverse = check_reverse(current_chord)
            has_offset = check_offset(current_chord)
            current_chord = build(
                current_chord,
                bpm=current_chord.tempo
                if current_chord.tempo is not None else current_bpm,
                name=current_chord.name)
            if has_reverse:
                current_chord.reverse_audio = True
            if has_offset:
                current_chord.offset = has_offset
        if type(current_chord) == piece:
            current_bpm = current_chord.tempo
            current_start_times = current_chord.start_times
            self.change_current_bpm_entry.delete(0, END)
            self.change_current_bpm_entry.insert(END, current_bpm)
            self.change_current_bpm(1)
            return 'piece', current_chord

    def clear_current_channel(self):
        current_ind = self.choose_channels.index(ANCHOR)
        if current_ind < self.channel_num and self.channel_list_focus:
            self.choose_channels.delete(current_ind)
            self.choose_channels.insert(current_ind,
                                        f'Channel {current_ind+1}')
            self.channel_names[current_ind] = f'Channel {current_ind+1}'
            self.channel_sound_modules_name[current_ind] = ''
            self.channel_sound_modules[current_ind] = None
            self.channel_sound_audiosegments[current_ind] = None
            self.channel_note_sounds_path[current_ind] = None
            self.channel_dict[current_ind] = copy(notedict)
            self.current_channel_name_entry.delete(0, END)
            self.current_channel_sound_modules_entry.delete(0, END)

    def clear_all_channels(self, mode=0):
        if_clear = messagebox.askyesnocancel(
            self.language_dict['other'][0],
            self.language_dict['other'][1],
            icon='warning') if mode == 0 else True
        if if_clear:
            self.stop_playing()
            self.choose_channels.delete(0, END)
            self.channel_names.clear()
            self.channel_sound_modules_name.clear()
            self.channel_sound_modules.clear()
            self.channel_sound_audiosegments.clear()
            self.channel_note_sounds_path.clear()
            self.channel_dict.clear()
            self.channel_num = 0
            self.current_channel_name_entry.delete(0, END)
            self.current_channel_sound_modules_entry.delete(0, END)

    def delete_channel(self):
        current_ind = self.choose_channels.index(ANCHOR)
        if current_ind < self.channel_num and self.channel_list_focus:
            self.choose_channels.delete(current_ind)
            new_ind = min(current_ind, self.channel_num - 2)
            self.choose_channels.see(new_ind)
            self.choose_channels.selection_anchor(new_ind)
            self.choose_channels.selection_set(new_ind)
            del self.channel_names[current_ind]
            del self.channel_sound_modules_name[current_ind]
            del self.channel_sound_modules[current_ind]
            del self.channel_sound_audiosegments[current_ind]
            del self.channel_note_sounds_path[current_ind]
            del self.channel_dict[current_ind]
            self.channel_num -= 1
            if self.channel_num > 0:
                self.show_current_channel()
            else:
                self.current_channel_name_entry.delete(0, END)
                self.current_channel_sound_modules_entry.delete(0, END)

    def add_new_channel(self):
        self.channel_num += 1
        current_channel_name = f'{self.language_dict["channel"]} {self.channel_num}'
        self.choose_channels.insert(END, current_channel_name)
        self.choose_channels.selection_clear(ANCHOR)
        self.choose_channels.see(END)
        self.choose_channels.selection_anchor(END)
        self.choose_channels.selection_set(END)
        self.channel_names.append(current_channel_name)
        self.channel_sound_modules_name.append('')
        self.channel_sound_modules.append(None)
        self.channel_sound_audiosegments.append(None)
        self.channel_note_sounds_path.append(None)
        self.channel_dict.append(copy(notedict))
        self.show_current_channel()

    def init_channels(self, num=1):
        self.channel_num = num
        for i in range(self.channel_num):
            current_channel_name = f'{self.language_dict["channel"]} {i+1}'
            self.choose_channels.insert(END, current_channel_name)
            self.channel_names.append(current_channel_name)
            self.channel_sound_modules_name.append('')
            self.channel_sound_modules.append(None)
            self.channel_sound_audiosegments.append(None)
            self.channel_note_sounds_path.append(None)
            self.channel_dict.append(copy(notedict))

    def change_channel_dict(self):
        if self.open_change_channel_dict:
            self.change_dict_window.focus_set()
            return
        else:
            current_ind = self.choose_channels.index(ANCHOR)
            self.current_channel_dict_num = current_ind
            if current_ind < self.channel_num and self.channel_list_focus:
                self.open_change_channel_dict = True
                self.change_dict_window = Toplevel(self)
                self.change_dict_window.iconphoto(False, self.icon_image)
                self.change_dict_window.configure(bg=background_color)
                x = self.winfo_x()
                y = self.winfo_y()
                w = self.change_dict_window.winfo_width()
                h = self.change_dict_window.winfo_height()
                self.change_dict_window.geometry("%dx%d+%d+%d" %
                                                 (w, h, x + 200, y + 200))
                self.change_dict_window.protocol("WM_DELETE_WINDOW",
                                                 self.close_change_dict_window)
                self.change_dict_window.title(
                    self.language_dict['change_channel_dict'][0])
                self.change_dict_window.minsize(500, 300)
                self.change_dict_window.focus_set()
                current_dict = self.channel_dict[current_ind]
                self.current_dict = current_dict
                self.dict_configs_bar = Scrollbar(self.change_dict_window)
                self.dict_configs_bar.place(x=151,
                                            y=90,
                                            height=185,
                                            anchor=CENTER)
                self.dict_configs = Listbox(
                    self.change_dict_window,
                    yscrollcommand=self.dict_configs_bar.set,
                    exportselection=False,
                    font=(font_type, font_size))
                self.dict_configs.config(activestyle='none')
                self.dict_configs.bind(
                    '<<ListboxSelect>>',
                    lambda e: self.show_current_dict_configs())
                self.dict_configs_bar.config(command=self.dict_configs.yview)
                self.dict_configs.place(x=0, y=0, height=185)
                for each in current_dict:
                    self.dict_configs.insert(END, each)
                self.current_note_name = ttk.Label(
                    self.change_dict_window,
                    text=self.language_dict['change_channel_dict'][1])
                self.current_note_name.place(x=200, y=0)
                self.current_note_name_entry = ttk.Entry(
                    self.change_dict_window,
                    width=10,
                    font=(font_type, font_size))
                self.current_note_name_entry.place(x=300, y=0)
                self.current_note_value = ttk.Label(
                    self.change_dict_window,
                    text=self.language_dict['change_channel_dict'][2])
                self.current_note_value.place(x=200, y=50)
                self.current_note_value_entry = ttk.Entry(
                    self.change_dict_window,
                    width=10,
                    font=(font_type, font_size))
                self.current_note_value_entry.place(x=300, y=50)
                self.change_current_note_name_button = ttk.Button(
                    self.change_dict_window,
                    text=self.language_dict['change_channel_dict'][3],
                    command=self.change_current_note_name)
                self.change_current_note_value_button = ttk.Button(
                    self.change_dict_window,
                    text=self.language_dict['change_channel_dict'][4],
                    command=self.change_current_note_value)
                self.add_new_note_button = ttk.Button(
                    self.change_dict_window,
                    text=self.language_dict['change_channel_dict'][5],
                    command=self.add_new_note)
                self.remove_note_button = ttk.Button(
                    self.change_dict_window,
                    text=self.language_dict['change_channel_dict'][6],
                    command=self.remove_note)
                self.new_note_name_entry = ttk.Entry(self.change_dict_window,
                                                     width=10,
                                                     font=(font_type,
                                                           font_size))
                self.change_current_note_name_button.place(x=200, y=100)
                self.change_current_note_value_button.place(x=350, y=100)
                self.add_new_note_button.place(x=200, y=150)
                self.new_note_name_entry.place(x=320, y=150)
                self.remove_note_button.place(x=200, y=200)
                self.reload_channel_sounds_button = ttk.Button(
                    self.change_dict_window,
                    text=self.language_dict['change_channel_dict'][7],
                    command=self.reload_channel_sounds)
                self.reload_channel_sounds_button.place(x=200, y=250)
                self.clear_all_notes_button = ttk.Button(
                    self.change_dict_window,
                    text=self.language_dict['change_channel_dict'][8],
                    command=self.clear_all_notes)
                self.clear_all_notes_button.place(x=320, y=200)

    def clear_all_notes(self):
        self.dict_configs.delete(0, END)
        self.current_dict.clear()
        self.current_note_name_entry.delete(0, END)
        self.current_note_value_entry.delete(0, END)

    def close_change_dict_window(self):
        self.change_dict_window.destroy()
        self.open_change_channel_dict = False

    def close_configure_sf2_file_window(self):
        self.configure_sf2_file_window.destroy()
        self.open_configure_sf2_file = False

    def change_current_note_name(self):
        current_note = self.dict_configs.get(ANCHOR)
        current_ind = self.dict_configs.index(ANCHOR)
        current_note_name = self.current_note_name_entry.get()
        if current_note_name and current_note_name != current_note:
            current_keys = list(self.current_dict.keys())
            current_keys[current_ind] = current_note_name
            self.current_dict[current_note_name] = self.current_dict[
                current_note]
            del self.current_dict[current_note]
            self.current_dict = {i: self.current_dict[i] for i in current_keys}
            self.channel_dict[
                self.current_channel_dict_num] = self.current_dict
            self.dict_configs.delete(0, END)
            for each in self.current_dict:
                self.dict_configs.insert(END, each)
            self.dict_configs.see(current_ind)
            self.dict_configs.selection_anchor(current_ind)
            self.dict_configs.selection_set(current_ind)

    def change_current_note_value(self):
        current_note = self.dict_configs.get(ANCHOR)
        if not current_note:
            return
        current_note_value_before = self.current_dict[current_note]
        current_note_value = self.current_note_value_entry.get()
        if current_note_value != current_note_value_before:
            self.current_dict[current_note] = current_note_value

    def add_new_note(self):
        current_note_name = self.new_note_name_entry.get()
        if current_note_name and current_note_name not in self.current_dict:
            self.current_dict[current_note_name] = ''
            self.dict_configs.insert(END, current_note_name)
            self.dict_configs.see(END)
            self.dict_configs.selection_clear(ANCHOR)
            self.dict_configs.selection_anchor(END)
            self.dict_configs.selection_set(END)
            self.show_current_dict_configs()

    def remove_note(self):
        current_note = self.dict_configs.get(ANCHOR)
        if current_note not in self.current_dict:
            return
        del self.current_dict[current_note]
        current_ind = self.dict_configs.index(ANCHOR)
        self.dict_configs.delete(current_ind)
        new_ind = min(current_ind, len(self.current_dict) - 1)
        self.dict_configs.see(new_ind)
        self.dict_configs.selection_anchor(new_ind)
        self.dict_configs.selection_set(new_ind)
        self.show_current_dict_configs()

    def reload_channel_sounds(self, current_ind=None):
        if current_ind is None:
            current_mode = 0
        else:
            current_mode = 1
        self.show_msg('')
        current_ind = self.current_channel_dict_num if not current_mode else current_ind
        sound_path = self.channel_sound_modules_name[current_ind]
        if os.path.isfile(sound_path):
            self.load_sf2_file(current_ind=current_ind, sound_path=sound_path)
        else:
            try:
                self.show_msg(
                    f'{self.language_dict["msg"][28]}{self.channel_names[current_ind]} ...'
                )
                self.msg.update()

                notedict = self.channel_dict[current_ind]
                note_sounds = load(notedict, sound_path, global_volume)
                note_sounds_path = load_sounds(note_sounds)
                self.channel_sound_modules[current_ind] = note_sounds
                self.channel_sound_audiosegments[
                    current_ind] = load_audiosegments(notedict, sound_path)
                self.channel_note_sounds_path[current_ind] = note_sounds_path
                if not current_mode:
                    self.current_channel_sound_modules_entry.delete(0, END)
                    self.current_channel_sound_modules_entry.insert(
                        END, sound_path)
                current_msg = self.language_dict["msg"][29].split('|')
                self.show_msg(
                    f'{current_msg[0]}{self.channel_names[current_ind]}{current_msg[1]}'
                )
                if not current_mode:
                    self.choose_channels.see(current_ind)
                    self.choose_channels.selection_anchor(current_ind)
                    self.choose_channels.selection_set(current_ind)
            except Exception as e:
                print(str(e))
                self.show_msg(self.language_dict["msg"][30])

    def show_current_dict_configs(self):
        current_note = self.dict_configs.get(ANCHOR)
        if current_note in self.current_dict:
            self.current_note_name_entry.delete(0, END)
            self.current_note_name_entry.insert(END, current_note)
            self.current_note_value_entry.delete(0, END)
            self.current_note_value_entry.insert(
                END, self.current_dict[current_note])

    def change_current_channel_name(self):
        current_ind = self.choose_channels.index(ANCHOR)
        if current_ind < self.channel_num and self.channel_list_focus:
            current_channel_name = self.current_channel_name_entry.get()
            self.choose_channels.delete(current_ind)
            self.choose_channels.insert(current_ind, current_channel_name)
            self.choose_channels.see(current_ind)
            self.choose_channels.selection_anchor(current_ind)
            self.choose_channels.selection_set(current_ind)
            self.channel_names[current_ind] = current_channel_name

    def show_current_channel(self):
        self.channel_list_focus = True
        current_ind = self.choose_channels.index(ANCHOR)
        if current_ind < self.channel_num and self.channel_list_focus:
            self.current_channel_name_entry.delete(0, END)
            self.current_channel_name_entry.insert(
                END, self.channel_names[current_ind])
            self.current_channel_sound_modules_entry.delete(0, END)
            self.current_channel_sound_modules_entry.insert(
                END, self.channel_sound_modules_name[current_ind])

    def cancel_choose_channels(self):
        self.choose_channels.selection_clear(0, END)
        self.current_channel_name_entry.delete(0, END)
        self.current_channel_sound_modules_entry.delete(0, END)
        self.current_channel_name_label.focus_set()
        self.channel_list_focus = False

    def load_midi_file_func(self, mode=0):
        self.show_msg('')
        if mode == 0:
            filename = filedialog.askopenfilename(
                initialdir=self.last_place,
                title=self.language_dict['title'][18],
                filetypes=(("MIDI", "*.mid"), (self.language_dict['title'][1],
                                               "*.*")))
        else:
            filename = self.load_midi_file_entry.get()
        if filename:
            try:
                memory = filename[:filename.rindex('/') + 1]
                current_midi_file = read(filename)
            except:
                self.show_msg(self.language_dict["msg"][31])
                return
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
            self.load_midi_file_entry.delete(0, END)
            self.load_midi_file_entry.insert(END, filename)
            self.set_musicpy_code_text.delete('1.0', END)
            self.change_current_bpm_entry.delete(0, END)
            self.change_current_bpm_entry.insert(END, current_midi_file[0])
            self.change_current_bpm(1)
            self.set_musicpy_code_text.insert(
                END, f'read("{filename}", mode="all", merge=True)[1]')
            self.show_msg(self.language_dict["msg"][32])

    def change_current_sound_path_func(self):
        current_path = self.current_channel_sound_modules_entry.get()
        if os.path.isdir(current_path):
            self.change_current_sound_path(1)
        elif os.path.isfile(current_path):
            self.load_sf2_file(1)

    def change_current_sound_path(self, mode=0):
        current_ind = self.choose_channels.index(ANCHOR)
        if current_ind < self.channel_num and self.channel_list_focus:
            self.show_msg('')
            if mode == 0:
                directory = filedialog.askdirectory(
                    initialdir=self.last_place,
                    title=self.language_dict['title'][19],
                )
            else:
                directory = self.current_channel_sound_modules_entry.get()
            if directory:
                memory = directory
                with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                    f.write(memory)
                self.last_place = memory
                try:
                    self.show_msg(
                        f'{self.language_dict["msg"][33]}{self.channel_names[current_ind]} ...'
                    )
                    self.msg.update()
                    sound_path = directory
                    notedict = self.channel_dict[current_ind]
                    note_sounds = load(notedict, sound_path, global_volume)
                    note_sounds_path = load_sounds(note_sounds)
                    self.channel_sound_modules[current_ind] = note_sounds
                    self.channel_note_sounds_path[
                        current_ind] = note_sounds_path
                    self.channel_sound_modules_name[current_ind] = sound_path
                    self.channel_sound_audiosegments[
                        current_ind] = load_audiosegments(
                            notedict, sound_path)

                    self.current_channel_sound_modules_entry.delete(0, END)
                    self.current_channel_sound_modules_entry.insert(
                        END, sound_path)
                    current_msg = self.language_dict["msg"][29].split('|')
                    self.show_msg(
                        f'{current_msg[0]}{self.channel_names[current_ind]}{current_msg[1]}'
                    )
                    self.choose_channels.see(current_ind)
                    self.choose_channels.selection_anchor(current_ind)
                    self.choose_channels.selection_set(current_ind)
                except Exception as e:
                    print(str(e))
                    self.show_msg(self.language_dict["msg"][30])

    def bar_to_real_time(self, bar, bpm, mode=0):
        # return time in ms
        return int((60000 / bpm) *
                   (bar * 4)) if mode == 0 else (60000 / bpm) * (bar * 4)

    def real_time_to_bar(self, time, bpm):
        return (time / (60000 / bpm)) / 4

    def change_current_bpm(self, mode=0):
        self.show_msg('')
        current_bpm = self.change_current_bpm_entry.get()
        try:
            current_bpm = float(current_bpm)
            self.current_bpm = current_bpm
            if mode == 0:
                self.show_msg(f'{self.language_dict["msg"][34]}{current_bpm}')
        except:
            if mode == 0:
                self.show_msg(self.language_dict["msg"][35])

    def play_note_func(self, name, duration, volume, channel=0):
        note_sounds_path = self.channel_note_sounds_path[channel]
        note_sounds = self.channel_sound_modules[channel]
        if name in note_sounds_path:
            current_sound = note_sounds[name]
            if current_sound:
                current_sound = pygame.mixer.Sound(note_sounds_path[name])
                current_sound.set_volume(global_volume * volume / 127)
                duration_time = self.bar_to_real_time(duration,
                                                      self.current_bpm)
                current_sound.play()
                current_fadeout_time = int(
                    duration_time * play_audio_fadeout_time_ratio
                ) if play_fadeout_use_ratio else int(play_audio_fadeout_time)
                current_id = self.after(
                    duration_time,
                    lambda: current_sound.fadeout(current_fadeout_time)
                    if current_fadeout_time != 0 else current_sound.stop())
                self.current_playing.append(current_id)

    def stop_playing(self):
        pygame.mixer.stop()
        if self.current_playing:
            for each in self.current_playing:
                self.after_cancel(each)
            self.current_playing.clear()
        if self.piece_playing:
            for each in self.piece_playing:
                self.after_cancel(each)
            self.piece_playing.clear()
        try:
            simpleaudio.stop_all()
        except:
            pass
        try:
            pygame.mixer.music.stop()
        except:
            pass

    def play_current_musicpy_code(self):
        if not self.default_load:
            return
        self.show_msg('')
        if not self.channel_sound_modules:
            self.show_msg(self.language_dict["msg"][18])
            return

        self.stop_playing()
        current_notes = self.set_musicpy_code_text.get('1.0', 'end-1c')
        current_channel_num = 0
        current_bpm = self.current_bpm
        if 'current_chord' in globals():
            del globals()['current_chord']
        try:
            current_chord = eval(current_notes, globals(), globals())
        except:
            try:
                lines = current_notes.split('\n')
                for k in range(len(lines)):
                    each = lines[k]
                    if each.startswith('play '):
                        lines[k] = 'current_chord = ' + each[5:]
                current_notes = '\n'.join(lines)
                exec(current_notes, globals(), globals())
                current_chord = globals()['current_chord']
                if type(current_chord) == tuple:
                    length = len(current_chord)
                    if length > 1:
                        if length == 2:
                            current_chord, current_bpm = current_chord
                        elif length == 3:
                            current_chord, current_bpm, current_channel_num = current_chord
                            current_channel_num -= 1
                        self.change_current_bpm_entry.delete(0, END)
                        self.change_current_bpm_entry.insert(END, current_bpm)
                        self.change_current_bpm(1)

            except Exception as e:
                print(str(e))
                self.show_msg(self.language_dict["msg"][4])
                return
        self.play_musicpy_sounds(current_chord, current_bpm,
                                 current_channel_num)

    def play_musicpy_sounds(self,
                            current_chord,
                            current_bpm=None,
                            current_channel_num=None):
        if type(current_chord) == note:
            has_reverse = check_reverse(current_chord)
            has_offset = check_offset(current_chord)
            current_chord = chord([current_chord])
            if has_reverse:
                current_chord.reverse_audio = True
            if has_offset:
                current_chord.offset = has_offset
        elif type(current_chord) == list and all(
                type(i) == chord for i in current_chord):
            current_chord = concat(current_chord, mode='|')
        if type(current_chord) == chord:
            if check_special(current_chord):
                self.export_audio_file(action='play',
                                       channel_num=current_channel_num)
            else:
                self.play_channel(current_chord, current_channel_num)
        elif type(current_chord) == track:
            has_reverse = check_reverse(current_chord)
            has_offset = check_offset(current_chord)
            current_chord = build(
                current_chord,
                bpm=current_chord.tempo
                if current_chord.tempo is not None else current_bpm,
                name=current_chord.name)
            if has_reverse:
                current_chord.reverse_audio = True
            if has_offset:
                current_chord.offset = has_offset
        if type(current_chord) == piece:
            if check_special(current_chord) or any(
                    type(self.channel_sound_modules[i]) == rs.sf2_loader
                    for i in current_chord.channels):
                self.export_audio_file(action='play')
                return
            current_tracks = current_chord.tracks
            current_channel_nums = current_chord.channels if current_chord.channels else [
                i for i in range(len(current_chord))
            ]
            current_bpm = current_chord.tempo
            current_start_times = current_chord.start_times
            self.change_current_bpm_entry.delete(0, END)
            self.change_current_bpm_entry.insert(END, current_bpm)
            self.change_current_bpm(1)
            for each in range(len(current_chord)):
                current_id = self.after(
                    self.bar_to_real_time(current_start_times[each],
                                          self.current_bpm),
                    lambda each=each: self.play_channel(
                        current_tracks[each], current_channel_nums[each]))
                self.piece_playing.append(current_id)
        self.show_msg(self.language_dict["msg"][22])

    def play_channel(self, current_chord, current_channel_num=0):
        if len(self.channel_sound_modules) <= current_channel_num:
            self.show_msg(
                f'{self.language_dict["msg"][25]}{current_channel_num+1}')
            return
        if not self.channel_sound_modules[current_channel_num]:
            self.show_msg(
                f'{self.language_dict["channel"]}{current_channel_num+1} {self.language_dict["msg"][26]}'
            )
            return
        current_sound_modules = self.channel_sound_modules[current_channel_num]
        if type(current_sound_modules) == rs.sf2_loader:
            current_sound_modules.play_chord(current_chord,
                                             bpm=self.current_bpm)
        else:
            current_intervals = current_chord.interval
            current_durations = current_chord.get_duration()
            current_volumes = current_chord.get_volume()
            current_time = 0
            for i in range(len(current_chord)):
                each = current_chord.notes[i]
                if type(each) == note:
                    if i == 0:
                        self.play_note_func(
                            f'{standardize_note(each.name)}{each.num}',
                            current_durations[i], current_volumes[i],
                            current_channel_num)
                    else:
                        duration = current_durations[i]
                        volume = current_volumes[i]
                        current_time += self.bar_to_real_time(
                            current_intervals[i - 1], self.current_bpm, 1)
                        current_id = self.after(
                            int(current_time),
                            lambda each=each, duration=duration, volume=volume:
                            self.play_note_func(
                                f'{standardize_note(each.name)}{each.num}',
                                duration, volume, current_channel_num))
                        self.current_playing.append(current_id)

    def play_current_chord(self):
        if not self.default_load:
            return
        self.show_msg('')
        current_notes = self.set_chord_text.get('1.0', 'end-1c')
        if ',' in current_notes:
            current_notes = current_notes.replace(' ', '').split(',')
        else:
            current_notes = current_notes.replace('  ', ' ').split(' ')
        try:
            current_notes = chord(current_notes)
            self.show_msg(self.language_dict["msg"][36])
        except:
            self.show_msg(self.language_dict["msg"][37])
            return
        self.stop_playing()
        for each in current_notes:
            play_note(f'{standardize_note(each.name)}{each.num}')

    def open_change_settings(self):
        if not self.open_settings:
            self.open_settings = True
        else:
            root2.focus_force()
            return
        os.chdir('scripts')
        with open('change_settings.pyw', encoding='utf-8-sig') as f:
            exec(f.read(), globals(), globals())


def open_main_window():
    current_start_window.destroy()
    global root
    root = Root()
    root.lift()
    root.attributes("-topmost", True)
    root.focus_force()
    root.attributes('-topmost', 0)
    root.mainloop()


class start_window(Tk):
    def __init__(self):
        super(start_window, self).__init__()
        self.configure(bg='ivory2')
        self.overrideredirect(True)
        self.minsize(500, 220)
        self.lift()
        self.attributes("-topmost", True)
        self.attributes('-topmost', 0)

        window_width = self.winfo_reqwidth()
        window_height = self.winfo_reqheight()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (window_width * 1.5)
        y = (screen_height / 2) - window_height
        self.geometry('+%d+%d' % (x, y))

        style = ttk.Style()
        style.configure('TLabel', font=('Consolas', 30), background='ivory2')
        style.configure('loading.TLabel',
                        font=('Consolas', 15),
                        background='ivory2')

        self.title_label = ttk.Label(self, text='Easy Sampler')
        self.title_label.place(x=120, y=80)
        pygame.mixer.init(frequency, sound_size, channel, buffer)
        pygame.mixer.set_num_channels(maxinum_channels)
        self.after(500, open_main_window)


current_start_window = start_window()
current_start_window.mainloop()
