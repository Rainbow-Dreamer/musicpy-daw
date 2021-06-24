with open('scripts/settings.py', encoding='utf-8-sig') as f:
    exec(f.read())


class custom_channel:
    def __init__(self, channel):
        self.channel = channel


class pitch:
    def __init__(self, path, note='C5'):
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
        self.audio = librosa.load(path, sr=self.sample_rate)[0]
        self.note = N(note) if type(note) == str else note

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

    def generate_dict(self, start='A0', end='C8', mode='librosa'):
        if type(start) != note:
            start = N(start)
        if type(end) != note:
            end = N(end)
        degree = self.note.degree
        result = {}
        for i in range(end.degree - start.degree + 1):
            current_note_name = str(start + i)
            print(f'Converting note {current_note_name} ...', flush=True)
            result[current_note_name] = self.pitch_shift(start.degree + i -
                                                         degree,
                                                         mode=mode)
        return result

    def export_sound_files(self,
                           path='.',
                           folder_name='Untitled',
                           start='A0',
                           end='C8',
                           format='wav',
                           mode='librosa'):
        abs_path = os.getcwd()
        os.chdir(path)
        if folder_name not in os.listdir():
            os.mkdir(folder_name)
        os.chdir(folder_name)
        current_dict = self.generate_dict(start, end, mode=mode)
        for each in current_dict:
            current_dict[each].export(f'{each}.{format}', format=format)
        os.chdir(abs_path)

    def __len__(self):
        return len(self.sounds)

    def play(self):
        play_audio(self)


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


def load(dic, path, file_format, volume):
    wavedict = {}
    for i in dic:
        try:
            current_sound = pygame.mixer.Sound(
                f'{path}/{dic[i]}.{file_format}')
            wavedict[i] = current_sound
        except:
            wavedict[i] = None
        root.update()
    if volume != None:
        [wavedict[x].set_volume(volume) for x in wavedict if wavedict[x]]
    return wavedict


def load_audiosegments(current_dict, current_sound_path, current_sound_format):
    current_sounds = {}
    current_sound_files = os.listdir(current_sound_path)
    for i in current_dict:
        current_sound_obj = current_dict[i]
        current_sound_name = f'{current_sound_obj}.{current_sound_format}'
        if current_sound_obj and current_sound_name in current_sound_files:
            current_sound_obj_path = f'{current_sound_path}/{current_sound_name}'
            current_sounds[i] = AudioSegment.from_file(
                current_sound_obj_path, format=current_sound_format)
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
    freq_list = [get_freq(i) for i in sound]
    if volume is None:
        volume = [velocity_to_db(i) for i in temp.get_volume()]
    else:
        volume = [volume for i in range(len(temp))
                  ] if type(volume) != list else volume
        volume = [percentage_to_db(i) for i in volume]
    for i in range(1, len(temp) + 1):
        current_note = temp[i]
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
    return temp


