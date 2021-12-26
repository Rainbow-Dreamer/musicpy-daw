import traceback

with open('scripts/settings.py', encoding='utf-8-sig') as f:
    exec(f.read())


class esi:
    def __init__(self, samples, settings=None, name_mappings=None):
        self.samples = samples
        self.settings = settings
        self.name_mappings = name_mappings
        self.file_names = {os.path.splitext(i)[0]: i for i in self.samples}

    def __getitem__(self, ind):
        if self.name_mappings:
            if ind in self.name_mappings:
                return self.samples[self.name_mappings[ind]]
        if ind in self.samples:
            return self.samples[ind]
        if ind in self.file_names:
            return self.samples[self.file_names[ind]]


class effect:
    def __init__(self, func, name=None, *args, unknown_args=None, **kwargs):
        self.func = func
        if name is None:
            name = 'effect'
        self.name = name
        self.parameters = [args, kwargs]
        if unknown_args is None:
            unknown_args = {}
        self.unknown_args = unknown_args

    def process(self, sound, *args, unknown_args=None, **kwargs):
        if args or kwargs or unknown_args:
            return self.func(*args, **kwargs, **unknown_args)
        else:
            return self.func(sound, *self.parameters[0], **self.parameters[1],
                             **self.unknown_args)

    def process_unknown_args(self, **kwargs):
        for each in kwargs:
            if each in self.unknown_args:
                self.unknown_args[each] = kwargs[each]

    def __call__(self, *args, unknown_args=None, **kwargs):
        temp = copy(self)
        temp.parameters[0] = args + temp.parameters[0][len(args):]
        temp.parameters[1].update(kwargs)
        if unknown_args is None:
            unknown_args = {}
        temp.unknown_args.update(unknown_args)
        return temp

    def new(self, *args, unknown_args=None, **kwargs):
        temp = copy(self)
        temp.parameters = [args, kwargs]
        temp.parameters[1].update(kwargs)
        if unknown_args is None:
            unknown_args = {}
        temp.unknown_args = unknown_args
        return temp

    def __repr__(self):
        return f'[effect]\nname: {self.name}\nparameters: {self.parameters} unknown arguments: {self.unknown_args}'


class effect_chain:
    def __init__(self, *effects):
        self.effects = list(effects)

    def __call__(self, sound):
        sound.effects = self.effects
        return sound

    def __repr__(self):
        return f'[effect chain]\neffects:\n' + '\n\n'.join(
            [str(i) for i in self.effects])


class pitch:
    def __init__(self, path, note='C5'):
        self.note = N(note) if isinstance(note, str) else note
        audio_load = False
        if not isinstance(path, AudioSegment):
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
            if not isinstance(path, AudioSegment):
                self.audio = librosa.load(path, sr=self.sample_rate)[0]
            else:
                os.chdir(abs_path)
                path.export('scripts/temp.wav', format='wav')
                self.audio = librosa.load('scripts/temp.wav',
                                          sr=path.frame_rate)[0]
                os.remove('scripts/temp.wav')
            audio_load = True

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
            result = result.set_frame_rate(44100)
        return result

    def __add__(self, semitones):
        return self.pitch_shift(semitones)

    def __sub__(self, semitones):
        return self.pitch_shift(-semitones)

    def get(self, pitch):
        if not isinstance(pitch, note):
            pitch = N(pitch)
        semitones = pitch.degree - self.note.degree
        return self + semitones

    def set_note(self, pitch):
        if not isinstance(pitch, note):
            pitch = N(pitch)
        self.note = pitch

    def generate_dict(self,
                      start='A0',
                      end='C8',
                      mode='librosa',
                      pitch_shifter=False):
        if not isinstance(start, note):
            start = N(start)
        if not isinstance(end, note):
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
        pygame.mixer.stop()


