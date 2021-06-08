with open('scripts/settings.py', encoding='utf-8-sig') as f:
    exec(f.read())


def load(dic, path, file_format, volume):
    wavedict = {
        i: pygame.mixer.Sound(f'{path}/{dic[i]}.{file_format}')
        for i in dic
    }
    if volume != None:
        [wavedict[x].set_volume(volume) for x in wavedict]
    return wavedict


def load_sounds(dic, path, file_format):
    wavedict = {i: f'{path}/{dic[i]}.{file_format}' for i in dic}
    return wavedict


def play_note(name):
    if name in note_sounds:
        note_sounds[name].play(maxtime=note_play_last_time)


def standardize_note(i):
    if i in standard_dict:
        i = standard_dict[i]
    return i


def start_load():
    pygame.mixer.init(frequency, sound_size, channel, buffer)
    pygame.mixer.set_num_channels(maxinum_channels)
    global note_sounds
    global note_sounds_path
    note_sounds = load(notedict, sound_path, sound_format, global_volume)
    note_sounds_path = load_sounds(notedict, sound_path, sound_format)
    current_start_window.loading_label.configure(text='loading complete')
    current_start_window.after(500, open_main_window)


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Easy Sampler")
        self.minsize(1000, 650)

        style = ttk.Style()
        style.configure('TButton', font=(font_type, font_size))
        style.configure('TEntry', font=(font_type, font_size))

        self.set_chord_button = ttk.Button(self,
                                           text='Enter Notes',
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
            text='Enter Musicpy Code',
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

        self.set_bpm_button = ttk.Button(self,
                                         text='Change BPM',
                                         command=self.set_bpm_func)
        self.set_bpm_button.place(x=0, y=300)
        self.set_bpm_entry = ttk.Entry(self, width=10)
        self.set_bpm_entry.insert(END, '120')
        self.set_bpm_entry.place(x=100, y=300)
        self.current_bpm = 120
        self.current_playing = []

        self.msg = ttk.Label(self, text='')
        self.msg.place(x=0, y=600)

        self.set_sound_path_button = ttk.Button(
            self, text='Change Sound Path', command=self.set_sound_path_func)
        self.set_sound_path_button.place(x=0, y=250)
        self.set_sound_path_entry = ttk.Entry(self, width=100)
        self.set_sound_path_entry.insert(END, sound_path)
        self.set_sound_path_entry.place(x=130, y=250)

        self.set_sound_format_button = ttk.Button(
            self,
            text='Change Sound Format',
            command=self.set_sound_format_func)
        self.set_sound_format_button.place(x=400, y=300)
        self.set_sound_format_entry = ttk.Entry(self, width=20)
        self.set_sound_format_entry.insert(END, sound_format)
        self.set_sound_format_entry.place(x=560, y=300)

        self.load_midi_file_button = ttk.Button(
            self, text='Load Midi Files', command=self.load_midi_file_func)
        self.load_midi_file_button.place(x=500, y=350)
        self.load_midi_file_entry = ttk.Entry(self, width=50)
        self.load_midi_file_entry.insert(END, '')
        self.load_midi_file_entry.place(x=620, y=350)

        self.change_settings_button = ttk.Button(
            self, text='Change Settings', command=self.open_change_settings)
        self.change_settings_button.place(x=620, y=200)
        self.open_settings = False
        
        self.choose_tracks_bar = Scrollbar(self)
        self.choose_tracks_bar.place(x=225, y=165, height=125, anchor=CENTER)
        self.choose_tracks = Listbox(
            self, yscrollcommand=self.choose_tracks_bar.set, height=7)        
        self.choose_tracks.bind('<<ListboxSelect>>',
                                        lambda e: self.show_current_track())        
        self.choose_tracks.place(x=0, y=100, width=220)
        self.choose_tracks_bar.config(
            command=self.choose_tracks.yview)        
        
        self.choose_tracks.insert(END, 'Track 1')
        self.choose_tracks.insert(END, 'Track 2')
        self.tracks = []
        self.track_names = ['Track 1', 'Track 2']
        self.track_sound_modules_name = [sound_path, '']
        self.track_sound_modules = [note_sounds, '']
        self.track_num = 1
        self.current_track_name_label = ttk.Label(self, text='Track Name')
        self.current_track_name_entry = ttk.Entry(self, width=20)
        self.current_track_name_label.place(x=250, y=100)
        self.current_track_name_entry.place(x=350, y=100)
        
        self.current_track_sound_modules_label = ttk.Label(self, text='Track Sound Modules')
        self.current_track_sound_modules_entry = ttk.Entry(self, width=82)
        self.current_track_sound_modules_label.place(x=250, y=150)
        self.current_track_sound_modules_entry.place(x=400, y=150)        
        
        self.change_current_track_name_button = ttk.Button(self, text='Change Track Name', command=self.change_current_track_name)
        self.change_current_track_name_button.place(x=550, y=100)

    def change_current_track_name(self):
        current_ind = self.choose_tracks.index(ANCHOR)
        current_track_name = self.current_track_name_entry.get()
        self.choose_tracks.delete(current_ind)
        self.choose_tracks.insert(current_ind, current_track_name)
        self.choose_tracks.selection_anchor(current_ind)
        self.choose_tracks.selection_set(current_ind)
        self.track_names[current_ind] = current_track_name
    
    def show_current_track(self):
        current_ind = self.choose_tracks.index(ANCHOR)
        self.current_track_name_entry.delete(0, END)
        self.current_track_name_entry.insert(END, self.track_names[current_ind])
        self.current_track_sound_modules_entry.delete(0, END)
        self.current_track_sound_modules_entry.insert(END, self.track_sound_modules_name[current_ind])
    
    def load_midi_file_func(self):
        self.msg.configure(text='')
        filename = filedialog.askopenfilename(initialdir='.',
                                              title="Choose Midi Files",
                                              filetype=(("midi files",
                                                         "*.mid"),
                                                        ("all files", "*.*")))
        if filename:
            self.load_midi_file_entry.delete(0, END)
            self.load_midi_file_entry.insert(END, filename)
            self.set_musicpy_code_entry.delete('1.0', END)
            current_midi_file = read(filename)
            self.set_bpm_entry.delete(0, END)
            self.set_bpm_entry.insert(END, current_midi_file[0])
            self.set_bpm_func()
            self.set_musicpy_code_entry.insert(
                END, f'read("{filename}", mode="all", merge=True)[1]')
            self.msg.configure(
                text=
                f'The midi file is loaded, please click Enter Musicpy Code button to play'
            )

    def set_sound_format_func(self):
        self.msg.configure(text='')
        current_sound_format = self.set_sound_format_entry.get()
        global sound_format
        sound_format = current_sound_format
        self.msg.configure(text=f'Set sound format to {current_sound_format}')

    def set_sound_path_func(self):
        self.msg.configure(text='')
        directory = filedialog.askdirectory(
            initialdir='.',
            title="Choose Sound Path",
        )
        if directory:
            self.set_sound_path_entry.delete(0, END)
            self.set_sound_path_entry.insert(END, directory)

            try:
                global sound_path
                global note_sounds
                global note_sounds_path
                sound_path = directory
                note_sounds = load(notedict, sound_path, sound_format,
                                   global_volume)
                note_sounds_path = load_sounds(notedict, sound_path,
                                               sound_format)
                self.msg.configure(text=f'The sound path has changed')
                self.stop_playing()
            except:
                self.msg.configure(
                    text=
                    f'Error: The sound files in the sound path do not match with settings'
                )

    def bar_to_real_time(self, bar, bpm):
        # return time in ms
        return int((60000 / bpm) * (bar * 4))

    def set_bpm_func(self):
        self.msg.configure(text='')
        current_bpm = self.set_bpm_entry.get()
        try:
            current_bpm = float(current_bpm)
            self.current_bpm = current_bpm
            self.msg.configure(text=f'Set BPM to {current_bpm}')
        except:
            self.msg.configure(text=f'Error: invalid BPM')
            pass

    def play_note_func(self, name, duration, volume):
        if name in note_sounds_path:
            current_sound = pygame.mixer.Sound(
                note_sounds[name]
            )  #current_sound = pygame.mixer.Sound(note_sounds_path[name])
            current_sound.set_volume(global_volume * volume / 127)
            duration_time = self.bar_to_real_time(duration, self.current_bpm)
            current_sound.play()
            current_id = self.after(
                duration_time, lambda: current_sound.fadeout(fadeout_time))
            self.current_playing.append(current_id)

    def stop_playing(self):
        pygame.mixer.stop()
        for each in self.current_playing:
            self.after_cancel(each)
        self.current_playing.clear()

    def play_current_musicpy_code(self):
        self.msg.configure(text='')
        self.stop_playing()
        current_notes = self.set_musicpy_code_entry.get('1.0', 'end-1c')
        try:
            current_chord = eval(current_notes)
        except:
            try:
                lines = current_notes.split('\n')
                for k in range(len(lines)):
                    each = lines[k]
                    if each.startswith('play'):
                        lines[k] = 'current_chord = ' + each[4:]
                current_notes = '\n'.join(lines)
                exec(current_notes, globals(), globals())
                current_chord = globals()['current_chord']
                if type(current_chord) == tuple and len(current_chord) > 1:
                    current_chord, current_bpm = current_chord
                    self.set_bpm_entry.delete(0, END)
                    self.set_bpm_entry.insert(END, current_bpm)
                    self.set_bpm_func()
            except Exception as e:
                print(str(e))
                self.msg.configure(
                    text=
                    f'Error: invalid musicpy code or not result in a chord instance'
                )
                return
        self.msg.configure(text=f'Start playing')
        if type(current_chord) == note:
            current_chord = chord([current_chord])
        elif type(current_chord) == list and all(
                type(i) == chord for i in current_chord):
            current_chord = concat(current_chord, mode='|')
        if type(current_chord) == chord:
            current_chord = current_chord.only_notes()
            current_intervals = current_chord.interval
            current_durations = current_chord.get_duration()
            current_volumes = current_chord.get_volume()
            current_time = 0
            for i in range(len(current_chord)):
                each = current_chord.notes[i]
                if i == 0:
                    self.play_note_func(
                        f'{standardize_note(each.name)}{each.num}',
                        current_durations[i], current_volumes[i])
                else:
                    duration = current_durations[i]
                    volume = current_volumes[i]
                    current_time += self.bar_to_real_time(
                        current_intervals[i - 1], self.current_bpm)
                    current_id = self.after(
                        current_time,
                        lambda each=each, duration=duration, volume=volume:
                        self.play_note_func(
                            f'{standardize_note(each.name)}{each.num}',
                            duration, volume))
                    self.current_playing.append(current_id)
        elif type(current_chord) == piece:
            pass

    def play_current_chord(self):
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
    root.attributes('-topmost', 0)
    root.mainloop()


class start_window(Tk):
    def __init__(self):
        super(start_window, self).__init__()
        self.configure(bg='ivory2')
        self.overrideredirect(True)
        self.minsize(500, 250)
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
        self.title_label.place(x=110, y=50)
        self.loading_label = ttk.Label(self,
                                       text='loading sounds, please wait...',
                                       style='loading.TLabel')
        self.loading_label.place(x=110, y=150)
        self.after(500, start_load)


current_start_window = start_window()
current_start_window.mainloop()