def audio(obj, track_num=0):
    if type(obj) == note:
        obj = chord([obj])
    result = root.export_audio_file(obj, action='get', track_num=track_num)
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
        self.minsize(1000, 650)
        self.configure(bg=background_color)

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
        style.configure('TEntry', font=(font_type, font_size))
        style.configure('TLabel',
                        background=background_color,
                        foreground=foreground_color)
        style.map('TButton',
                  background=[('active', active_background_color)],
                  foreground=[('active', active_foreground_color)])

        self.set_chord_button = ttk.Button(self,
                                           text='Play Notes',
                                           command=self.play_current_chord)
        self.set_chord_button.place(x=0, y=350)
        self.set_chord_entry = Text(self,
                                    width=50,
                                    height=5,
                                    wrap='none',
                                    undo=True,
                                    autoseparators=True,
                                    maxundo=-1)
        self.set_chord_entry.place(x=100, y=350)

        self.set_musicpy_code_button = ttk.Button(
            self,
            text='Play Musicpy Code',
            command=self.play_current_musicpy_code)
        self.set_musicpy_code_button.place(x=0, y=450)
        self.set_musicpy_code_entry = Text(self,
                                           width=120,
                                           height=10,
                                           wrap='none',
                                           undo=True,
                                           autoseparators=True,
                                           maxundo=-1)
        self.set_musicpy_code_entry.place(x=130, y=450)
        self.bind('<Control-r>', lambda e: self.play_current_musicpy_code())
        self.bind('<Control-e>', lambda e: self.stop_playing())
        self.bind('<Control-w>', lambda e: self.open_project_file())
        self.bind('<Control-s>', lambda e: self.save_as_project_file())
        self.bind('<Control-f>', lambda e: self.load_musicpy_code())
        self.bind('<Control-d>', lambda e: self.save_current_musicpy_code())
        self.bind('<Control-g>', lambda e: self.open_export_menu())
        self.bind('<Control-h>', lambda e: self.load_midi_file_func())
        self.menubar = Menu(self,
                            tearoff=False,
                            bg=background_color,
                            activebackground=active_background_color,
                            activeforeground=active_foreground_color,
                            disabledforeground=disabled_foreground_color)
        self.set_musicpy_code_entry.bind(
            "<Button-3>",
            lambda x: self.rightKey(x, self.set_musicpy_code_entry))

        self.stop_button = ttk.Button(self,
                                      text='Stop',
                                      command=self.stop_playing)
        self.stop_button.place(x=0, y=500)

        self.change_current_bpm_button = ttk.Button(
            self, text='Change BPM', command=self.change_current_bpm)
        self.change_current_bpm_button.place(x=0, y=300)
        self.change_current_bpm_entry = ttk.Entry(self, width=10)
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
        self.change_current_sound_path_button.place(x=700, y=150)

        self.change_current_sound_format_button = ttk.Button(
            self,
            text='Change Sound Format',
            command=self.change_current_sound_format)
        self.change_current_sound_format_button.place(x=850, y=150)
        self.current_sound_format_label = ttk.Label(self,
                                                    text='Track Sound Format')
        self.current_sound_format_label.place(x=520, y=250)
        self.change_current_sound_format_entry = ttk.Entry(self, width=20)
        self.change_current_sound_format_entry.place(x=660, y=250)
        self.change_current_sound_format_entry.bind(
            '<Return>', lambda e: self.change_current_sound_format())

        self.load_midi_file_button = ttk.Button(
            self, text='Load MIDI File', command=self.load_midi_file_func)
        self.load_midi_file_button.place(x=500, y=350)
        self.load_midi_file_entry = ttk.Entry(self, width=50)
        self.load_midi_file_entry.insert(END, '')
        self.load_midi_file_entry.place(x=620, y=350)

        self.change_settings_button = ttk.Button(
            self, text='Change Settings', command=self.open_change_settings)
        self.change_settings_button.place(x=0, y=600)
        self.open_settings = False

        self.choose_tracks_bar = Scrollbar(self)
        self.choose_tracks_bar.place(x=225, y=215, height=125, anchor=CENTER)
        self.choose_tracks = Listbox(self,
                                     yscrollcommand=self.choose_tracks_bar.set,
                                     height=7,
                                     exportselection=False)
        self.choose_tracks.bind('<<ListboxSelect>>',
                                lambda e: self.show_current_track())
        self.choose_tracks.bind('<z>', lambda e: self.add_new_track())
        self.choose_tracks.bind('<x>', lambda e: self.delete_track())
        self.choose_tracks.bind('<c>', lambda e: self.clear_current_track())
        self.choose_tracks.bind('<v>', lambda e: self.clear_all_tracks())
        self.choose_tracks.place(x=0, y=150, width=220)
        self.choose_tracks_bar.config(command=self.choose_tracks.yview)

        self.current_track_name_label = ttk.Label(self, text='Track Name')
        self.current_track_name_entry = ttk.Entry(self, width=20)
        self.current_track_name_label.place(x=250, y=150)
        self.current_track_name_entry.place(x=350, y=150)
        self.current_track_name_entry.bind(
            '<Return>', lambda e: self.change_current_track_name())
        self.current_track_sound_modules_label = ttk.Label(
            self, text='Track Sound Modules')
        self.current_track_sound_modules_entry = ttk.Entry(self, width=82)
        self.current_track_sound_modules_entry.bind(
            '<Return>', lambda e: self.change_current_sound_path(mode=1))
        self.current_track_sound_modules_label.place(x=250, y=200)
        self.current_track_sound_modules_entry.place(x=400, y=200)

        self.change_current_track_name_button = ttk.Button(
            self,
            text='Change Track Name',
            command=self.change_current_track_name)
        self.change_current_track_name_button.place(x=550, y=150)

        self.add_new_track_button = ttk.Button(self,
                                               text='Add New Track',
                                               command=self.add_new_track)
        self.add_new_track_button.place(x=250, y=250)

        self.delete_new_track_button = ttk.Button(self,
                                                  text='Delete Track',
                                                  command=self.delete_track)
        self.delete_new_track_button.place(x=370, y=250)

        self.clear_all_tracks_button = ttk.Button(
            self, text='Clear All Tracks', command=self.clear_all_tracks)
        self.clear_all_tracks_button.place(x=250, y=300)

        self.clear_all_tracks_button = ttk.Button(
            self, text='Clear Track', command=self.clear_current_track)
        self.clear_all_tracks_button.place(x=370, y=300)

        self.change_track_dict_button = ttk.Button(
            self, text='Change Track Dict', command=self.change_track_dict)
        self.change_track_dict_button.place(x=830, y=250)

        self.load_track_settings_button = ttk.Button(
            self, text='Load Track Settings', command=self.load_track_settings)
        self.load_track_settings_button.place(x=830, y=300)

        self.piece_playing = []

        self.open_change_track_dict = False

        self.export_button = ttk.Button(self,
                                        text='Export',
                                        command=self.open_export_menu)
        self.export_button.place(x=500, y=400)

        self.export_menubar = Menu(
            self,
            tearoff=False,
            bg=background_color,
            activebackground=active_background_color,
            activeforeground=active_foreground_color,
            disabledforeground=disabled_foreground_color)

        self.export_audio_file_menubar = Menu(
            self,
            tearoff=False,
            bg=background_color,
            activebackground=active_background_color,
            activeforeground=active_foreground_color,
            disabledforeground=disabled_foreground_color)
        self.export_audio_file_menubar.add_command(
            label='Wave File',
            command=lambda: self.export_audio_file(mode='wav'))
        self.export_audio_file_menubar.add_command(
            label='MP3 File',
            command=lambda: self.export_audio_file(mode='mp3'))
        self.export_audio_file_menubar.add_command(
            label='OGG File',
            command=lambda: self.export_audio_file(mode='ogg'))
        self.export_audio_file_menubar.add_command(
            label='Other Format',
            command=lambda: self.export_audio_file(mode='other'))

        self.export_menubar.add_cascade(label='Audio File',
                                        menu=self.export_audio_file_menubar)
        self.export_menubar.add_command(label='MIDI File',
                                        command=self.export_midi_file)

        self.file_top = ttk.Button(
            self,
            text='File',
            command=lambda: self.file_top_make_menu(mode='file'))
        self.file_menu = Menu(self,
                              tearoff=False,
                              bg=background_color,
                              activebackground=active_background_color,
                              activeforeground=active_foreground_color,
                              disabledforeground=disabled_foreground_color)
        self.file_menu.add_command(label='Open project file',
                                   command=self.open_project_file)
        self.file_menu.add_command(label='Save as project file',
                                   command=self.save_as_project_file)
        self.file_menu.add_command(label='Open MIDI file',
                                   command=self.load_midi_file_func)
        self.file_menu.add_command(label='Save current musicpy code',
                                   command=self.save_current_musicpy_code)
        self.file_menu.add_command(label='Load musicpy code',
                                   command=self.load_musicpy_code)
        self.file_top.place(x=0, y=0)

        self.file_top_options = ttk.Button(
            self,
            text='Options',
            command=lambda: self.file_top_make_menu(mode='options'))
        self.options_menu = Menu(self,
                                 tearoff=False,
                                 bg=background_color,
                                 activebackground=active_background_color,
                                 activeforeground=active_foreground_color,
                                 disabledforeground=disabled_foreground_color)
        self.options_menu.add_command(label='Change settings',
                                      command=self.open_change_settings)
        self.file_top_options.place(x=82, y=0)

        self.file_top_tools = ttk.Button(
            self,
            text='Tools',
            command=lambda: self.file_top_make_menu(mode='tools'))
        self.tools_menu = Menu(self,
                               tearoff=False,
                               bg=background_color,
                               activebackground=active_background_color,
                               activeforeground=active_foreground_color,
                               disabledforeground=disabled_foreground_color)
        self.tools_menu.add_command(label='Make ESI file',
                                    command=self.make_esi_file)
        self.tools_menu.add_command(label='Load ESI file',
                                    command=self.load_esi_file)
        self.tools_menu.add_command(label='Unzip ESI file',
                                    command=self.unzip_esi_file)
        self.file_top_tools.place(x=164, y=0)

        self.current_project_name = ttk.Label(self, text='new.esp')
        self.current_project_name.place(x=0, y=30)

        self.load_musicpy_code_button = ttk.Button(
            self, text='Load musicpy code', command=self.load_musicpy_code)
        self.load_musicpy_code_button.place(x=0, y=550)

        try:
            with open('browse memory.txt', encoding='utf-8-sig') as f:
                self.last_place = f.read()
        except:
            self.last_place = "."

        self.choose_tracks.insert(END, 'Track 1')
        self.track_names = ['Track 1']
        self.track_sound_modules_name = [sound_path]
        self.track_sound_format = ['wav']
        self.track_num = 1
        self.after(10, self.initialize)

    def initialize(self):
        global note_sounds
        global note_sounds_path
        self.msg.configure(text='Loading default sound modules...')
        note_sounds = load(notedict, sound_path, sound_format, global_volume)
        note_sounds_path = load_sounds(note_sounds)
        self.track_sound_modules = [note_sounds]
        self.track_sound_audiosegments = [
            load_audiosegments(notedict, sound_path, sound_format)
        ]
        self.track_note_sounds_path = [note_sounds_path]
        self.track_dict = [notedict]
        self.msg.configure(text='Loading complete')
        self.default_load = True

    def make_esi_file(self):
        self.msg.configure(text='')
        file_path = filedialog.askdirectory(
            initialdir=self.last_place,
            title="Choose the folder of sound files",
        )
        if file_path:
            memory = file_path
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
        else:
            return
        abs_path = os.getcwd()
        filenames = os.listdir(file_path)
        if not filenames:
            self.msg.configure(
                text='There are no sound files to make ESI files')
            return
        length_list = []
        export_path = filedialog.askdirectory(
            initialdir=self.last_place,
            title="Choose the path you want to place ESI and ESS files",
        )
        if not export_path:
            return
        os.chdir(export_path)
        name = os.path.basename(file_path)
        with open(f'{name}.esi', 'wb') as file:
            os.chdir(file_path)
            for t in filenames:
                with open(t, 'rb') as f:
                    each = f.read()
                    length_list.append(len(each))
                    file.write(each)
        os.chdir(export_path)

        with open(f'{name}.ess', 'w', encoding='utf-8-sig') as f:
            f.write(
                str(length_list) + ',' +
                str([os.path.basename(i) for i in filenames]))
        self.msg.configure(
            text=
            f'Successfully made ESI file and ESS file: {name}.esi and {name}.ess'
        )
        os.chdir(abs_path)
        return

    def load_esi_file(self):
        self.msg.configure(text='')
        current_ind = self.choose_tracks.index(ANCHOR)
        if current_ind >= self.track_num:
            self.msg.configure(text='Please select a track first')
            return

        abs_path = os.getcwd()
        file_path = filedialog.askopenfilename(
            initialdir=self.last_place,
            title="Choose ESI file",
            filetype=(("Easy Sampler Instrument", "*.esi"), ("All files",
                                                             "*.*")))
        if file_path:
            memory = file_path[:file_path.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
        else:
            return

        split_file_path = filedialog.askopenfilename(
            initialdir=self.last_place,
            title="Choose ESS file",
            filetype=(("Easy Sampler Split", "*.ess"), ("All files", "*.*")))
        if split_file_path:
            memory = split_file_path[:split_file_path.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
        else:
            return

        self.msg.configure(text=f'Loading {os.path.basename(file_path)} ...')
        self.msg.update()
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
                    track_settings = current.decode('utf-8-sig').replace(
                        '\r', '')
        filenames = [i for i in filenames if i[-4:] != '.txt']
        sound_files_pygame = []
        os.chdir('scripts')
        for each in sound_files:
            with open('temp', 'wb') as f:
                f.write(each)
            sound_files_pygame.append(pygame.mixer.Sound('temp'))
        os.remove('temp')
        os.chdir('..')
        sound_files_audio = [
            AudioSegment.from_file(
                BytesIO(sound_files[i]),
                format=filenames[i][filenames[i].rfind('.') + 1:])
            for i in range(len(sound_files))
        ]
        self.track_dict[current_ind] = copy(notedict)
        if track_settings is not None:
            self.load_track_settings(text=track_settings)
        current_dict = self.track_dict[current_ind]
        filenames = [i[:i.rfind('.')] for i in filenames]
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
        self.track_sound_modules[current_ind] = note_sounds

        self.track_sound_audiosegments[current_ind] = {
            i: (result_audio[current_dict[i]]
                if current_dict[i] in result_audio else None)
            for i in current_dict
        }
        self.track_note_sounds_path[current_ind] = load_sounds(note_sounds)
        self.msg.configure(
            text=f'Successfully loaded {os.path.basename(file_path)}')

    def unzip_esi_file(self):
        self.msg.configure(text='')
        abs_path = os.getcwd()
        file_path = filedialog.askopenfilename(
            initialdir=self.last_place,
            title="Choose ESI file",
            filetype=(("Easy Sampler Instrument", "*.esi"), ("All files",
                                                             "*.*")))
        if file_path:
            memory = file_path[:file_path.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
        else:
            return

        split_file_path = filedialog.askopenfilename(
            initialdir=self.last_place,
            title="Choose ESS file",
            filetype=(("Easy Sampler Split", "*.ess"), ("All files", "*.*")))
        if split_file_path:
            memory = split_file_path[:split_file_path.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
        else:
            return

        with open(split_file_path, 'r', encoding='utf-8-sig') as f:
            unzip = f.read()
        unzip_ind, filenames = literal_eval(unzip)

        export_path = filedialog.askdirectory(
            initialdir=self.last_place,
            title="Choose the folder you want to unzip ESI files to",
        )
        if export_path:
            os.chdir(export_path)
        folder_name = os.path.basename(file_path)
        folder_name = folder_name[:folder_name.rfind('.')]
        if folder_name not in os.listdir():
            os.mkdir(folder_name)
        with open(file_path, 'rb') as file:
            os.chdir(folder_name)
            for each in range(len(filenames)):
                current_filename = filenames[each]
                current_length = unzip_ind[each]
                with open(current_filename, 'wb') as f:
                    f.write(file.read(current_length))
        self.msg.configure(
            text=f'Unzip {os.path.basename(file_path)} successfully')
        os.chdir(abs_path)

    def load_musicpy_code(self):
        filename = filedialog.askopenfilename(initialdir=self.last_place,
                                              title="Choose musicpy code file",
                                              filetype=(("Text", "*.txt"),
                                                        ("All files", "*.*")))
        if filename:
            memory = filename[:filename.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
            try:
                with open(filename, encoding='utf-8-sig',
                          errors='ignore') as f:
                    self.set_musicpy_code_entry.delete('1.0', END)
                    self.set_musicpy_code_entry.insert(END, f.read())
                    self.set_musicpy_code_entry.see(INSERT)
            except:
                self.set_musicpy_code_entry.delete('1.0', END)
                self.msg.configure(text='Not a valid text file')

    def cut(self, editor, event=None):
        editor.event_generate("<<Cut>>")

    def copy(self, editor, event=None):
        editor.event_generate("<<Copy>>")

    def paste(self, editor, event=None):
        editor.event_generate('<<Paste>>')

    def choose_all(self, editor, event=None):
        editor.tag_add(SEL, '1.0', END)
        editor.mark_set(INSERT, END)
        editor.see(INSERT)

    def inputs_undo(self, editor, event=None):
        try:
            editor.edit_undo()
        except:
            pass

    def inputs_redo(self, editor, event=None):
        try:
            editor.edit_redo()
        except:
            pass

    def rightKey(self, event, editor):
        self.menubar.delete(0, END)
        self.menubar.add_command(label='Cut',
                                 command=lambda: self.cut(editor),
                                 foreground=foreground_color)
        self.menubar.add_command(label='Copy',
                                 command=lambda: self.copy(editor),
                                 foreground=foreground_color)
        self.menubar.add_command(label='Paste',
                                 command=lambda: self.paste(editor),
                                 foreground=foreground_color)
        self.menubar.add_command(label='Select all',
                                 command=lambda: self.choose_all(editor),
                                 foreground=foreground_color)
        self.menubar.add_command(label='Undo',
                                 command=lambda: self.inputs_undo(editor),
                                 foreground=foreground_color)
        self.menubar.add_command(label='Redo',
                                 command=lambda: self.inputs_redo(editor),
                                 foreground=foreground_color)
        self.menubar.add_command(
            label='Save',
            command=lambda: self.save_current_musicpy_code(),
            foreground=foreground_color)
        self.menubar.add_command(label='Load',
                                 command=lambda: self.load_musicpy_code(),
                                 foreground=foreground_color)
        self.menubar.add_command(label='Export',
                                 command=lambda: self.open_export_menu(),
                                 foreground=foreground_color)
        self.menubar.post(event.x_root, event.y_root)

    def open_project_file(self):
        if not self.default_load:
            return
        self.msg.configure(text='')
        filename = filedialog.askopenfilename(
            initialdir=self.last_place,
            title="Choose project file",
            filetype=(("Easy Sampler Project", "*.esp"), ("Text", "*.txt"),
                      ("All files", "*.*")))
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
                self.set_musicpy_code_entry.delete('1.0', END)
                self.msg.configure(
                    text='Not a valid text file or easy sampler project file')
                return
        else:
            return
        self.clear_all_tracks(1)
        self.track_num = self.project_dict['track_num']
        self.init_tracks(self.track_num)
        self.track_names = self.project_dict['track_names']
        self.track_sound_modules_name = self.project_dict[
            'track_sound_modules_name']
        self.track_sound_format = self.project_dict['track_sound_format']
        self.track_dict = self.project_dict['track_dict']
        self.current_bpm = self.project_dict['current_bpm']
        self.change_current_bpm_entry.delete(0, END)
        self.change_current_bpm_entry.insert(END, self.current_bpm)
        self.load_midi_file_entry.delete(0, END)
        self.load_midi_file_entry.insert(
            END, self.project_dict['current_midi_file'])
        self.set_musicpy_code_entry.delete('1.0', END)
        self.set_musicpy_code_entry.insert(
            END, self.project_dict['current_musicpy_code'])
        self.current_track_name_label.focus_set()
        for current_ind in range(self.track_num):
            self.choose_tracks.delete(current_ind)
            self.choose_tracks.insert(current_ind,
                                      self.track_names[current_ind])
        for i in range(self.track_num):
            self.reload_track_sounds(i)
        self.current_track_sound_modules_entry.delete(0, END)
        self.choose_tracks.selection_clear(0, END)
        self.current_project_name.configure(text=os.path.basename(filename))
        self.msg.configure(text='Successfully loaded current project file')

    def save_as_project_file(self):
        if not self.default_load:
            return
        self.msg.configure(text='')
        self.project_dict = {}
        self.project_dict['track_num'] = self.track_num
        self.project_dict['track_names'] = self.track_names
        self.project_dict[
            'track_sound_modules_name'] = self.track_sound_modules_name
        self.project_dict['track_sound_format'] = self.track_sound_format
        self.project_dict['track_dict'] = self.track_dict
        self.project_dict['current_bpm'] = self.current_bpm
        self.project_dict['current_midi_file'] = self.load_midi_file_entry.get(
        )
        self.project_dict[
            'current_musicpy_code'] = self.set_musicpy_code_entry.get(
                '1.0', 'end-1c')
        filename = filedialog.asksaveasfilename(
            initialdir=self.last_place,
            title="Save As Project File",
            filetype=(("Easy Sampler Project", "*.esp"), ("Text", "*.txt"),
                      ("All files", "*.*")),
            defaultextension=f".esp",
            initialfile='untitled')
        if filename:
            memory = filename[:filename.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(str(self.project_dict))
            self.msg.configure(text='Successfully saved as project file')

    def save_current_musicpy_code(self):
        filename = filedialog.asksaveasfilename(
            initialdir=self.last_place,
            title="Save Current Musicpy Code",
            filetype=(("All files", "*.*"), ),
            defaultextension=f".txt",
            initialfile='untitled')
        if filename:
            memory = filename[:filename.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write(self.set_musicpy_code_entry.get('1.0', 'end-1c'))

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

    def load_track_settings(self, text=None):
        current_ind = self.choose_tracks.index(ANCHOR)
        if current_ind >= self.track_num:
            return
        if text is None:
            filename = filedialog.askopenfilename(
                initialdir=self.last_place,
                title="Choose Track Settings",
                filetype=(("Text", "*.txt"), ("all files", "*.*")))
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
        current_dict = self.track_dict[current_ind]
        for each in data:
            if ',' in each:
                current_key, current_value = each.split(',')
                current_dict[current_key] = current_value
            elif 'format' in each and '=' in each:
                current_sound_format = each.replace(' ', '').split('=')[1]
                self.track_sound_format[current_ind] = current_sound_format
                self.change_current_sound_format_entry.delete(0, END)
                self.change_current_sound_format_entry.insert(
                    END, current_sound_format)
        self.current_track_dict_num = current_ind
        if text is None:
            self.reload_track_sounds()
            self.msg.configure(
                text=
                f'Successfully load settings \'{os.path.basename(filename)}\' for Track {current_ind+1}'
            )

    def open_export_menu(self):
        self.export_menubar.tk_popup(x=self.winfo_pointerx(),
                                     y=self.winfo_pointery())

    def ask_other_format(self):
        self.ask_other_format_window = Toplevel(self)
        self.ask_other_format_window.configure(bg=background_color)
        self.ask_other_format_window.minsize(370, 200)
        x = self.winfo_x()
        y = self.winfo_y()
        w = self.ask_other_format_window.winfo_width()
        h = self.ask_other_format_window.winfo_height()
        self.ask_other_format_window.geometry("%dx%d+%d+%d" %
                                              (w, h, x + 200, y + 200))
        self.ask_other_format_window.title('Other Format')
        x = self.winfo_x()
        y = self.winfo_y()
        self.ask_other_format_window.geometry("+%d+%d" % (x + 100, y + 140))
        self.ask_other_format_label = ttk.Label(
            self.ask_other_format_window,
            text=
            "Enter a file format, and we'll try to convert if it is supported")
        self.ask_other_format_label.place(x=0, y=50)
        self.ask_other_format_entry = ttk.Entry(self.ask_other_format_window,
                                                width=20)
        self.ask_other_format_entry.place(x=100, y=100)
        self.ask_other_format_ok_button = ttk.Button(
            self.ask_other_format_window,
            text='OK',
            command=self.read_other_format)
        self.ask_other_format_cancel_button = ttk.Button(
            self.ask_other_format_window,
            text='Cancel',
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
                          track_num=0):
        if mode == 'other':
            self.ask_other_format()
            return
        self.msg.configure(text='')
        if not self.track_sound_modules:
            if action == 'export':
                self.msg.configure(
                    text=
                    'You need at least 1 track with loaded sound modules to export audio files'
                )
                return
            elif action == 'play':
                self.msg.configure(
                    text=
                    'You need at least 1 track with loaded sound modules to play'
                )
                return
            elif action == 'get':
                self.msg.configure(
                    text='You need at least 1 track with loaded sound modules')
                return
        if action == 'export':
            filename = filedialog.asksaveasfilename(
                initialdir=self.last_place,
                title="Export Audio File",
                filetype=(("All files", "*.*"), ),
                defaultextension=f".{mode}",
                initialfile='untitled')
            if not filename:
                return
        if action == 'get':
            result = obj
            if type(result) == chord:
                result = ['chord', result, track_num]
            elif type(result) == piece:
                result = ['piece', result]
            else:
                self.msg.configure(
                    text='Must be chord or piece instance to convert to audio')
                return
        else:
            result = self.get_current_musicpy_chords()
        if result is None:
            return
        if action == 'export':
            self.msg.configure(
                text=f'Start to convert current musicpy code to {filename}')
        self.msg.update()
        types = result[0]
        current_chord = result[1]
        self.stop_playing()

        if types == 'chord':
            current_track_num = result[2]
            current_bpm = self.current_bpm
            for each in current_chord:
                if type(each) == AudioSegment:
                    each.duration = self.real_time_to_bar(
                        len(each), current_bpm)
                    each.volume = 127
            apply_fadeout_obj = self.apply_fadeout(current_chord, current_bpm)
            whole_duration = apply_fadeout_obj.eval_time(
                current_bpm, mode='number', audio_mode=1) * 1000
            current_start_times = 0
            current_chord = current_chord.only_notes(audio_mode=1)
            silent_audio = AudioSegment.silent(duration=whole_duration)
            silent_audio = self.track_to_audio(current_chord,
                                               current_track_num,
                                               silent_audio,
                                               current_bpm,
                                               mode=action)
            try:
                if action == 'export':
                    silent_audio.export(filename, format=mode)
                elif action == 'play':
                    self.msg.configure(text=f'Start playing')
                    play_audio(silent_audio)
                elif action == 'get':
                    return silent_audio
            except:
                if action == 'export':
                    self.msg.configure(
                        text=f'Error: {mode} file format is not supported')
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
                each_track = current_chord.tracks[i]
                each_track = each_track.only_notes(audio_mode=1)
                for each in each_track:
                    if type(each) == AudioSegment:
                        each.duration = self.real_time_to_bar(
                            len(each), current_bpm)
                        each.volume = 127
                current_chord.tracks[i] = each_track
            apply_fadeout_obj = self.apply_fadeout(current_chord, current_bpm)
            whole_duration = apply_fadeout_obj.eval_time(
                current_bpm, mode='number', audio_mode=1) * 1000
            silent_audio = AudioSegment.silent(duration=whole_duration)
            for i in range(len(current_chord)):
                silent_audio = self.track_to_audio(current_tracks[i],
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
                    self.msg.configure(text=f'Start playing')
                    play_audio(silent_audio)
                elif action == 'get':
                    return silent_audio
            except:
                if action == 'export':
                    self.msg.configure(
                        text=f'Error: {mode} file format is not supported')
                return
        if action == 'export':
            self.msg.configure(text=f'Successfully export {filename}')

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

    def track_to_audio(self,
                       current_chord,
                       current_track_num=0,
                       silent_audio=None,
                       current_bpm=None,
                       current_pan=None,
                       current_volume=None,
                       current_start_time=0,
                       mode='export'):
        if len(self.track_sound_modules) <= current_track_num:
            self.msg.configure(text=f'Cannot find Track {current_track_num+1}')
            return
        if not self.track_sound_modules[current_track_num]:
            self.msg.configure(
                text=
                f'Track {current_track_num+1} has not loaded any sounds yet')
            return

        apply_fadeout_obj = self.apply_fadeout(current_chord, current_bpm)
        whole_duration = apply_fadeout_obj.eval_time(
            current_bpm, mode='number', audio_mode=1) * 1000
        current_silent_audio = AudioSegment.silent(duration=whole_duration)
        current_intervals = current_chord.interval
        current_durations = current_chord.get_duration()
        current_volumes = current_chord.get_volume()
        current_dict = self.track_dict[current_track_num]
        current_sounds = self.track_sound_audiosegments[current_track_num]
        current_sound_path = self.track_sound_modules_name[current_track_num]
        current_sound_format = self.track_sound_format[current_track_num]
        current_start_time = self.bar_to_real_time(current_start_time,
                                                   current_bpm, 1)
        current_position = 0
        whole_length = len(current_chord)
        if show_convert_progress:
            counter = 1
        for i in range(whole_length):
            if mode == 'export' and show_convert_progress:
                self.msg.configure(
                    text=
                    f'converting progress: {round((counter / whole_length) * 100, 3):.3f}% of track {current_track_num + 1}'
                )
                self.msg.update()
                counter += 1
            each = current_chord.notes[i]
            interval = self.bar_to_real_time(current_intervals[i], current_bpm,
                                             1)
            duration = self.bar_to_real_time(
                current_durations[i], current_bpm,
                1) if type(each) != AudioSegment else len(each)
            volume = velocity_to_db(current_volumes[i])
            current_offset = 0
            if check_offset(each):
                current_offset = self.bar_to_real_time(each.offset,
                                                       current_bpm, 1)
            current_fadeout_time = int(
                duration * export_audio_fadeout_time_ratio
            ) if export_fadeout_use_ratio else int(export_audio_fadeout_time)
            if type(each) == AudioSegment:
                current_sound = each[current_offset:duration]
            else:
                each_name = str(each)
                if each_name not in current_sounds:
                    each_name = str(~each)
                current_sound = current_sounds[each_name]
                current_max_time = min(len(current_sound),
                                       duration + current_fadeout_time)
                current_max_fadeout_time = min(len(current_sound),
                                               current_fadeout_time)
                current_sound = current_sound[current_offset:current_max_time]
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
                    current_sound = current_sound.fade_in(each.fade_in_time)
                if each.fade_out_time > 0:
                    current_sound = current_sound.fade_out(each.fade_out_time)
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
        self.msg.configure(text='')
        filename = filedialog.asksaveasfilename(initialdir=self.last_place,
                                                title="Export MIDI File",
                                                filetype=(("All files",
                                                           "*.*"), ),
                                                defaultextension=f".mid",
                                                initialfile='untitled')
        if not filename:
            return
        result = self.get_current_musicpy_chords()
        if result is None:
            return
        current_chord = result[1]
        self.stop_playing()
        self.msg.configure(
            text=f'Start to convert current musicpy code to {filename}')
        self.msg.update()
        write(filename, current_chord, self.current_bpm)
        self.msg.configure(text=f'Successfully export {filename}')

    def get_current_musicpy_chords(self):
        current_notes = self.set_musicpy_code_entry.get('1.0', 'end-1c')
        current_track_num = 0
        current_bpm = self.current_bpm
        try:
            current_chord = eval(current_notes)
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
                length = len(current_chord)
                if type(current_chord) == tuple and length > 1:
                    if length == 2:
                        current_chord, current_bpm = current_chord
                    elif length == 3:
                        current_chord, current_bpm, current_track_num = current_chord
                        current_track_num -= 1
                    self.change_current_bpm_entry.delete(0, END)
                    self.change_current_bpm_entry.insert(END, current_bpm)
                    self.change_current_bpm(1)
            except Exception as e:
                print(str(e))
                self.msg.configure(
                    text=
                    f'Error: invalid musicpy code or not result in a chord instance'
                )
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
            return 'chord', current_chord, current_track_num
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

    def clear_current_track(self):
        current_ind = self.choose_tracks.index(ANCHOR)
        if current_ind < self.track_num:
            self.choose_tracks.delete(current_ind)
            self.choose_tracks.insert(current_ind, f'Track {current_ind+1}')
            self.track_names[current_ind] = f'Track {current_ind+1}'
            self.track_sound_modules_name[current_ind] = ''
            self.track_sound_modules[current_ind] = None
            self.track_sound_audiosegments[current_ind] = None
            self.track_note_sounds_path[current_ind] = None
            self.track_sound_format[current_ind] = 'wav'
            self.track_dict[current_ind] = copy(notedict)
            self.current_track_name_entry.delete(0, END)
            self.current_track_sound_modules_entry.delete(0, END)
            self.change_current_sound_format_entry.delete(0, END)

    def clear_all_tracks(self, mode=0):
        if_clear = messagebox.askyesnocancel(
            'Clear All Tracks',
            'Are you sure you want to clear all tracks? This will stop current playing.',
            icon='warning') if mode == 0 else True
        if if_clear:
            self.stop_playing()
            self.choose_tracks.delete(0, END)
            self.track_names.clear()
            self.track_sound_modules_name.clear()
            self.track_sound_modules.clear()
            self.track_sound_audiosegments.clear()
            self.track_note_sounds_path.clear()
            self.track_sound_format.clear()
            self.track_dict.clear()
            self.track_num = 0
            self.current_track_name_entry.delete(0, END)
            self.current_track_sound_modules_entry.delete(0, END)
            self.change_current_sound_format_entry.delete(0, END)

    def delete_track(self):
        current_ind = self.choose_tracks.index(ANCHOR)
        if current_ind < self.track_num:
            self.choose_tracks.delete(current_ind)
            new_ind = min(current_ind, self.track_num - 2)
            self.choose_tracks.see(new_ind)
            self.choose_tracks.selection_anchor(new_ind)
            self.choose_tracks.selection_set(new_ind)
            del self.track_names[current_ind]
            del self.track_sound_modules_name[current_ind]
            del self.track_sound_modules[current_ind]
            del self.track_sound_audiosegments[current_ind]
            del self.track_note_sounds_path[current_ind]
            del self.track_sound_format[current_ind]
            del self.track_dict[current_ind]
            self.track_num -= 1
            if self.track_num > 0:
                self.show_current_track()
            else:
                self.current_track_name_entry.delete(0, END)
                self.current_track_sound_modules_entry.delete(0, END)
                self.change_current_sound_format_entry.delete(0, END)

    def add_new_track(self):
        self.track_num += 1
        current_track_name = f'Track {self.track_num}'
        self.choose_tracks.insert(END, current_track_name)
        self.choose_tracks.selection_clear(ANCHOR)
        self.choose_tracks.see(END)
        self.choose_tracks.selection_anchor(END)
        self.choose_tracks.selection_set(END)
        self.track_names.append(current_track_name)
        self.track_sound_modules_name.append('')
        self.track_sound_modules.append(None)
        self.track_sound_audiosegments.append(None)
        self.track_note_sounds_path.append(None)
        self.track_sound_format.append('wav')
        self.track_dict.append(copy(notedict))
        self.show_current_track()

    def init_tracks(self, num=1):
        self.track_num = num
        for i in range(self.track_num):
            current_track_name = f'Track {i}'
            self.choose_tracks.insert(END, current_track_name)
            self.track_names.append(current_track_name)
            self.track_sound_modules_name.append('')
            self.track_sound_modules.append(None)
            self.track_sound_audiosegments.append(None)
            self.track_note_sounds_path.append(None)
            self.track_sound_format.append('wav')
            self.track_dict.append(copy(notedict))

    def change_track_dict(self):
        if self.open_change_track_dict:
            self.change_dict_window.focus_set()
            return
        else:
            current_ind = self.choose_tracks.index(ANCHOR)
            self.current_track_dict_num = current_ind
            if current_ind < self.track_num:
                self.open_change_track_dict = True
                self.change_dict_window = Toplevel(self)
                self.change_dict_window.configure(bg=background_color)
                x = self.winfo_x()
                y = self.winfo_y()
                w = self.change_dict_window.winfo_width()
                h = self.change_dict_window.winfo_height()
                self.change_dict_window.geometry("%dx%d+%d+%d" %
                                                 (w, h, x + 200, y + 200))
                self.change_dict_window.protocol("WM_DELETE_WINDOW",
                                                 self.close_change_dict_window)
                self.change_dict_window.title('Change Track Dictionary')
                self.change_dict_window.minsize(500, 300)
                current_dict = self.track_dict[current_ind]
                self.current_dict = current_dict
                self.dict_configs_bar = Scrollbar(self.change_dict_window)
                self.dict_configs_bar.place(x=150,
                                            y=90,
                                            height=185,
                                            anchor=CENTER)
                self.dict_configs = Listbox(
                    self.change_dict_window,
                    yscrollcommand=self.dict_configs_bar.set,
                    exportselection=False)
                self.dict_configs.bind(
                    '<<ListboxSelect>>',
                    lambda e: self.show_current_dict_configs())
                self.dict_configs_bar.config(command=self.dict_configs.yview)
                self.dict_configs.place(x=0, y=0)
                for each in current_dict:
                    self.dict_configs.insert(END, each)
                self.current_note_name = ttk.Label(self.change_dict_window,
                                                   text='Note Name')
                self.current_note_name.place(x=200, y=0)
                self.current_note_name_entry = ttk.Entry(
                    self.change_dict_window, width=10)
                self.current_note_name_entry.place(x=300, y=0)
                self.current_note_value = ttk.Label(self.change_dict_window,
                                                    text='Note Value')
                self.current_note_value.place(x=200, y=50)
                self.current_note_value_entry = ttk.Entry(
                    self.change_dict_window, width=10)
                self.current_note_value_entry.place(x=300, y=50)
                self.change_current_note_name_button = ttk.Button(
                    self.change_dict_window,
                    text='Change Note Name',
                    command=self.change_current_note_name)
                self.change_current_note_value_button = ttk.Button(
                    self.change_dict_window,
                    text='Change Note Value',
                    command=self.change_current_note_value)
                self.add_new_note_button = ttk.Button(
                    self.change_dict_window,
                    text='Add New Note',
                    command=self.add_new_note)
                self.remove_note_button = ttk.Button(self.change_dict_window,
                                                     text='Remove Note',
                                                     command=self.remove_note)
                self.new_note_name_entry = ttk.Entry(self.change_dict_window,
                                                     width=10)
                self.change_current_note_name_button.place(x=200, y=100)
                self.change_current_note_value_button.place(x=350, y=100)
                self.add_new_note_button.place(x=200, y=150)
                self.new_note_name_entry.place(x=320, y=150)
                self.remove_note_button.place(x=200, y=200)
                self.reload_track_sounds_button = ttk.Button(
                    self.change_dict_window,
                    text='Reload Sound Modules',
                    command=self.reload_track_sounds)
                self.reload_track_sounds_button.place(x=200, y=250)
                self.clear_all_notes_button = ttk.Button(
                    self.change_dict_window,
                    text='Clear All Notes',
                    command=self.clear_all_notes)
                self.clear_all_notes_button.place(x=320, y=200)

    def clear_all_notes(self):
        self.dict_configs.delete(0, END)
        self.current_dict.clear()
        self.current_note_name_entry.delete(0, END)
        self.current_note_value_entry.delete(0, END)

    def close_change_dict_window(self):
        self.change_dict_window.destroy()
        self.open_change_track_dict = False

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
            self.track_dict[self.current_track_dict_num] = self.current_dict
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

    def reload_track_sounds(self, current_ind=None):
        if current_ind is None:
            current_mode = 0
        else:
            current_mode = 1
        self.msg.configure(text='')
        current_ind = self.current_track_dict_num if not current_mode else current_ind
        try:
            self.msg.configure(
                text=
                f'Loading the sounds of {self.track_names[current_ind]} ...')
            self.msg.update()
            sound_path = self.track_sound_modules_name[current_ind]
            notedict = self.track_dict[current_ind]
            sound_format = self.track_sound_format[current_ind]
            note_sounds = load(notedict, sound_path, sound_format,
                               global_volume)
            note_sounds_path = load_sounds(note_sounds)
            self.track_sound_modules[current_ind] = note_sounds
            self.track_sound_audiosegments[current_ind] = load_audiosegments(
                notedict, sound_path, sound_format)
            self.track_note_sounds_path[current_ind] = note_sounds_path
            self.current_track_sound_modules_entry.delete(0, END)
            self.current_track_sound_modules_entry.insert(END, sound_path)
            self.msg.configure(
                text=
                f'The sound path of {self.track_names[current_ind]} has changed'
            )
            if not current_mode:
                self.choose_tracks.see(current_ind)
                self.choose_tracks.selection_anchor(current_ind)
                self.choose_tracks.selection_set(current_ind)
        except Exception as e:
            print(str(e))
            self.msg.configure(
                text=
                f'Error: The sound files in the sound path do not match with settings'
            )

    def show_current_dict_configs(self):
        current_note = self.dict_configs.get(ANCHOR)
        if current_note in self.current_dict:
            self.current_note_name_entry.delete(0, END)
            self.current_note_name_entry.insert(END, current_note)
            self.current_note_value_entry.delete(0, END)
            self.current_note_value_entry.insert(
                END, self.current_dict[current_note])

    def change_current_track_name(self):
        current_ind = self.choose_tracks.index(ANCHOR)
        if current_ind < self.track_num:
            current_track_name = self.current_track_name_entry.get()
            self.choose_tracks.delete(current_ind)
            self.choose_tracks.insert(current_ind, current_track_name)
            self.choose_tracks.see(current_ind)
            self.choose_tracks.selection_anchor(current_ind)
            self.choose_tracks.selection_set(current_ind)
            self.track_names[current_ind] = current_track_name

    def show_current_track(self):
        current_ind = self.choose_tracks.index(ANCHOR)
        if current_ind < self.track_num:
            self.current_track_name_entry.delete(0, END)
            self.current_track_name_entry.insert(END,
                                                 self.track_names[current_ind])
            self.current_track_sound_modules_entry.delete(0, END)
            self.current_track_sound_modules_entry.insert(
                END, self.track_sound_modules_name[current_ind])
            self.change_current_sound_format_entry.delete(0, END)
            self.change_current_sound_format_entry.insert(
                END, self.track_sound_format[current_ind])

    def load_midi_file_func(self):
        self.msg.configure(text='')
        filename = filedialog.askopenfilename(initialdir=self.last_place,
                                              title="Choose MIDI File",
                                              filetype=(("MIDI", "*.mid"),
                                                        ("All files", "*.*")))
        if filename:
            memory = filename[:filename.rindex('/') + 1]
            with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                f.write(memory)
            self.last_place = memory
            self.load_midi_file_entry.delete(0, END)
            self.load_midi_file_entry.insert(END, filename)
            self.set_musicpy_code_entry.delete('1.0', END)
            current_midi_file = read(filename)
            self.change_current_bpm_entry.delete(0, END)
            self.change_current_bpm_entry.insert(END, current_midi_file[0])
            self.change_current_bpm(1)
            self.set_musicpy_code_entry.insert(
                END, f'read("{filename}", mode="all", merge=True)[1]')
            self.msg.configure(
                text=
                f'The MIDI file is loaded, please click Play Musicpy Code button to play'
            )

    def change_current_sound_format(self):
        current_ind = self.choose_tracks.index(ANCHOR)
        if current_ind < self.track_num:
            self.msg.configure(text='')
            current_sound_format = self.change_current_sound_format_entry.get()
            self.track_sound_format[current_ind] = current_sound_format
            self.msg.configure(
                text=
                f'Set sound format of Track {current_ind+1} to {current_sound_format}'
            )
            self.choose_tracks.see(current_ind)
            self.choose_tracks.selection_anchor(current_ind)
            self.choose_tracks.selection_set(current_ind)

    def change_current_sound_path(self, mode=0):
        current_ind = self.choose_tracks.index(ANCHOR)
        if current_ind < self.track_num:
            self.msg.configure(text='')
            if mode == 0:
                directory = filedialog.askdirectory(
                    initialdir=self.last_place,
                    title="Choose Sound Path",
                )
            else:
                directory = self.current_track_sound_modules_entry.get()
            if directory:
                memory = directory
                with open('browse memory.txt', 'w', encoding='utf-8-sig') as f:
                    f.write(memory)
                self.last_place = memory
                try:
                    self.msg.configure(
                        text=
                        f'Loading the sounds of {self.track_names[current_ind]} ...'
                    )
                    self.msg.update()
                    sound_path = directory
                    notedict = self.track_dict[current_ind]
                    sound_format = self.track_sound_format[current_ind]
                    note_sounds = load(notedict, sound_path, sound_format,
                                       global_volume)
                    note_sounds_path = load_sounds(note_sounds)
                    self.track_sound_modules[current_ind] = note_sounds
                    self.track_sound_audiosegments[
                        current_ind] = load_audiosegments(
                            notedict, sound_path, sound_format)
                    self.track_note_sounds_path[current_ind] = note_sounds_path
                    self.track_sound_modules_name[current_ind] = sound_path
                    self.current_track_sound_modules_entry.delete(0, END)
                    self.current_track_sound_modules_entry.insert(
                        END, sound_path)
                    self.msg.configure(
                        text=
                        f'The sound path of {self.track_names[current_ind]} has changed'
                    )
                    self.choose_tracks.see(current_ind)
                    self.choose_tracks.selection_anchor(current_ind)
                    self.choose_tracks.selection_set(current_ind)
                except Exception as e:
                    print(str(e))
                    self.msg.configure(
                        text=
                        f'Error: The sound files in the sound path do not match with settings'
                    )

    def bar_to_real_time(self, bar, bpm, mode=0):
        # return time in ms
        return int((60000 / bpm) *
                   (bar * 4)) if mode == 0 else (60000 / bpm) * (bar * 4)

    def real_time_to_bar(self, time, bpm):
        return (time / (60000 / bpm)) / 4

    def change_current_bpm(self, mode=0):
        self.msg.configure(text='')
        current_bpm = self.change_current_bpm_entry.get()
        try:
            current_bpm = float(current_bpm)
            self.current_bpm = current_bpm
            if mode == 0:
                self.msg.configure(text=f'Set BPM to {current_bpm}')
        except:
            if mode == 0:
                self.msg.configure(text=f'Error: invalid BPM')

    def play_note_func(self, name, duration, volume, track=0):
        note_sounds_path = self.track_note_sounds_path[track]
        note_sounds = self.track_sound_modules[track]
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
        self.msg.configure(text='')
        if not self.track_sound_modules:
            self.msg.configure(
                text=
                'You need at least 1 track with loaded sound modules to play')
            return

        self.stop_playing()
        current_notes = self.set_musicpy_code_entry.get('1.0', 'end-1c')
        current_track_num = 0
        current_bpm = self.current_bpm
        if 'current_chord' in globals():
            del globals()['current_chord']
        try:
            current_chord = eval(current_notes)
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
                length = len(current_chord)
                if type(current_chord) == tuple and length > 1:
                    if length == 2:
                        current_chord, current_bpm = current_chord
                    elif length == 3:
                        current_chord, current_bpm, current_track_num = current_chord
                        current_track_num -= 1
                    self.change_current_bpm_entry.delete(0, END)
                    self.change_current_bpm_entry.insert(END, current_bpm)
                    self.change_current_bpm(1)
            except Exception as e:
                print(str(e))
                self.msg.configure(
                    text=
                    f'Error: invalid musicpy code or not result in a chord instance'
                )
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
            if check_special(current_chord):
                self.export_audio_file(action='play')
            else:
                self.play_track(current_chord, current_track_num)
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
            if check_special(current_chord):
                self.export_audio_file(action='play')
                return
            current_tracks = current_chord.tracks
            current_track_nums = current_chord.channels if current_chord.channels else [
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
                    lambda each=each: self.play_track(current_tracks[
                        each], current_track_nums[each]))
                self.piece_playing.append(current_id)
        self.msg.configure(text=f'Start playing')

    def play_track(self, current_chord, current_track_num=0):
        if len(self.track_sound_modules) <= current_track_num:
            self.msg.configure(text=f'Cannot find Track {current_track_num+1}')
            return
        if not self.track_sound_modules[current_track_num]:
            self.msg.configure(
                text=
                f'Track {current_track_num+1} has not loaded any sounds yet')
            return
        current_chord = current_chord.only_notes()
        current_intervals = current_chord.interval
        current_durations = current_chord.get_duration()
        current_volumes = current_chord.get_volume()
        current_time = 0
        for i in range(len(current_chord)):
            each = current_chord.notes[i]
            if i == 0:
                self.play_note_func(f'{standardize_note(each.name)}{each.num}',
                                    current_durations[i], current_volumes[i],
                                    current_track_num)
            else:
                duration = current_durations[i]
                volume = current_volumes[i]
                current_time += self.bar_to_real_time(current_intervals[i - 1],
                                                      self.current_bpm, 1)
                current_id = self.after(
                    int(current_time),
                    lambda each=each, duration=duration, volume=volume: self.
                    play_note_func(f'{standardize_note(each.name)}{each.num}',
                                   duration, volume, current_track_num))
                self.current_playing.append(current_id)

    def play_current_chord(self):
        if not self.default_load:
            return
        self.msg.configure(text='')
        current_notes = self.set_chord_entry.get('1.0', 'end-1c')
        if ',' in current_notes:
            current_notes = current_notes.replace(' ', '').split(',')
        else:
            current_notes = current_notes.replace('  ', ' ').split(' ')
        try:
            current_notes = chord(current_notes)
            self.msg.configure(text=f'Start playing notes')
        except:
            self.msg.configure(text=f'Error: invalid notes')
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
        with open('change_settings.pyw') as f:
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