class sound:
    def __init__(self, path):
        if not isinstance(path, AudioSegment):
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

    def stop(self):
        pygame.mixer.stop()


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Easy Sampler")
        self.minsize(1100, 670)
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

        self.set_musicpy_code_button = ttk.Button(
            self,
            text='Play Musicpy Code',
            command=self.play_current_musicpy_code)
        self.set_musicpy_code_button.place(x=0, y=310)
        self.set_musicpy_code_text = Text(self,
                                          width=115,
                                          height=10,
                                          wrap='none',
                                          undo=True,
                                          autoseparators=True,
                                          maxundo=-1,
                                          font=(font_type, font_size))
        self.set_musicpy_code_text.place(x=150, y=250, height=335)
        inputs_v = ttk.Scrollbar(self,
                                 orient="vertical",
                                 command=self.set_musicpy_code_text.yview)
        inputs_h = ttk.Scrollbar(self,
                                 orient="horizontal",
                                 command=self.set_musicpy_code_text.xview)
        self.set_musicpy_code_text.configure(yscrollcommand=inputs_v.set,
                                             xscrollcommand=inputs_h.set)
        inputs_v.place(x=960, y=250, height=335)
        inputs_h.place(x=150, y=585, width=810)

        self.current_line_number = 1
        self.current_column_number = 1
        self.line_column = ttk.Label(
            self,
            text=
            f'Line {self.current_line_number} Col {self.current_column_number}'
        )
        self.line_column.place(x=780, y=630)
        self.get_current_line_column()

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
        self.stop_button.place(x=0, y=360)

        self.change_current_bpm_button = ttk.Button(
            self, text='Change BPM', command=self.change_current_bpm)
        self.change_current_bpm_button.place(x=0, y=210)
        self.change_current_bpm_entry = ttk.Entry(self,
                                                  width=10,
                                                  font=(font_type, font_size))
        self.change_current_bpm_entry.insert(END, '120')
        self.change_current_bpm_entry.place(x=100, y=210)
        self.current_bpm = 120
        self.current_playing = []

        self.msg = ttk.Label(self, text='')
        self.msg.place(x=130, y=630)

        self.change_current_sound_path_button = ttk.Button(
            self,
            text='Change Sound Path',
            command=self.change_current_sound_path)
        self.change_current_sound_path_button.place(x=550, y=210)

        self.load_midi_file_button = ttk.Button(
            self, text='Import MIDI File', command=self.load_midi_file_func)
        self.load_midi_file_button.place(x=590, y=60)
        self.load_midi_file_entry = ttk.Entry(self,
                                              width=50,
                                              font=(font_type, font_size))
        self.load_midi_file_entry.insert(END, '')
        self.load_midi_file_entry.bind(
            '<Return>', lambda e: self.load_midi_file_func(mode=1))
        self.load_midi_file_entry.place(x=720, y=60)

        self.change_settings_button = ttk.Button(
            self, text='Change Settings', command=self.open_change_settings)
        self.change_settings_button.place(x=0, y=460)
        self.open_settings = False

        self.open_debug_window_button = ttk.Button(
            self, text='Open Debug Window', command=self.open_debug_window)
        self.open_debug_window_button.place(x=0, y=510)
        self.is_open_debug_window = False

        self.choose_channels_bar = Scrollbar(self)
        self.choose_channels_bar.place(x=227, y=125, height=125, anchor=CENTER)
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
        self.choose_channels.place(x=0, y=62, width=220, height=125)
        self.choose_channels_bar.config(command=self.choose_channels.yview)

        self.current_channel_name_label = ttk.Label(self, text='Channel Name')
        self.current_channel_name_entry = ttk.Entry(self,
                                                    width=30,
                                                    font=(font_type,
                                                          font_size))
        self.current_channel_name_label.place(x=250, y=60)
        self.current_channel_name_entry.place(x=350, y=60)
        self.current_channel_name_entry.bind(
            '<Return>', lambda e: self.change_current_channel_name())
        self.current_channel_sound_modules_label = ttk.Label(
            self, text='Channel Sound Modules')
        self.current_channel_sound_modules_entry = ttk.Entry(self,
                                                             width=90,
                                                             font=(font_type,
                                                                   font_size))
        self.current_channel_sound_modules_entry.bind(
            '<Return>', lambda e: self.change_current_sound_path_func())
        self.current_channel_sound_modules_label.place(x=250, y=110)
        self.current_channel_sound_modules_entry.place(x=410, y=110)

        self.change_current_channel_name_button = ttk.Button(
            self,
            text='Change Channel Name',
            command=self.change_current_channel_name)
        self.change_current_channel_name_button.place(x=550, y=160)

        self.add_new_channel_button = ttk.Button(self,
                                                 text='Add New Channel',
                                                 command=self.add_new_channel)
        self.add_new_channel_button.place(x=250, y=160)

        self.delete_new_channel_button = ttk.Button(
            self, text='Delete Channel', command=self.delete_channel)
        self.delete_new_channel_button.place(x=400, y=160)

        self.clear_all_channels_button = ttk.Button(
            self, text='Clear All Channels', command=self.clear_all_channels)
        self.clear_all_channels_button.place(x=250, y=210)

        self.clear_channel_button = ttk.Button(
            self, text='Clear Channel', command=self.clear_current_channel)
        self.clear_channel_button.place(x=400, y=210)

        self.change_channel_dict_button = ttk.Button(
            self, text='Change Channel Dict', command=self.change_channel_dict)
        self.change_channel_dict_button.place(x=700, y=160)

        self.load_channel_settings_button = ttk.Button(
            self,
            text='Load Channel Settings',
            command=self.load_channel_settings)
        self.load_channel_settings_button.place(x=700, y=210)

        self.configure_sf2_button = ttk.Button(self,
                                               text='Configure Soundfonts',
                                               command=self.configure_sf2_file)
        self.configure_sf2_button.place(x=870, y=210)

        self.load_sf2_button = ttk.Button(self,
                                          text='Load Soundfonts',
                                          command=self.load_sf2_file)
        self.load_sf2_button.place(x=870, y=160)

        self.piece_playing = []

        self.open_change_channel_dict = False
        self.open_pitch_shifter_window = False
        self.open_configure_sf2_file = False

        self.export_button = ttk.Button(self,
                                        text='Export',
                                        command=self.open_export_menu)
        self.export_button.place(x=0, y=260)

        self.current_project_name = ttk.Label(self, text='untitled.esp')
        self.current_project_name.place(x=0, y=30)
        self.project_name = 'untitled.esp'
        self.opening_project_name = None

        self.load_musicpy_code_button = ttk.Button(
            self, text='Import musicpy code', command=self.load_musicpy_code)
        self.load_musicpy_code_button.place(x=0, y=410)

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
        self.file_menu.add_command(label=self.language_dict['file'][7],
                                   command=self.open_new_project_file)
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
        self.show_msg(self.language_dict['msg'][0])
        self.channel_sound_modules = [load_audiosegments(notedict, sound_path)]
        self.channel_dict = [notedict]
        self.show_msg(self.language_dict['msg'][1])
        self.default_load = True

    def get_current_line_column(self):
        ind = self.set_musicpy_code_text.index(INSERT)
        line, column = ind.split('.')
        self.current_line_number = int(line)
        self.current_column_number = int(column)
        self.line_column.config(
            text=
            f'Line {self.current_line_number} Col {self.current_column_number}'
        )
        self.after(10, self.get_current_line_column)

    def open_new_project_file(self):
        self.current_project_name.configure(text='untitled.esp')
        self.project_name = 'untitled.esp'
        self.opening_project_name = None
        self.clear_all_channels(1)
        self.set_musicpy_code_text.delete('1.0', END)
        self.choose_channels.insert(END, self.language_dict['init'][0])
        self.channel_names = [self.language_dict['init'][0]]
        self.channel_sound_modules_name = [sound_path]
        self.channel_num = 1
        self.channel_list_focus = True
        self.change_current_bpm_entry.delete(0, END)
        self.change_current_bpm_entry.insert(END, '120')
        self.change_current_bpm_entry.place(x=100, y=210)
        self.current_bpm = 120
        self.initialize()

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
            print(traceback.format_exc())
            output(traceback.format_exc())
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
            play_audio(self.current_pitch)
            self.pitch_shifter_playing = True

    def pitch_shifter_stop(self):
        if self.pitch_shifter_playing:
            pygame.mixer.stop()
            self.pitch_shifter_playing = False

    def pitch_shifter_play_shifted(self):
        if self.pitch_shifter_window.has_load:
            if self.pitch_shifter_shifted_playing:
                self.pitch_shifter_stop_shifted()
            play_audio(self.new_pitch)
            self.pitch_shifter_shifted_playing = True

    def pitch_shifter_stop_shifted(self):
        if self.pitch_shifter_shifted_playing:
            pygame.mixer.stop()
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
            print(traceback.format_exc())
            output(traceback.format_exc())
            self.pitch_msg(self.language_dict["msg"][40])

    def close_pitch_shifter_window(self):
        self.pitch_shifter_window.destroy()
        self.open_pitch_shifter_window = False

    def close_debug_window(self):
        self.debug_window.destroy()
        self.is_open_debug_window = False

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
        current_channel_num = 0
        current_bpm = self.current_bpm
        current_globals = globals()
        if 'easy_sampler_current_chord' in current_globals:
            del current_globals['easy_sampler_current_chord']
        current_codes = self.set_musicpy_code_text.get('1.0', 'end-1c')
        try:
            exec(current_codes, current_globals, current_globals)
        except:
            pass
        lines = current_notes.split('\n')
        find_command = False
        for k in range(len(lines)):
            each = lines[k]
            if each.startswith('play '):
                find_command = True
                lines[k] = 'easy_sampler_current_chord = ' + each[5:]
            elif each.startswith('play(') or each.startswith(
                    'export(') or each.startswith('play_midi('):
                find_command = True
        if not find_command:
            current_notes = f'easy_sampler_current_chord = {current_notes}'
        else:
            current_notes = '\n'.join(lines)
        try:
            exec(current_notes, current_globals, current_globals)
        except Exception as e:
            print(traceback.format_exc())
            if not global_play:
                self.show_msg(self.language_dict["msg"][4])
                output(traceback.format_exc())
            return
        if 'easy_sampler_current_chord' in current_globals:
            current_chord = current_globals['easy_sampler_current_chord']
        else:
            return
        if isinstance(current_chord, tuple):
            length = len(current_chord)
            if length > 1:
                if length == 2:
                    current_chord, current_bpm = current_chord
                elif length == 3:
                    current_chord, current_bpm, current_channel_num = current_chord
                self.change_current_bpm_entry.delete(0, END)
                self.change_current_bpm_entry.insert(END, current_bpm)
                self.change_current_bpm(1)
        if current_chord is not None:
            self.stop_playing()
            self.play_musicpy_sounds(current_chord,
                                     current_bpm,
                                     current_channel_num,
                                     inner=False)

    def play_selected_audio(self):
        if not self.default_load:
            return
        self.show_msg('')
        try:
            current_notes = self.set_musicpy_code_text.selection_get()
        except:
            return
        current_globals = globals()
        current_codes = self.set_musicpy_code_text.get('1.0', 'end-1c')
        try:
            exec(current_codes, current_globals, current_globals)
        except:
            pass
        try:
            current_audio = eval(current_notes, globals(), globals())
            pygame.mixer.stop()
            play_audio(current_audio)
        except Exception as e:
            print(traceback.format_exc())
            output(traceback.format_exc())
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

    def load_esi_file(self, mode=0, current_ind=None, file_path=None):
        self.show_msg('')
        if current_ind is None:
            current_ind = self.choose_channels.index(ANCHOR)
        if current_ind >= self.channel_num or not self.channel_list_focus:
            self.show_msg(self.language_dict['msg'][8])
            return
        abs_path = os.getcwd()
        if file_path is None:
            if mode == 0:
                file_path = filedialog.askopenfilename(
                    initialdir=self.last_place,
                    title=self.language_dict['title'][7],
                    filetypes=(("Easy Sampler Instrument", "*.esi"),
                               (self.language_dict['title'][1], "*.*")))
                if file_path:
                    memory = file_path[:file_path.rindex('/') + 1]
                    with open('browse memory.txt', 'w',
                              encoding='utf-8-sig') as f:
                        f.write(memory)
                    self.last_place = memory
                else:
                    return
            else:
                file_path = self.current_channel_sound_modules_entry.get()

        self.show_msg(
            f'{self.language_dict["msg"][9]}{os.path.basename(file_path)} ...')
        self.msg.update()
        with open(file_path, 'rb') as file:
            current_esi = pickle.load(file)
        channel_settings = current_esi.settings
        current_samples = current_esi.samples
        filenames = list(current_samples.keys())
        sound_files_audio = [
            AudioSegment.from_file(BytesIO(current_samples[i]),
                                   format=os.path.splitext(i)[1]
                                   [1:]).set_frame_rate(44100).set_channels(2)
            for i in filenames
        ]
        self.channel_dict[current_ind] = copy(notedict)
        if channel_settings is not None:
            self.load_channel_settings(text=channel_settings)
        current_dict = self.channel_dict[current_ind]
        filenames = [os.path.splitext(i)[0] for i in filenames]
        result_audio = {
            filenames[i]: sound_files_audio[i]
            for i in range(len(filenames))
        }
        self.channel_sound_modules[current_ind] = {
            i: (result_audio[current_dict[i]]
                if current_dict[i] in result_audio else None)
            for i in current_dict
        }
        self.channel_sound_modules_name[current_ind] = file_path
        self.current_channel_sound_modules_entry.delete(0, END)
        self.current_channel_sound_modules_entry.insert(END, file_path)
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

    def open_project_file(self, filename=None):
        if not self.default_load:
            return
        self.show_msg('')
        if not filename:
            filename = filedialog.askopenfilename(
                initialdir=self.last_place,
                title=self.language_dict['title'][12],
                filetypes=(("Easy Sampler Project", "*.esp"),
                           (self.language_dict['title'][11],
                            "*.txt"), (self.language_dict['title'][1], "*.*")))
        if filename:
            if '/' in filename:
                memory = filename[:filename.rindex('/') + 1]
            else:
                memory = filename[:filename.rindex('\\') + 1]
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
            os.chdir(os.path.dirname(filename))
            try:
                with open('browse memory.txt', encoding='utf-8-sig') as f:
                    self.last_place = f.read()
            except:
                pass
        else:
            return
        self.default_load = False
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
            current_sf2 = self.channel_sound_modules[each]
            if current_sf2:
                current_sf2_info = current_soundfonts[each]
                current_bank = current_sf2_info[2]
                current_sf2.change_bank(current_bank)
                try:
                    current_sf2.current_preset_name, current_sf2.current_preset_ind = current_sf2.get_all_instrument_names(
                        get_ind=True, mode=1, return_mode=1)
                except:
                    current_sf2.current_preset_name, current_sf2.current_preset_ind = [], []
                current_sf2.change(*current_sf2_info)
        self.show_msg(self.language_dict["msg"][14])
        self.default_load = True

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
            if isinstance(current_sound_modules, rs.sf2_loader):
                current_info = [
                    current_sound_modules.current_channel,
                    current_sound_modules.current_sfid,
                    current_sound_modules.current_bank,
                    current_sound_modules.current_preset
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
            title=self.language_dict['title'][13]
            if new else self.language_dict['title'][20],
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
        if current_ind < self.channel_num and (self.channel_list_focus or
                                               (current_ind is not None)):
            self.show_msg('')
            if sound_path is not None:
                self.show_msg(
                    f'{self.language_dict["msg"][33]}{self.channel_names[current_ind]} ...'
                )
                self.msg.update()
                current_sf2 = rs.sf2_loader(sound_path)
                current_sf2.all_instruments_dict = current_sf2.all_instruments(
                )
                current_sf2.all_available_banks = list(
                    current_sf2.all_instruments_dict.keys())
                try:
                    current_sf2.current_preset_name, current_sf2.current_preset_ind = current_sf2.get_all_instrument_names(
                        get_ind=True, return_mode=1)
                except:
                    current_sf2.current_preset_name, current_sf2.current_preset_ind = [], []
                self.channel_sound_modules[current_ind] = current_sf2
                self.channel_sound_modules_name[current_ind] = sound_path
                current_msg = self.language_dict["msg"][29].split('|')
                self.show_msg(
                    f'{current_msg[0]}{self.channel_names[current_ind]}{current_msg[1]}'
                )
            else:
                if mode == 0:
                    filename = filedialog.askopenfilename(
                        initialdir=self.last_place,
                        title=self.language_dict['title'][19],
                        filetypes=(("Soundfont", ["*.sf2", "*.sf3", "*.dls"]),
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
                        current_sf2 = rs.sf2_loader(sound_path)
                        current_sf2.all_instruments_dict = current_sf2.all_instruments(
                        )
                        current_sf2.all_available_banks = list(
                            current_sf2.all_instruments_dict.keys())
                        try:
                            current_sf2.current_preset_name, current_sf2.current_preset_ind = current_sf2.get_all_instrument_names(
                                get_ind=True, return_mode=1)
                        except:
                            current_sf2.current_preset_name, current_sf2.current_preset_ind = [], []
                        self.channel_sound_modules[current_ind] = current_sf2
                        self.channel_sound_modules_name[
                            current_ind] = sound_path
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
                        print(traceback.format_exc())
                        output(traceback.format_exc())
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
                if not isinstance(current_sf2, rs.sf2_loader):
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
                self.configure_sf2_file_window.minsize(700, 300)
                self.configure_sf2_file_window.focus_set()

                self.preset_configs_bar = Scrollbar(
                    self.configure_sf2_file_window)
                self.preset_configs_bar.place(x=367,
                                              y=120,
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
                self.preset_configs.place(x=200, y=30, height=185, width=160)

                self.bank_configs_bar = Scrollbar(
                    self.configure_sf2_file_window)
                self.bank_configs_bar.place(x=167,
                                            y=120,
                                            height=185,
                                            anchor=CENTER)
                self.bank_configs = Listbox(
                    self.configure_sf2_file_window,
                    yscrollcommand=self.bank_configs_bar.set,
                    exportselection=False,
                    font=(font_type, font_size))
                self.bank_configs.config(activestyle='none')
                self.bank_configs.bind(
                    '<<ListboxSelect>>',
                    lambda e: self.show_current_bank_configs())
                self.bank_configs_bar.config(command=self.bank_configs.yview)
                self.bank_configs.place(x=0, y=30, height=185, width=160)

                self.current_all_available_banks = current_sf2.all_available_banks
                self.current_preset_ind = current_sf2.current_preset_ind

                for each in current_sf2.current_preset_name:
                    self.preset_configs.insert(END, each)
                for each in current_sf2.all_available_banks:
                    self.bank_configs.insert(END, each)
                self.current_bank = ttk.Label(
                    self.configure_sf2_file_window,
                    text=self.language_dict['configure_sf2'][1])
                self.current_bank.place(x=400, y=30)
                self.current_bank_entry = ttk.Entry(
                    self.configure_sf2_file_window,
                    width=10,
                    font=(font_type, font_size))
                self.current_bank_entry.insert(END,
                                               str(current_sf2.current_bank))
                self.current_bank_entry.place(x=500, y=30)
                self.current_preset = ttk.Label(
                    self.configure_sf2_file_window,
                    text=self.language_dict['configure_sf2'][2])
                self.current_preset.place(x=400, y=80)
                self.current_preset_entry = ttk.Entry(
                    self.configure_sf2_file_window,
                    width=10,
                    font=(font_type, font_size))
                self.current_preset_entry.insert(
                    END, str(current_sf2.current_preset + 1))
                self.current_preset_entry.place(x=500, y=80)
                if current_sf2.current_preset in current_sf2.current_preset_ind:
                    current_preset_ind = current_sf2.current_preset_ind.index(
                        current_sf2.current_preset)
                    self.preset_configs.selection_clear(0, END)
                    self.preset_configs.selection_set(current_preset_ind)
                    self.preset_configs.see(current_preset_ind)
                    self.bank_configs.selection_clear(0, END)
                    self.bank_configs.selection_set(
                        current_sf2.all_available_banks.index(
                            current_sf2.current_bank))
                    self.bank_configs.see(current_preset_ind)
                self.change_current_bank_button = ttk.Button(
                    self.configure_sf2_file_window,
                    text=self.language_dict['configure_sf2'][3],
                    command=self.change_current_bank)
                self.change_current_preset_button = ttk.Button(
                    self.configure_sf2_file_window,
                    text=self.language_dict['configure_sf2'][4],
                    command=self.change_current_preset)
                self.listen_preset_button = ttk.Button(
                    self.configure_sf2_file_window,
                    text=self.language_dict['configure_sf2'][5],
                    command=self.listen_preset)
                self.change_current_bank_button.place(x=400, y=130)
                self.change_current_preset_button.place(x=520, y=130)
                self.listen_preset_button.place(x=400, y=180)
                self.preset_label = ttk.Label(self.configure_sf2_file_window,
                                              text='Presets')
                self.preset_label.place(x=200, y=0)
                self.bank_label = ttk.Label(self.configure_sf2_file_window,
                                            text='Banks')
                self.bank_label.place(x=0, y=0)

    def change_current_bank(self, mode=0):
        current_ind = self.choose_channels.index(ANCHOR)
        if mode == 0:
            current_bank = self.current_bank_entry.get()
            if not current_bank.isdigit():
                return
            else:
                current_bank = int(current_bank)
        elif mode == 1:
            current_bank_ind = self.bank_configs.index(ANCHOR)
            current_bank = self.current_all_available_banks[current_bank_ind]
        current_sf2 = self.channel_sound_modules[current_ind]
        if current_bank == current_sf2.current_bank:
            return
        current_sf2.change(bank=current_bank, preset=0, correct=False)
        try:
            current_sf2.current_preset_name, current_sf2.current_preset_ind = current_sf2.get_all_instrument_names(
                get_ind=True, mode=1, return_mode=1)
        except:
            current_sf2.current_preset_name, current_sf2.current_preset_ind = [], []
        self.current_preset_ind = current_sf2.current_preset_ind
        self.current_preset_entry.delete(0, END)
        self.current_preset_entry.insert(
            END, '1' if not current_sf2.current_preset_ind else
            str(current_sf2.current_preset_ind[0] + 1))
        self.preset_configs.delete(0, END)
        for each in current_sf2.current_preset_name:
            self.preset_configs.insert(END, each)
        self.preset_configs.selection_clear(0, END)
        self.preset_configs.selection_set(0)
        self.preset_configs.see(0)

    def change_current_preset(self, mode=0):
        current_ind = self.choose_channels.index(ANCHOR)
        if mode == 1:
            current_preset = str(self.current_preset_ind[
                self.preset_configs.curselection()[0]] + 1)
        else:
            current_preset = self.current_preset_entry.get()
        current_sf2 = self.channel_sound_modules[current_ind]
        if current_preset.isdigit():
            current_preset = int(current_preset)
            current_sf2.change(preset=current_preset - 1)
            if current_preset - 1 in current_sf2.current_preset_ind:
                self.preset_configs.selection_clear(0, END)
                current_preset_ind = current_sf2.current_preset_ind.index(
                    current_preset - 1)
                self.preset_configs.selection_set(current_preset_ind)
                self.preset_configs.see(current_preset_ind)

    def listen_preset(self):
        current_ind = self.choose_channels.index(ANCHOR)
        current_sf2 = self.channel_sound_modules[current_ind]
        current_sf2.play_note('C5')

    def show_current_preset_configs(self):
        current_ind = self.preset_configs.index(ANCHOR)
        self.current_preset_entry.delete(0, END)
        self.current_preset_entry.insert(
            END, str(self.current_preset_ind[current_ind] + 1))
        self.change_current_preset(1)

    def show_current_bank_configs(self):
        current_ind = self.bank_configs.index(ANCHOR)
        current_bank = self.current_all_available_banks[current_ind]
        self.current_bank_entry.delete(0, END)
        self.current_bank_entry.insert(END, str(current_bank))
        self.change_current_bank(mode=1)

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
                          channel_num=0,
                          inner=True,
                          length=None,
                          extra_length=None,
                          track_lengths=None,
                          track_extra_lengths=None,
                          export_args={},
                          soundfont_args=None):
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
        if action == 'get' or (not inner):
            result = obj
            if isinstance(result, chord):
                result = ['chord', result, channel_num]
            elif isinstance(result, piece):
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
        if soundfont_args is None:
            soundfont_args = default_soundfont_args
        types = result[0]
        current_chord = result[1]

        if types == 'chord':
            current_channel_num = result[2]
            current_bpm = self.current_bpm
            current_chord = copy(current_chord)
            current_chord.normalize_tempo(bpm=current_bpm)
            for each in current_chord:
                if isinstance(each, AudioSegment):
                    each.duration = self.real_time_to_bar(
                        len(each), current_bpm)
                    each.volume = 127

            current_sound_modules = self.channel_sound_modules[
                current_channel_num]
            if isinstance(current_sound_modules, rs.sf2_loader):
                if action == 'export':
                    current_msg = self.language_dict["msg"][27].split('|')
                    self.show_msg(
                        f'{current_msg[0]}{self.language_dict["track"]} 1/1 {self.language_dict["channel"]} {current_channel_num + 1} (soundfont) '
                    )
                    self.msg.update()
                silent_audio = current_sound_modules.export_chord(
                    current_chord,
                    bpm=current_bpm,
                    start_time=current_chord.start_time,
                    get_audio=True,
                    effects=current_chord.effects
                    if check_effect(current_chord) else None,
                    length=length,
                    extra_length=extra_length,
                    **soundfont_args)
            else:
                apply_fadeout_obj = self.apply_fadeout(current_chord,
                                                       current_bpm)
                if length:
                    whole_duration = length * 1000
                else:
                    whole_duration = apply_fadeout_obj.eval_time(
                        current_bpm,
                        mode='number',
                        audio_mode=1,
                        start_time=current_chord.start_time) * 1000
                    if extra_length:
                        whole_duration += extra_length * 1000
                silent_audio = AudioSegment.silent(duration=whole_duration)
                silent_audio = self.channel_to_audio(
                    current_chord,
                    current_channel_num,
                    silent_audio,
                    current_bpm,
                    mode=action,
                    length=length,
                    extra_length=extra_length,
                    current_start_time=current_chord.start_time)
            try:
                if action == 'export':
                    silent_audio.export(filename, format=mode, **export_args)
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
            current_chord = copy(current_chord)
            current_chord.normalize_tempo()
            current_chord.apply_start_time_to_changes(
                [-i for i in current_chord.start_times],
                msg=True,
                pan_volume=True)
            current_name = current_chord.name
            current_bpm = current_chord.bpm
            current_start_times = current_chord.start_times
            current_pan = current_chord.pan
            current_volume = current_chord.volume
            current_tracks = current_chord.tracks
            current_channels = current_chord.sampler_channels if current_chord.sampler_channels else [
                i for i in range(len(current_chord))
            ]
            for i in range(len(current_chord.tracks)):
                each_channel = current_chord.tracks[i]
                for each in each_channel:
                    if isinstance(each, AudioSegment):
                        each.duration = self.real_time_to_bar(
                            len(each), current_bpm)
                        each.volume = 127
                current_chord.tracks[i] = each_channel
            apply_fadeout_obj = self.apply_fadeout(current_chord, current_bpm)
            if length:
                whole_duration = length * 1000
            else:
                whole_duration = apply_fadeout_obj.eval_time(
                    current_bpm, mode='number', audio_mode=1) * 1000
                if extra_length:
                    whole_duration += extra_length * 1000
            silent_audio = AudioSegment.silent(duration=whole_duration)
            sound_modules_num = len(self.channel_sound_modules)
            track_number = len(current_chord)
            for i in range(track_number):
                current_channel_number = current_channels[i]
                if current_channel_number >= sound_modules_num:
                    self.show_msg(
                        f'{self.language_dict["track"]} {i+1} : {self.language_dict["msg"][25]}{current_channel_number+1}'
                    )
                    self.msg.update()
                    continue
                current_sound_modules = self.channel_sound_modules[
                    current_channel_number]
                current_track = current_tracks[i]
                if isinstance(current_sound_modules, rs.sf2_loader):
                    if action == 'export':
                        current_msg = self.language_dict["msg"][27].split('|')
                        self.show_msg(
                            f'{current_msg[0]}{self.language_dict["track"]} {i+1}/{track_number} {self.language_dict["channel"]} {current_channels[i] + 1} (soundfont)'
                        )
                        self.msg.update()
                    current_instrument = current_chord.instruments_numbers[i]
                    current_channel = current_chord.channels[
                        i] if current_chord.channels else current_sound_modules.current_channel
                    current_sfid, current_bank, current_preset = current_sound_modules.channel_info(
                        current_channel)
                    if current_sfid == 0:
                        current_sound_modules.change_sfid(
                            current_sound_modules.sfid_list[0],
                            current_channel)
                        current_sfid, current_bank, current_preset = current_sound_modules.channel_info(
                            current_channel)
                    if isinstance(current_instrument, int):
                        current_instrument = [
                            current_instrument - 1, current_bank
                        ]
                    else:
                        current_instrument = [current_instrument[0] - 1
                                              ] + current_instrument[1:]
                    current_sound_modules.change(
                        channel=current_channel,
                        sfid=(current_instrument[2]
                              if len(current_instrument) > 2 else None),
                        bank=current_instrument[1],
                        preset=current_instrument[0],
                        mode=1)
                    silent_audio = silent_audio.overlay(
                        current_sound_modules.export_chord(
                            current_track,
                            bpm=current_bpm,
                            get_audio=True,
                            channel=current_channel,
                            effects=current_track.effects
                            if check_effect(current_track) else None,
                            pan=current_pan[i],
                            volume=current_volume[i],
                            length=None
                            if not track_lengths else track_lengths[i],
                            extra_length=None if not track_extra_lengths else
                            track_extra_lengths[i],
                            **soundfont_args),
                        position=self.bar_to_real_time(current_start_times[i],
                                                       current_bpm, 1))
                    current_sound_modules.change(current_channel,
                                                 current_sfid,
                                                 current_bank,
                                                 current_preset,
                                                 mode=1)
                else:
                    silent_audio = self.channel_to_audio(
                        current_tracks[i],
                        current_channels[i],
                        silent_audio,
                        current_bpm,
                        current_pan[i],
                        current_volume[i],
                        current_start_times[i],
                        mode=action,
                        length=None if not track_lengths else track_lengths[i],
                        extra_length=None
                        if not track_extra_lengths else track_extra_lengths[i],
                        track_ind=i,
                        whole_track_number=track_number)
            if check_effect(current_chord):
                silent_audio = process_effect(silent_audio,
                                              current_chord.effects,
                                              bpm=current_bpm)
            try:
                if action == 'export':
                    silent_audio.export(filename, format=mode, **export_args)
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
        if isinstance(temp, chord):
            for each in temp.notes:
                if not isinstance(each, AudioSegment):
                    if export_fadeout_use_ratio:
                        current_fadeout_time = each.duration * export_audio_fadeout_time_ratio
                    else:
                        current_fadeout_time = self.real_time_to_bar(
                            export_audio_fadeout_time, bpm)
                    each.duration += current_fadeout_time
            return temp
        elif isinstance(temp, piece):
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
                         mode='export',
                         length=None,
                         extra_length=None,
                         track_ind=0,
                         whole_track_number=1):
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
        if length:
            whole_duration = length * 1000
        else:
            whole_duration = apply_fadeout_obj.eval_time(
                current_bpm, mode='number', audio_mode=1) * 1000
            if extra_length:
                whole_duration += extra_length * 1000
        current_silent_audio = AudioSegment.silent(duration=whole_duration)
        current_intervals = current_chord.interval
        current_durations = current_chord.get_duration()
        current_volumes = current_chord.get_volume()
        current_dict = self.channel_dict[current_channel_num]
        current_sounds = self.channel_sound_modules[current_channel_num]
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
                    f'{current_msg[0]}{round((counter / whole_length) * 100, 3):.3f}{current_msg[1]} {self.language_dict["track"]} {track_ind+1}/{whole_track_number} {self.language_dict["channel"]} {current_channel_num + 1}'
                )
                self.msg.update()
                counter += 1
            each = current_chord.notes[i]
            if isinstance(each, (note, AudioSegment)):
                interval = self.bar_to_real_time(current_intervals[i],
                                                 current_bpm, 1)
                duration = self.bar_to_real_time(
                    current_durations[i], current_bpm,
                    1) if not isinstance(each, AudioSegment) else len(each)
                volume = velocity_to_db(current_volumes[i])
                current_fadeout_time = int(
                    duration * export_audio_fadeout_time_ratio
                ) if export_fadeout_use_ratio else int(
                    export_audio_fadeout_time)
                if isinstance(each, AudioSegment):
                    current_sound = each[:duration]
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
                    current_sound = current_sound[:current_max_time]
                if check_effect(each):
                    current_sound = process_effect(current_sound,
                                                   each.effects,
                                                   bpm=current_bpm)

                if current_fadeout_time != 0 and not isinstance(
                        each, AudioSegment):
                    current_sound = current_sound.fade_out(
                        duration=current_max_fadeout_time)
                current_sound += volume
                current_silent_audio = current_silent_audio.overlay(
                    current_sound, position=current_position)
                current_position += interval
        if current_pan:
            pan_ranges = [
                self.bar_to_real_time(i.start_time, current_bpm, 1)
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
                self.bar_to_real_time(i.start_time, current_bpm, 1)
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
        if check_effect(current_chord):
            current_silent_audio = process_effect(current_silent_audio,
                                                  current_chord.effects,
                                                  bpm=current_bpm)
        silent_audio = silent_audio.overlay(current_silent_audio,
                                            position=current_start_time)
        return silent_audio

    def export_midi_file(self, current_chord=None, write_args={}):
        self.show_msg('')
        filename = filedialog.asksaveasfilename(
            initialdir=self.last_place,
            title=self.language_dict['title'][17],
            filetypes=((self.language_dict['title'][1], "*.*"), ),
            defaultextension=f".mid",
            initialfile=self.language_dict['untitled'])
        if not filename:
            return
        if current_chord is None:
            result = self.get_current_musicpy_chords()
            if result is None:
                return
            current_chord = result[1]
        self.show_msg(f'{self.language_dict["msg"][21]}{filename}')
        self.msg.update()
        write(current_chord, self.current_bpm, name=filename, **write_args)
        self.show_msg(f'{self.language_dict["msg"][24]}{filename}')

    def get_current_musicpy_chords(self):
        current_notes = self.set_musicpy_code_text.get('1.0', 'end-1c')
        current_channel_num = 0
        current_bpm = self.current_bpm
        current_globals = globals()
        if 'easy_sampler_current_chord' in current_globals:
            del current_globals['easy_sampler_current_chord']
        lines = current_notes.split('\n')
        find_command = False
        for k in range(len(lines)):
            each = lines[k]
            if each.startswith('play '):
                find_command = True
                lines[k] = 'easy_sampler_current_chord = ' + each[5:]
            elif each.startswith('play(') or each.startswith(
                    'export(') or each.startswith('play_midi('):
                find_command = True
        if not find_command:
            current_notes = f'easy_sampler_current_chord = {current_notes}'
        else:
            current_notes = '\n'.join(lines)
        try:
            exec(current_notes, current_globals, current_globals)
        except Exception as e:
            print(traceback.format_exc())
            output(traceback.format_exc())
            return
        if 'easy_sampler_current_chord' in current_globals:
            current_chord = current_globals['easy_sampler_current_chord']
        else:
            return
        if isinstance(current_chord, tuple):
            length = len(current_chord)
            if length > 1:
                if length == 2:
                    current_chord, current_bpm = current_chord
                elif length == 3:
                    current_chord, current_bpm, current_channel_num = current_chord
                self.change_current_bpm_entry.delete(0, END)
                self.change_current_bpm_entry.insert(END, current_bpm)
                self.change_current_bpm(1)
        elif current_chord is None:
            return
        if isinstance(current_chord, note):
            current_chord = chord([current_chord])
        elif isinstance(current_chord, list) and all(
                isinstance(i, chord) for i in current_chord):
            current_chord = concat(current_chord, mode='|')
        if isinstance(current_chord, chord):
            return 'chord', current_chord, current_channel_num
        if isinstance(current_chord, track):
            has_effect = False
            if check_effect(current_chord):
                has_effect = True
                current_effects = copy(current_chord.effects)
            current_chord = build(current_chord,
                                  bpm=current_chord.bpm if current_chord.bpm
                                  is not None else current_bpm)
            if has_effect:
                current_chord.effects = current_effects
        if isinstance(current_chord, piece):
            current_bpm = current_chord.bpm
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
            if os.path.splitext(sound_path)[1][1:].lower() == 'esi':
                self.load_esi_file(current_ind=current_ind,
                                   file_path=sound_path)
            else:
                self.load_sf2_file(current_ind=current_ind,
                                   sound_path=sound_path)
        else:
            try:
                self.show_msg(
                    f'{self.language_dict["msg"][28]}{self.channel_names[current_ind]} ...'
                )
                self.msg.update()

                notedict = self.channel_dict[current_ind]
                self.channel_sound_modules[current_ind] = load_audiosegments(
                    notedict, sound_path)
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
                print(traceback.format_exc())
                output(traceback.format_exc())
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
                END,
                f'new_midi_file = read("{filename}", mode="all", to_piece=True)\n'
            )
            self.set_musicpy_code_text.focus_set()
            self.show_msg(self.language_dict["msg"][32])

    def change_current_sound_path_func(self):
        current_path = self.current_channel_sound_modules_entry.get()
        if os.path.isdir(current_path):
            self.change_current_sound_path(1)
        elif os.path.isfile(current_path):
            if os.path.splitext(current_path)[1][1:].lower() == 'esi':
                self.load_esi_file(1)
            else:
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
                    self.channel_sound_modules[
                        current_ind] = load_audiosegments(
                            notedict, sound_path)
                    self.channel_sound_modules_name[current_ind] = sound_path
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
                    print(traceback.format_exc())
                    output(traceback.format_exc())
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
        note_sounds = self.channel_sound_modules[channel]
        if name in note_sounds:
            current_sound = note_sounds[name]
            if current_sound:
                current_sound = pygame.mixer.Sound(
                    buffer=current_sound.raw_data)
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
        pygame.mixer.music.stop()
        if self.current_playing:
            for each in self.current_playing:
                self.after_cancel(each)
            self.current_playing.clear()
        if self.piece_playing:
            for each in self.piece_playing:
                self.after_cancel(each)
            self.piece_playing.clear()

    def play_current_musicpy_code(self):
        if not self.default_load:
            return
        self.show_msg('')
        self.msg.update()
        if not self.channel_sound_modules:
            self.show_msg(self.language_dict["msg"][18])
            return

        self.stop_playing()
        global global_play
        global_play = False
        current_notes = self.set_musicpy_code_text.get('1.0', 'end-1c')
        current_channel_num = 0
        current_bpm = self.current_bpm
        current_globals = globals()
        if 'easy_sampler_current_chord' in current_globals:
            del current_globals['easy_sampler_current_chord']
        lines = current_notes.split('\n')
        find_command = False
        for k in range(len(lines)):
            each = lines[k].lstrip(' ')
            if each.startswith('play '):
                find_command = True
                lines[k] = 'easy_sampler_current_chord = ' + each[5:]
            elif each.startswith('play(') or each.startswith(
                    'export(') or each.startswith(
                        'play_midi(') or each.startswith('output('):
                find_command = True
        if not find_command:
            current_notes = f'easy_sampler_current_chord = {current_notes}'
        else:
            current_notes = '\n'.join(lines)
        try:
            exec(current_notes, current_globals, current_globals)
        except Exception as e:
            print(traceback.format_exc())
            if not global_play:
                self.show_msg(self.language_dict["msg"][4])
                output(traceback.format_exc())
            return
        if 'easy_sampler_current_chord' in current_globals:
            current_chord = current_globals['easy_sampler_current_chord']
        else:
            return
        if isinstance(current_chord, tuple):
            length = len(current_chord)
            if length > 1:
                if length == 2:
                    current_chord, current_bpm = current_chord
                elif length == 3:
                    current_chord, current_bpm, current_channel_num = current_chord
                self.change_current_bpm_entry.delete(0, END)
                self.change_current_bpm_entry.insert(END, current_bpm)
                self.change_current_bpm(1)
        if current_chord is not None:
            self.play_musicpy_sounds(current_chord, current_bpm,
                                     current_channel_num)

    def play_musicpy_sounds(self,
                            current_chord,
                            current_bpm=None,
                            current_channel_num=None,
                            inner=True,
                            length=None,
                            extra_length=None,
                            track_lengths=None,
                            track_extra_lengths=None,
                            soundfont_args=None):
        if isinstance(current_chord, note):
            current_chord = chord([current_chord])
        elif isinstance(current_chord, list) and all(
                isinstance(i, chord) for i in current_chord):
            current_chord = concat(current_chord, mode='|')
        if isinstance(current_chord, chord):
            if check_special(current_chord) or isinstance(
                    self.channel_sound_modules[current_channel_num],
                    rs.sf2_loader):
                self.export_audio_file(action='play',
                                       channel_num=current_channel_num,
                                       obj=None if inner else current_chord,
                                       inner=inner,
                                       length=length,
                                       extra_length=extra_length,
                                       track_lengths=track_lengths,
                                       track_extra_lengths=track_extra_lengths,
                                       soundfont_args=soundfont_args)
            else:
                if current_chord.start_time == 0:
                    self.play_channel(current_chord, current_channel_num)
                else:
                    self.play_channel(current_chord,
                                      current_channel_num,
                                      start_time=bar_to_real_time(
                                          current_chord.start_time,
                                          current_bpm, 1))
        elif isinstance(current_chord, track):
            has_effect = False
            if check_effect(current_chord):
                has_effect = True
                current_effects = copy(current_chord.effects)
            current_chord = build(current_chord,
                                  bpm=current_chord.bpm
                                  if current_chord.bpm is not None else bpm)
            if has_effect:
                current_chord.effects = current_effects
        if isinstance(current_chord, piece):
            current_channel_nums = current_chord.sampler_channels if current_chord.sampler_channels else [
                i for i in range(len(current_chord))
            ]
            if check_special(current_chord) or any(
                    isinstance(self.channel_sound_modules[i], rs.sf2_loader)
                    for i in current_channel_nums):
                self.export_audio_file(action='play',
                                       obj=None if inner else current_chord,
                                       inner=inner,
                                       length=length,
                                       extra_length=extra_length,
                                       track_lengths=track_lengths,
                                       track_extra_lengths=track_extra_lengths,
                                       soundfont_args=soundfont_args)
                self.show_msg(self.language_dict["msg"][22])
                return
            current_tracks = current_chord.tracks
            current_bpm = current_chord.bpm
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

    def play_channel(self, current_chord, current_channel_num=0, start_time=0):
        if len(self.channel_sound_modules) <= current_channel_num:
            self.show_msg(
                f'{self.language_dict["msg"][25]}{current_channel_num+1}')
            return
        if not self.channel_sound_modules[current_channel_num]:
            self.show_msg(
                f'{self.language_dict["channel"]}{current_channel_num+1} {self.language_dict["msg"][26]}'
            )
            return
        current_intervals = current_chord.interval
        current_durations = current_chord.get_duration()
        current_volumes = current_chord.get_volume()
        current_time = start_time
        for i in range(len(current_chord)):
            each = current_chord.notes[i]
            if isinstance(each, note):
                duration = current_durations[i]
                volume = current_volumes[i]
                current_id = self.after(
                    int(current_time),
                    lambda each=each, duration=duration, volume=volume: self.
                    play_note_func(f'{standardize_note(each.name)}{each.num}',
                                   duration, volume, current_channel_num))
                self.current_playing.append(current_id)
                current_time += self.bar_to_real_time(current_intervals[i],
                                                      self.current_bpm, 1)

    def open_change_settings(self):
        if not self.open_settings:
            self.open_settings = True
        else:
            root2.focus_force()
            return
        os.chdir('scripts')
        with open('change_settings.pyw', encoding='utf-8-sig') as f:
            exec(f.read(), globals(), globals())

    def modules(self, ind):
        return self.channel_sound_modules[ind]

    def module_names(self, ind):
        return self.channel_sound_modules_name[ind]

    def open_debug_window(self):
        if self.is_open_debug_window:
            self.debug_window.focus_set()
            return
        else:
            self.is_open_debug_window = True
            self.debug_window = Toplevel(self)
            self.debug_window.iconphoto(False, self.icon_image)
            self.debug_window.configure(bg=background_color)
            x = self.winfo_x()
            y = self.winfo_y()
            w = self.debug_window.winfo_width()
            h = self.debug_window.winfo_height()
            self.debug_window.geometry("%dx%d+%d+%d" %
                                       (w, h, x + 200, y + 200))
            self.debug_window.protocol("WM_DELETE_WINDOW",
                                       self.close_debug_window)
            self.debug_window.title(self.language_dict['debug window'])
            self.debug_window.minsize(700, 400)
            self.debug_window.focus_set()
            self.debug_window.output_text = Text(self.debug_window,
                                                 width=87,
                                                 height=20,
                                                 wrap='none',
                                                 undo=True,
                                                 autoseparators=True,
                                                 maxundo=-1,
                                                 font=(font_type, font_size))
            self.debug_window.output_text.place(x=20, y=20)
            self.debug_window.clear_text_button = ttk.Button(
                self.debug_window,
                text=self.language_dict['debug clear'],
                command=lambda: self.debug_window.output_text.delete(
                    '1.0', END))
            self.debug_window.clear_text_button.place(x=600, y=350)
            debug_inputs_v = ttk.Scrollbar(
                self.debug_window,
                orient="vertical",
                command=self.debug_window.output_text.yview)
            debug_inputs_h = ttk.Scrollbar(
                self.debug_window,
                orient="horizontal",
                command=self.debug_window.output_text.xview)
            self.debug_window.output_text.configure(
                yscrollcommand=debug_inputs_v.set,
                xscrollcommand=debug_inputs_h.set)
            debug_inputs_v.place(x=632, y=20, height=285)
            debug_inputs_h.place(x=20, y=305, width=612)


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
        pygame.mixer.quit()
        pygame.mixer.init(frequency, sound_size, channel, buffer)
        pygame.mixer.set_num_channels(maxinum_channels)
        self.after(500, open_main_window)


def open_main_window():
    current_start_window.destroy()
    global root
    root = Root()
    root.lift()
    root.attributes("-topmost", True)
    root.focus_force()
    root.attributes('-topmost', 0)
    argv = sys.argv
    if len(argv) > 1:
        current_file = argv[1]
        root.after(100, lambda: root.open_project_file(current_file))
    root.mainloop()


def play_audio(audio, mode=0):
    if isinstance(audio, (pitch, sound)):
        current_audio = audio.sounds
    else:
        current_audio = audio
    if mode == 0:
        if current_audio.channels == 1:
            current_audio = current_audio.set_frame_rate(44100).set_channels(2)
        current_sound_object = pygame.mixer.Sound(
            buffer=current_audio.raw_data)
        current_sound_object.play()
    elif mode == 1:
        try:
            current_file = BytesIO()
            current_audio.export(current_file, format='wav')
            current_sound_object = pygame.mixer.Sound(file=current_file)
        except:
            current_path = os.getcwd()
            os.chdir(abs_path)
            current_audio.export('scripts/temp.wav', format='wav')
            current_sound_object = pygame.mixer.Sound(file='scripts/temp.wav')
            os.remove('scripts/temp.wav')
            os.chdir(current_path)
        current_sound_object.play()


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
                    current_sound_obj_path,
                    format=current_sound_format).set_frame_rate(
                        44100).set_channels(2)
            except:
                with open(current_sound_obj_path, 'rb') as f:
                    current_data = f.read()
                current_sounds[i] = AudioSegment.from_file(
                    BytesIO(current_data),
                    format=current_sound_format).set_frame_rate(
                        44100).set_channels(2)
        else:
            current_sounds[i] = None
    return current_sounds


def load_sounds(dic):
    wavedict = {i: (dic[i].get_raw() if dic[i] else None) for i in dic}
    return wavedict


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


def bar_to_real_time(bar, bpm, mode=0):
    # return time in ms
    return int(
        (60000 / bpm) * (bar * 4)) if mode == 0 else (60000 / bpm) * (bar * 4)


def real_time_to_bar(time, bpm):
    return (time / (60000 / bpm)) / 4


def check_pan_or_volume(sound):
    return isinstance(sound, piece) and (any(i for i in sound.pan)
                                         or any(i for i in sound.volume))


def has_audio(sound):
    if isinstance(sound, chord):
        return any(isinstance(i, AudioSegment) for i in sound.notes)
    elif isinstance(sound, piece):
        return any(has_audio(i) for i in sound.tracks)


def check_special(sound):
    return check_effect_all(sound) or check_pan_or_volume(sound) or has_audio(
        sound)


def check_effect(sound):
    return hasattr(sound, 'effects') and isinstance(sound.effects,
                                                    list) and sound.effects


def check_effect_all(sound):
    if isinstance(sound, chord):
        return check_effect(sound) or any(check_effect(i) for i in sound)
    elif isinstance(sound, piece):
        return check_effect(sound) or any(
            check_effect_all(i) for i in sound.tracks)
    else:
        return check_effect(sound)


def process_effect(sound, effects, **kwargs):
    current_args = kwargs
    for each in effects:
        each.process_unknown_args(**current_args)
        sound = each.process(sound)
    return sound


def set_effect(sound, *effects):
    if len(effects) == 1:
        current_effect = effects[0]
        if not isinstance(current_effect, effect):
            if isinstance(current_effect, effect_chain):
                effects = current_effect.effects
            else:
                effects = list(current_effect)
        else:
            effects = list(effects)
    else:
        effects = list(effects)
    sound.effects = effects
    return sound


def adsr_func(sound, attack, decay, sustain, release):
    change_db = percentage_to_db(sustain)
    result_db = sound.dBFS + change_db
    if attack > 0:
        sound = sound.fade_in(attack)
    if decay > 0:
        sound = sound.fade(to_gain=result_db, start=attack, duration=decay)
    else:
        sound = sound[:attack].append(sound[attack:] + change_db)
    if release > 0:
        sound = sound.fade_out(release)
    return sound


def sine(freq=440, duration=1000, volume=0):
    if isinstance(freq, (str, note)):
        freq = get_freq(freq)
    return Sine(freq).to_audio_segment(duration, volume)


def triangle(freq=440, duration=1000, volume=0):
    if isinstance(freq, (str, note)):
        freq = get_freq(freq)
    return Triangle(freq).to_audio_segment(duration, volume)


def sawtooth(freq=440, duration=1000, volume=0):
    if isinstance(freq, (str, note)):
        freq = get_freq(freq)
    return Sawtooth(freq).to_audio_segment(duration, volume)


def square(freq=440, duration=1000, volume=0):
    if isinstance(freq, (str, note)):
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
                  ] if not isinstance(volume, list) else volume
        volume = [percentage_to_db(i) for i in volume]
    for i in range(len(temp)):
        current_note = temp[i]
        if isinstance(current_note, note):
            if mode == 'sine':
                temp[i] = sine(
                    get_freq(current_note),
                    root.bar_to_real_time(current_note.duration, bpm, 1),
                    volume[i])
            elif mode == 'triangle':
                temp[i] = triangle(
                    get_freq(current_note),
                    root.bar_to_real_time(current_note.duration, bpm, 1),
                    volume[i])
            elif mode == 'sawtooth':
                temp[i] = sawtooth(
                    get_freq(current_note),
                    root.bar_to_real_time(current_note.duration, bpm, 1),
                    volume[i])
            elif mode == 'square':
                temp[i] = square(
                    get_freq(current_note),
                    root.bar_to_real_time(current_note.duration, bpm, 1),
                    volume[i])
            else:
                temp[i] = mode(
                    get_freq(current_note),
                    root.bar_to_real_time(current_note.duration, bpm, 1),
                    volume[i])
    return temp


def audio(obj, channel_num=0):
    if isinstance(obj, note):
        obj = chord([obj])
    elif isinstance(obj, track):
        obj = build(obj, bpm=obj.bpm, name=obj.name)
    result = root.export_audio_file(obj, action='get', channel_num=channel_num)
    return result


def audio_chord(audio_list, interval=0, duration=1 / 4, volume=127):
    result = chord([])
    result.notes = audio_list
    result.interval = interval if isinstance(
        interval, list) else [interval for i in range(len(audio_list))]
    durations = duration if isinstance(
        duration, list) else [duration for i in range(len(audio_list))]
    volumes = volume if isinstance(
        volume, list) else [volume for i in range(len(audio_list))]
    for i in range(len(result.notes)):
        result.notes[i].duration = durations[i]
        result.notes[i].volume = volumes[i]
    return result


play_midi = play


def play(current_chord,
         bpm=None,
         channel=0,
         length=None,
         extra_length=None,
         track_lengths=None,
         track_extra_lengths=None,
         soundfont_args=None):
    global global_play
    global_play = True
    if bpm is not None:
        root.change_current_bpm_entry.delete(0, END)
        root.change_current_bpm_entry.insert(END, bpm)
        root.change_current_bpm(1)
    root.play_musicpy_sounds(current_chord,
                             bpm,
                             channel,
                             inner=False,
                             length=length,
                             extra_length=extra_length,
                             track_lengths=track_lengths,
                             track_extra_lengths=track_extra_lengths,
                             soundfont_args=soundfont_args)


def export(current_chord,
           mode='wav',
           action='export',
           channel=0,
           bpm=None,
           length=None,
           extra_length=None,
           track_lengths=None,
           track_extra_lengths=None,
           export_args={},
           soundfont_args=None,
           write_args={}):
    global global_play
    global_play = True
    if bpm is not None:
        root.change_current_bpm_entry.delete(0, END)
        root.change_current_bpm_entry.insert(END, bpm)
        root.change_current_bpm(1)
    if mode == 'mid' or mode == 'midi':
        root.export_midi_file(current_chord, **write_args)
    else:
        root.export_audio_file(obj=current_chord,
                               mode=mode,
                               action=action,
                               channel_num=channel,
                               inner=False,
                               length=length,
                               extra_length=extra_length,
                               track_lengths=track_lengths,
                               track_extra_lengths=track_extra_lengths,
                               export_args=export_args,
                               soundfont_args=soundfont_args)


def output(*obj):
    result = ' '.join([str(i) for i in obj]) + '\n'
    if root.is_open_debug_window:
        root.debug_window.output_text.insert(END, result)
        root.debug_window.focus_set()


global_play = False
reverse = effect(lambda s: s.reverse(), 'reverse')
offset = effect(lambda s, bar, bpm: s[bar_to_real_time(bar, bpm, 1):],
                'offset',
                unknown_args={'bpm': None})
fade_in = effect(lambda s, duration: s.fade_in(duration), 'fade in')
fade_out = effect(lambda s, duration: s.fade_out(duration), 'fade out')
fade = effect(
    lambda s, duration1, duration2=0: s.fade_in(duration1).fade_out(duration2),
    'fade')
adsr = effect(adsr_func, 'adsr')

current_start_window = start_window()
current_start_window.mainloop()
