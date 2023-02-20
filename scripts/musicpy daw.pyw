import traceback
import json
import multiprocessing
import threading
from pydoc import importfile
import fractions
from scripts.change_settings import change_parameter, config_window, json_module

sys.path.append('scripts/effects')
settings_path = 'scripts/settings.json'
current_settings = json_module(settings_path)
icon_path = 'resources/images/musicpy daw.png'

import musicpy

musicpy_vars = dir(musicpy)
function_names = list(set(musicpy_vars))
function_names.sort()


class Daw(QtWidgets.QMainWindow):

    def __init__(self, file=None, dpi=None):
        super().__init__()
        self.dpi = dpi
        self.current_font = QtGui.QFont(current_settings.font_type,
                                        current_settings.font_size)
        self.current_font = set_font(self.current_font, self.dpi)
        current_settings.font_size = self.current_font.pointSize()
        self.current_text_area_font = QtGui.QFont(
            current_settings.text_area_font_type,
            current_settings.text_area_font_size)
        self.current_text_area_font = set_font(self.current_text_area_font,
                                               self.dpi)
        current_settings.text_area_font_size = self.current_text_area_font.pointSize(
        )
        self.change_language(current_settings.default_language)
        self.init_screen()
        self.init_parameters()
        for each, value in self.main_window_language_dict.items():
            current_widget = vars(self)[each]
            current_widget.setText(value)
            current_widget.adjustSize()
        if file is not None:
            self.after(10, lambda: self.initialize(mode=1, file=file))
        else:
            self.after(10, self.initialize)

    def get_stylesheet(self):
        result = f'''
        QMainWindow {{
        background-color: {current_settings.background_color};
        }}
        QPushButton {{
        background-color: {current_settings.button_background_color};
        color: {current_settings.foreground_color};
        font-size: {current_settings.font_size}pt;
        font-family: {current_settings.font_type};
        border: 6px transparent;
        border-style: outset;
        }}
        QPushButton:hover {{
        background-color: {current_settings.active_background_color};
        color: {current_settings.active_foreground_color};
        }}
        QCheckBox {{
        background-color: {current_settings.background_color};
        color: {current_settings.foreground_color};
        }}
        QLabel {{
        background-color: {current_settings.background_color};
        color: {current_settings.label_foreground_color};
        font-size: {current_settings.font_size}pt;
        font-family: {current_settings.font_type};
        }}
        QMenu {{
        background-color: {current_settings.text_area_background_color};
        color: {current_settings.text_area_foreground_color};
        font-size: {current_settings.font_size}pt;
        font-family: {current_settings.font_type};
        }}
        QMenu::item:selected {{
        background-color: {current_settings.active_background_color};
        color: {current_settings.active_foreground_color};
        }}
        QPlainTextEdit {{
        background-color: {current_settings.text_area_background_color};
        color: {current_settings.text_area_foreground_color};
        selection-color: {current_settings.text_area_selection_foreground_color};
        selection-background-color: {current_settings.text_area_selection_background_color};
        }}
    '''
        return result

    def get_action(self,
                   text='',
                   command=None,
                   icon=None,
                   shortcut=None,
                   checkable=False,
                   initial_value=False,
                   **kwargs):
        current_action = QtWidgets.QAction(
            QtGui.QIcon() if icon is None else QtGui.QIcon(icon), text, self,
            **kwargs)
        current_action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
        if command is not None:
            current_action.triggered.connect(command)
        if shortcut is not None:
            current_action.setShortcut(shortcut)
        if checkable:
            current_action.setCheckable(True)
            current_action.setChecked(initial_value)
        return current_action

    def get_menu(self, actions, text=''):
        current_menu = QtWidgets.QMenu(text, self)
        for i in actions:
            if isinstance(i, QtWidgets.QAction):
                current_menu.addAction(i)
            elif isinstance(i, QtWidgets.QMenu):
                current_menu.addMenu(i)
        return current_menu

    def after(self, time, function):
        QtCore.QTimer.singleShot(time, function)

    def init_screen(self):
        self.setWindowTitle("Musicpy Daw")
        self.setMinimumSize(1100, 670)
        self.setWindowIcon(QtGui.QIcon(icon_path))
        try:
            self.init_skin(current_settings.current_skin)
        except:
            current_settings.current_skin = 'default'
            self.init_skin(current_settings.current_skin)

        current_stylesheet = self.get_stylesheet()
        self.setStyleSheet(current_stylesheet)
        self.current_project_name = Label(self, text='untitled.mdp')
        self.current_project_name.place(x=0, y=35)
        self.set_musicpy_code_button = Button(
            self,
            text='Play Musicpy Code',
            command=self.play_current_musicpy_code)
        self.set_musicpy_code_button.place(x=0, y=310)

        self.file_top = Button(
            self,
            text='File',
            command=lambda: self.file_top_make_menu(mode='file'))
        self.file_top.place(x=0, y=0)

        self.file_top_options = Button(
            self,
            text='Options',
            command=lambda: self.file_top_make_menu(mode='options'))
        self.file_top_options.place(x=70, y=0)

        self.file_top_tools = Button(
            self,
            text='Tools',
            command=lambda: self.file_top_make_menu(mode='tools'))
        self.file_top_tools.place(x=160, y=0)

        self.init_menu()

        self.set_musicpy_code_text = CustomTextEdit(
            self,
            pairing_symbols=current_settings.pairing_symbols,
            custom_actions=self.set_musicpy_code_text_actions,
            size=(810, 335),
            font=QtGui.QFont(current_settings.text_area_font_type,
                             current_settings.text_area_font_size),
            place=(150, 250))
        self.current_line_number = 1
        self.current_column_number = 1

        self.line_column = Label(
            self,
            text=
            f'Line {self.current_line_number} Col {self.current_column_number}'
        )
        self.line_column.place(x=780, y=610)
        self.get_current_line_column()
        self.custom_actions = [
            self.get_action(command=self.play_current_musicpy_code,
                            shortcut='Ctrl+R'),
            self.get_action(command=self.stop_playing, shortcut='Ctrl+E'),
            self.get_action(command=self.open_project_file, shortcut='Ctrl+W'),
            self.get_action(command=self.save_as_project_file,
                            shortcut='Ctrl+S'),
            self.get_action(
                command=lambda e: self.save_as_project_file(new=True),
                shortcut='Ctrl+B'),
            self.get_action(command=self.import_musicpy_code,
                            shortcut='Ctrl+F'),
            self.get_action(command=self.save_current_musicpy_code,
                            shortcut='Ctrl+D'),
            self.get_action(command=self.open_export_menu, shortcut='Ctrl+G'),
            self.get_action(command=self.import_midi_file_func,
                            shortcut='Ctrl+H'),
            self.get_action(command=self.close, shortcut='Ctrl+Q')
        ]
        self.addActions(self.custom_actions)
        self.stop_button = Button(self, text='Stop', command=self.stop_playing)
        self.stop_button.place(x=0, y=360)

        self.change_current_bpm_button = Button(
            self, text='Change BPM', command=self.change_current_bpm)
        self.change_current_bpm_button.place(x=0, y=210)
        self.change_current_bpm_entry = LineEdit(self,
                                                 width=70,
                                                 x=100,
                                                 y=210,
                                                 font=self.current_font)
        self.change_current_bpm_entry.setText('120')
        self.msg = Label(self, text='')
        self.msg.place(x=130, y=630)

        self.import_instrument_button = Button(self,
                                               text='Import Instrument',
                                               command=self.import_instrument)
        self.import_instrument_button.place(x=550, y=210)

        self.change_settings_button = Button(self,
                                             text='Change Settings',
                                             command=self.open_change_settings)
        self.change_settings_button.place(x=0, y=460)

        self.open_debug_window_button = Button(self,
                                               text='Open Debug Window',
                                               command=self.open_debug_window)
        self.open_debug_window_button.place(x=0, y=510)

        self.choose_channels = Channel(self)
        self.choose_channels.setFixedHeight(70)
        self.choose_channels.setFont(self.current_font)
        self.choose_channels.addActions([
            self.get_action(shortcut='Z', command=self.add_new_channel),
            self.get_action(shortcut='X', command=self.delete_channel),
            self.get_action(shortcut='C', command=self.clear_current_channel),
            self.get_action(shortcut='V', command=self.clear_all_channels)
        ])
        self.choose_channels.setFixedSize(220, 125)
        self.choose_channels.move(0, 62)
        self.choose_channels.insertItem(0, self.language_dict['init'][0])

        self.current_channel_name_label = Label(self,
                                                text='Channel Name',
                                                x=250,
                                                y=60)
        self.current_channel_name_entry = LineEdit(self,
                                                   width=300,
                                                   x=350,
                                                   y=55,
                                                   font=self.current_font)
        self.current_channel_name_entry.addAction(
            self.get_action(shortcut='Return',
                            command=self.change_current_channel_name))
        self.current_channel_instruments_label = Label(
            self, text='Channel Instrument')
        self.current_channel_instruments_entry = LineEdit(
            self, width=500, x=410, y=105, font=self.current_font)
        self.current_channel_instruments_entry.addAction(
            self.get_action(shortcut='Return',
                            command=self.import_instrument_func))
        self.current_channel_instruments_label.place(x=250, y=110)

        self.change_current_channel_name_button = Button(
            self,
            text='Change Channel Name',
            command=self.change_current_channel_name)
        self.change_current_channel_name_button.place(x=550, y=160)

        self.add_new_channel_button = Button(self,
                                             text='Add New Channel',
                                             command=self.add_new_channel)
        self.add_new_channel_button.place(x=250, y=160)

        self.delete_new_channel_button = Button(self,
                                                text='Delete Channel',
                                                command=self.delete_channel)
        self.delete_new_channel_button.place(x=400, y=160)

        self.clear_all_channels_button = Button(
            self, text='Clear All Channels', command=self.clear_all_channels)
        self.clear_all_channels_button.place(x=250, y=210)

        self.clear_channel_button = Button(self,
                                           text='Clear Channel',
                                           command=self.clear_current_channel)
        self.clear_channel_button.place(x=400, y=210)

        self.configure_instrument_button = Button(
            self,
            text='Configure Instrument',
            command=self.configure_instrument)
        self.configure_instrument_button.place(x=710, y=210)

        self.clear_instrument_button = Button(
            self,
            text='Clear Instrument',
            command=self.clear_current_instrument)
        self.clear_instrument_button.place(x=710, y=160)
        self.export_button = Button(self,
                                    text='Export',
                                    command=self.open_export_menu)
        self.export_button.place(x=0, y=260)
        self.import_musicpy_code_button = Button(
            self, text='Import Musicpy Code', command=self.import_musicpy_code)
        self.import_musicpy_code_button.place(x=0, y=410)

        self.check_enable_label = Label(self,
                                        text=self.language_dict['mixer'][6],
                                        x=680,
                                        y=60)
        self.check_enable_button = CheckBox(self,
                                            value=False,
                                            command=self.change_enabled,
                                            x=730,
                                            y=60)

        self.show()

    def init_parameters(self):
        self.font_type = current_settings.text_area_font_type
        self.font_size = current_settings.text_area_font_size
        self.current_bpm = 120
        self.current_playing = []
        self.piece_playing = []
        self.default_load = False
        self.project_name = 'untitled.mdp'
        self.project_name_file_path = None
        self.channel_names = [self.language_dict['init'][0]]
        self.channel_instrument_names = [current_settings.sound_path]
        self.channel_effects = [[]]
        self.master_effects = []
        self.channel_enabled = [True]
        self.channel_num = 1
        self.channel_list_focus = False
        self.project_dict = {}
        self.current_loading_num = 0
        self.current_project_file_path = ''
        self.last_path = ''
        if os.path.exists('last_path.txt'):
            with open('last_path.txt', encoding='utf-8') as f:
                self.last_path = f.read()
        self.pitch_shifter_window = None
        self.debug_window = None
        self.configure_soundfont_file_window = None
        self.change_dict_window = None
        self.current_config_window = None

    def init_menu(self):
        self.export_audio_menubar = self.get_menu(
            text=self.language_dict['export audio formats'][4],
            actions=[
                self.get_action(
                    text=self.language_dict['export audio formats'][0],
                    command=lambda: self.export_audio_file(mode='wav')),
                self.get_action(
                    text=self.language_dict['export audio formats'][1],
                    command=lambda: self.export_audio_file(mode='mp3')),
                self.get_action(
                    text=self.language_dict['export audio formats'][2],
                    command=lambda: self.export_audio_file(mode='ogg')),
                self.get_action(
                    text=self.language_dict['export audio formats'][3],
                    command=lambda: self.export_audio_file(mode='other'))
            ])
        self.export_menubar = self.get_menu(
            text=self.language_dict['right key'][8],
            actions=[
                self.export_audio_menubar,
                self.get_action(
                    text=self.language_dict['export audio formats'][5],
                    command=self.export_midi_file)
            ])
        self.set_musicpy_code_text_actions = [
            self.get_action(text=self.language_dict['right key'][0],
                            command=self.cut),
            self.get_action(text=self.language_dict['right key'][1],
                            command=self.copy),
            self.get_action(text=self.language_dict['right key'][2],
                            command=self.paste),
            self.get_action(text=self.language_dict['right key'][3],
                            command=self.choose_all),
            self.get_action(text=self.language_dict['right key'][4],
                            command=self.inputs_undo),
            self.get_action(text=self.language_dict['right key'][5],
                            command=self.inputs_redo),
            self.get_action(text=self.language_dict['right key'][6],
                            command=self.save_current_musicpy_code),
            self.get_action(text=self.language_dict['right key'][7],
                            command=self.import_musicpy_code),
            self.export_menubar,
            self.get_action(text=self.language_dict['right key'][9],
                            command=self.play_selected_musicpy_code),
            self.get_action(text=self.language_dict['right key'][10],
                            command=self.play_selected_audio)
        ]
        self.file_menu = self.get_menu(actions=[
            self.get_action(text=self.language_dict['file'][7],
                            command=self.open_new_project_file),
            self.get_action(text=self.language_dict['file'][0],
                            command=self.open_project_file),
            self.get_action(text=self.language_dict['file'][1],
                            command=self.save_as_project_file),
            self.get_action(
                text=self.language_dict['file'][6],
                command=lambda: self.save_as_project_file(new=True)),
            self.get_action(text=self.language_dict['file'][2],
                            command=self.import_midi_file_func),
            self.get_action(text=self.language_dict['file'][3],
                            command=self.save_current_musicpy_code),
            self.get_action(text=self.language_dict['file'][4],
                            command=self.import_musicpy_code),
            self.export_menubar,
            self.get_action(text=self.language_dict['file'][8],
                            command=self.save_current_instrument_parameters),
            self.get_action(text=self.language_dict['file'][9],
                            command=self.import_channel_settings)
        ])

        self.options_menu = self.get_menu(actions=[
            self.get_action(text=self.language_dict['option'][0],
                            command=self.open_change_settings),
            self.get_action(text=self.language_dict['option'][1],
                            command=self.change_channel_dict)
        ])

        self.change_languages_menu = self.get_menu(
            text=self.language_dict['option'][2], actions=[])
        os.chdir(abs_path)
        current_languages = [
            os.path.splitext(i)[0] for i in os.listdir('scripts/languages')
        ]
        for each in current_languages:
            self.change_languages_menu.addAction(
                self.get_action(text=each,
                                command=lambda e, each=each: self.
                                change_language(each, 1)))

        self.options_menu.addMenu(self.change_languages_menu)

        self.change_skin_menu = self.get_menu(
            text=self.language_dict['option'][3], actions=[])

        current_skins = [
            os.path.splitext(i)[0] for i in os.listdir('scripts/skins')
        ]
        for each in current_skins:
            self.change_skin_menu.addAction(
                self.get_action(
                    text=each,
                    command=lambda e, each=each: self.change_skin(each)))

        self.options_menu.addMenu(self.change_skin_menu)
        self.options_menu.addAction(
            self.get_action(text=self.language_dict['option'][4],
                            command=self.open_mixer))

        self.tools_menu = self.get_menu(actions=[
            self.get_action(text=self.language_dict['tool'][0],
                            command=self.make_mdi_file),
            self.get_action(text=self.language_dict['tool'][1],
                            command=self.import_mdi_file),
            self.get_action(text=self.language_dict['tool'][2],
                            command=self.unzip_mdi_file),
            self.get_action(text=self.language_dict['tool'][3],
                            command=self.import_audio_file_as_sample),
            self.get_action(text=self.language_dict['tool'][4],
                            command=self.open_pitch_shifter)
        ])

        self.import_instrument_menubar = self.get_menu(actions=[
            self.get_action(text=self.language_dict['import_instrument'][0],
                            command=self.import_instrument_folder),
            self.get_action(text=self.language_dict['import_instrument'][1],
                            command=self.import_soundfont_file),
            self.get_action(text=self.language_dict['import_instrument'][2],
                            command=self.import_mdi_file),
            self.get_action(text=self.language_dict['import_instrument'][3],
                            command=self.import_python_instrument),
            self.get_action(text=self.language_dict['import_instrument'][4],
                            command=self.import_instrument_parameters)
        ])

        self.configure_instrument_menubar = self.get_menu(actions=[
            self.get_action(text=self.language_dict["import_instrument"][1],
                            command=self.configure_soundfont_file),
            self.get_action(text=self.language_dict["import_instrument"][3],
                            command=self.configure_python_instrument)
        ])

    def initialize(self, mode=0, file=None):
        if mode == 0:
            self.channel_dict = [copy(current_settings.notedict)]
            self.channel_instruments = [None]
            if os.path.exists(current_settings.sound_path):
                self.show_msg(self.language_dict['msg'][0])
                self.import_default_instrument()
            else:
                self.default_load = True
        elif mode == 1:
            self.channel_dict = []
            self.channel_instruments = []
            self.default_load = True
            self.project_dict = self.get_project_dict()
            self.check_if_edited()
            self.open_project_file(file)

    def import_default_instrument(self):
        if os.path.isfile(current_settings.sound_path):
            self.import_soundfont_file(current_ind=0,
                                       sound_path=current_settings.sound_path)
            self.default_load = True
            self.project_dict = self.get_project_dict()
            self.check_if_edited()
        else:
            current_queue = multiprocessing.Queue()
            current_process = multiprocessing.Process(
                target=load_audiosegments,
                args=(current_settings.notedict, current_settings.sound_path,
                      current_queue))
            current_process.start()
            self.current_loading_num += 1
            self.wait_for_load_audiosegments(current_queue)

    def wait_for_load_audiosegments(self,
                                    current_queue,
                                    current_ind=None,
                                    current_mode=None,
                                    sound_path=''):
        if current_queue.empty():
            QtCore.QTimer.singleShot(
                200, lambda: self.wait_for_load_audiosegments(
                    current_queue, current_ind, current_mode, sound_path))
        else:
            if current_ind is None:
                self.channel_instruments = [current_queue.get()]
                self.show_msg(self.language_dict['msg'][1])
                self.default_load = True
                self.project_dict = self.get_project_dict()
                self.check_if_edited()
                self.current_loading_num -= 1
            else:
                self.channel_instruments[current_ind] = current_queue.get()
                if not current_mode:
                    self.current_channel_instruments_entry.clear()
                    self.current_channel_instruments_entry.setText(sound_path)
                    self.current_channel_instruments_entry.setCursorPosition(0)
                    self.channel_instrument_names[current_ind] = sound_path
                current_msg = self.language_dict["msg"][10].split('|')
                self.show_msg(
                    f'{current_msg[0]}{os.path.basename(sound_path)}{current_msg[1]}{current_ind+1}'
                )
                self.current_loading_num -= 1

    def check_if_edited(self):
        self.get_current_line_column()
        if self.is_changed():
            self.setWindowTitle('Musicpy Daw *')
        else:
            self.setWindowTitle('Musicpy Daw')
        self.after(100, self.check_if_edited)

    def get_current_line_column(self):
        self.current_line_number = self.set_musicpy_code_text.textCursor(
        ).blockNumber() + 1
        self.current_column_number = self.set_musicpy_code_text.textCursor(
        ).columnNumber() + 1
        self.line_column.setText(
            f'Line {self.current_line_number} Col {self.current_column_number}'
        )
        self.line_column.adjustSize()

    def change_font_size(self, e):
        num = e.delta // 120
        self.font_size += num
        if self.font_size < 1:
            self.font_size = 1
        self.set_musicpy_code_text.configure(font=(self.font_type,
                                                   self.font_size))

    def open_new_project_file(self):
        self.current_project_name.configure(text='untitled.mdp')
        self.project_name = 'untitled.mdp'
        self.project_name_file_path = None
        self.clear_all_channels(1)
        self.set_musicpy_code_text.clear()
        self.choose_channels.addItem(self.language_dict['init'][0])
        self.channel_names = [self.language_dict['init'][0]]
        self.channel_instrument_names = [current_settings.sound_path]
        self.channel_effects = [[]]
        self.master_effects.clear()
        self.channel_enabled = [True]
        self.channel_num = 1
        self.channel_list_focus = True
        self.change_current_bpm_entry.clear()
        self.change_current_bpm_entry.setText('120')
        self.change_current_bpm_entry.place(x=100, y=210)
        self.current_bpm = 120
        self.initialize()
        self.show_msg('')

    def show_msg(self, text=''):
        self.msg.setText(text)
        self.msg.adjustSize()
        self.msg.repaint()
        app.processEvents()

    def change_language(self, language, mode=0):
        os.chdir(abs_path)
        try:
            with open(f'scripts/languages/{language}.json',
                      encoding='utf-8') as f:
                data = json.load(f)
            self.main_window_language_dict = data['main_window']
            self.language_dict = data['other']
            if mode == 1:
                self.reload_language()
                change_parameter('default_language', language, settings_path)
        except Exception as e:
            current_msg = self.language_dict['msg'][2].split('|')
            self.show_msg(f'{current_msg[0]}{language}.py{current_msg[1]}')

    def reload_language(self):
        self.init_menu()
        for each, value in self.main_window_language_dict.items():
            current_widget = vars(self)[each]
            current_widget.setText(value)
            current_widget.adjustSize()
        self.set_musicpy_code_text = CustomTextEdit(
            self,
            pairing_symbols=current_settings.pairing_symbols,
            custom_actions=self.set_musicpy_code_text_actions,
            size=(810, 335),
            font=QtGui.QFont(current_settings.text_area_font_type,
                             current_settings.text_area_font_size),
            place=(150, 250))
        self.set_musicpy_code_text.show()
        self.show_msg('')

    def update_last_path(self, path):
        if not os.path.isdir(path):
            current_path = os.path.dirname(path)
        else:
            current_path = path
        if current_path != self.last_path:
            with open('last_path.txt', 'w', encoding='utf-8') as f:
                f.write(current_path)
            self.last_path = current_path

    def import_audio_file_as_sample(self):
        file_path = Dialog(
            caption=self.language_dict['title'][0],
            directory=self.last_path,
            filter=f"{self.language_dict['title'][1]} (*)").filename[0]
        if file_path:
            self.update_last_path(file_path)
            current_text = self.set_musicpy_code_text.toPlainText()
            if current_text[current_text.rfind('\n') + 1:]:
                self.set_musicpy_code_text.appendPlainText(
                    f"\nnew_sound = sound('{file_path}')\n")
            else:
                self.set_musicpy_code_text.appendPlainText(
                    f"new_sound = sound('{file_path}')\n")
            self.set_musicpy_code_text.activateWindow()
            self.set_musicpy_code_text.moveCursor(QtGui.QTextCursor.End)
        else:
            return

    def open_pitch_shifter(self):
        self.pitch_shifter_window = Pitch_shifter_window(self)

    def open_mixer(self):
        self.mixer_window = Mixer_window(self)

    def configure_python_instrument(self):
        current_ind = self.choose_channels.currentIndex().row()
        if current_ind < self.channel_num and self.channel_list_focus:
            current_instrument = self.channel_instruments[current_ind]
            if current_instrument.__class__.__name__ == 'Synth':
                self.current_instrument_window = Python_instrument_window(
                    self, current_ind=current_ind)
        else:
            self.show_msg(self.language_dict['msg'][8])

    def play_selected_musicpy_code(self):
        if not self.default_load:
            return
        self.show_msg('')
        if not self.channel_instruments:
            self.show_msg(self.language_dict['msg'][3])
            return
        try:
            current_notes = self.set_musicpy_code_text.textCursor(
            ).selectedText()
        except:
            return
        current_channel_num = 0
        current_bpm = self.current_bpm
        current_codes = self.set_musicpy_code_text.toPlainText()
        try:
            exec(current_codes, globals(), globals())
        except:
            pass
        lines = current_notes.split('\n')
        find_command = False
        current_chord = None
        for k in range(len(lines)):
            each = lines[k]
            if each.startswith('play '):
                find_command = True
                current_chord = each[5:]
                lines[k] = ''
            elif each.startswith('play(') or each.startswith(
                    'export(') or each.startswith('play_midi('):
                find_command = True
        if find_command:
            current_notes = '\n'.join(lines)
        try:
            exec(current_notes, globals(), globals())
        except Exception as e:
            self.show_msg(self.language_dict["msg"][4])
            output(traceback.format_exc())
            return
        if current_chord is None:
            try:
                current_chord = eval(current_notes)
            except:
                return
        else:
            try:
                current_chord = eval(current_chord)
            except:
                self.show_msg(self.language_dict["msg"][4])
                output(traceback.format_exc())
                return
        if isinstance(current_chord, tuple):
            length = len(current_chord)
            if length > 1:
                if length == 2:
                    current_chord, current_bpm = current_chord
                elif length == 3:
                    current_chord, current_bpm, current_channel_num = current_chord
                if isinstance(current_bpm, (int, float)):
                    if isinstance(current_bpm,
                                  float) and current_bpm.is_integer():
                        current_bpm = int(current_bpm)
                    self.change_current_bpm_entry.clear()
                    self.change_current_bpm_entry.setText(str(current_bpm))
                    self.change_current_bpm(1)
        self.stop_playing()
        try:
            self.play_musicpy_sounds(current_chord, current_bpm,
                                     current_channel_num)
        except Exception as e:
            self.show_msg(self.language_dict["msg"][4])
            output(traceback.format_exc())

    def play_selected_audio(self):
        if not self.default_load:
            return
        self.show_msg('')
        try:
            current_notes = self.set_musicpy_code_text.textCursor(
            ).selectedText()
        except:
            return
        current_codes = self.set_musicpy_code_text.toPlainText()
        try:
            exec(current_codes, globals(), globals())
        except:
            pass
        try:
            current_audio = eval(current_notes)
            pygame.mixer.stop()
            play_audio(current_audio)
        except Exception as e:
            output(traceback.format_exc())
            self.show_msg(self.language_dict['msg'][5])

    def make_mdi_file(self):
        self.show_msg('')
        file_path = Dialog(caption=self.language_dict['title'][5],
                           directory=self.last_path,
                           mode=1).directory
        if not file_path:
            return
        self.update_last_path(file_path)
        export_path = Dialog(caption=self.language_dict['title'][6],
                             directory=self.last_path,
                             mode=1).directory
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
                with open(t, encoding='utf-8') as f:
                    current_settings = f.read()
            else:
                with open(t, 'rb') as f:
                    current_samples[t] = f.read()
        current_mdi = mdi(current_samples, current_settings)
        os.chdir(export_path)
        with open(f'{name}.mdi', 'wb') as f:
            pickle.dump(current_mdi, f)
        current_msg = self.language_dict['msg'][7]
        self.show_msg(f'{current_msg} {name}.mdi')
        os.chdir(abs_path)
        return

    def import_mdi_file(self, mode=0, current_ind=None, sound_path=None):
        self.show_msg('')
        if current_ind is None:
            current_ind = self.choose_channels.currentIndex().row()
        if current_ind >= self.channel_num or not self.channel_list_focus:
            self.show_msg(self.language_dict['msg'][8])
            return
        abs_path = os.getcwd()
        if sound_path is None:
            if mode == 0:
                sound_path = Dialog(
                    caption=self.language_dict['title'][7],
                    directory=self.last_path,
                    filter=
                    f"Musicpy Daw Instrument (*.mdi);;{self.language_dict['title'][1]} (*)"
                ).filename[0]
                if not sound_path:
                    return
                self.update_last_path(sound_path)
            else:
                sound_path = self.current_channel_instruments_entry.text()
        original_sound_path = sound_path
        if not os.path.exists(sound_path):
            sound_path = os.path.join(self.current_project_file_path,
                                      sound_path)

        if not os.path.exists(sound_path):
            return

        self.show_msg(
            f'{self.language_dict["msg"][9]}{os.path.basename(sound_path)} ...'
        )
        try:
            with open(sound_path, 'rb') as file:
                current_mdi = pickle.load(file)
            channel_settings = current_mdi.settings
            current_samples = current_mdi.samples
            filenames = list(current_samples.keys())
            sound_files_audio = [
                AudioSegment.from_file(
                    BytesIO(current_samples[i]),
                    format=os.path.splitext(i)[1][1:]).set_frame_rate(
                        current_settings.frequency).set_channels(
                            2).set_sample_width(2) for i in filenames
            ]
            self.channel_dict[current_ind] = copy(current_settings.notedict)
            if channel_settings is not None:
                self.import_channel_settings(text=channel_settings)
            current_dict = self.channel_dict[current_ind]
            filenames = [os.path.splitext(i)[0] for i in filenames]
            result_audio = {
                filenames[i]: sound_files_audio[i]
                for i in range(len(filenames))
            }
        except:
            self.show_msg(self.language_dict['msg'][46])
            return
        self.channel_instruments[current_ind] = {
            i: (result_audio[current_dict[i]]
                if current_dict[i] in result_audio else None)
            for i in current_dict
        }
        self.channel_instrument_names[current_ind] = original_sound_path
        self.current_channel_instruments_entry.clear()
        self.current_channel_instruments_entry.setText(original_sound_path)
        self.current_channel_instruments_entry.setCursorPosition(0)
        current_msg = self.language_dict["msg"][10].split('|')
        self.show_msg(
            f'{current_msg[0]}{os.path.basename(sound_path)}{current_msg[1]}{current_ind+1}'
        )

    def unzip_mdi_file(self):
        self.show_msg('')
        abs_path = os.getcwd()
        file_path = Dialog(
            caption=self.language_dict['title'][7],
            directory=self.last_path,
            filter=
            f"Musicpy Daw Instrument (*.mdi);;{self.language_dict['title'][1]} (*)"
        ).filename[0]
        if not file_path:
            return

        self.update_last_path(file_path)
        export_path = Dialog(caption=self.language_dict['title'][8],
                             directory=self.last_path,
                             mode=1).directory
        if export_path:
            os.chdir(export_path)
        folder_name = os.path.basename(file_path)
        folder_name = folder_name[:folder_name.rfind('.')]
        if folder_name not in os.listdir():
            os.mkdir(folder_name)
        with open(file_path, 'rb') as file:
            current_mdi = pickle.load(file)
        os.chdir(folder_name)
        for each in current_mdi.samples:
            with open(each, 'wb') as f:
                f.write(current_mdi.samples[each])
        current_msg = self.language_dict["msg"][11].split('|')
        self.show_msg(
            f'{current_msg[0]}{os.path.basename(file_path)}{current_msg[1]}')
        os.chdir(abs_path)

    def import_python_instrument(self,
                                 mode=0,
                                 current_ind=None,
                                 sound_path=None):
        has_current_ind = False
        if current_ind is not None:
            has_current_ind = True
        else:
            current_ind = self.choose_channels.currentIndex().row()
        if current_ind < self.channel_num and (self.channel_list_focus
                                               or has_current_ind):
            self.show_msg('')
            if sound_path is not None:
                original_sound_path = sound_path
                if not os.path.exists(sound_path):
                    sound_path = os.path.join(self.current_project_file_path,
                                              sound_path)
                self.show_msg(
                    f'{self.language_dict["msg"][33]}{self.channel_names[current_ind]} ...'
                )
                try:
                    current_instrument = importfile(sound_path).Synth()
                    self.channel_instrument_names[current_ind] = sound_path
                    self.channel_instruments[current_ind] = current_instrument
                    self.current_channel_instruments_entry.clear()
                    self.current_channel_instruments_entry.setText(sound_path)
                    self.current_channel_instruments_entry.setCursorPosition(0)
                except:
                    self.show_msg(self.language_dict["python instrument"][1])
                    return
                self.channel_instruments[current_ind] = current_instrument
                self.channel_instrument_names[
                    current_ind] = original_sound_path
                current_msg = self.language_dict["msg"][10].split('|')
                self.show_msg(
                    f'{current_msg[0]}{os.path.basename(sound_path)}{current_msg[1]}{current_ind+1}'
                )
            else:
                if mode == 0:
                    filename = Dialog(
                        caption=self.language_dict['title'][17],
                        directory=self.last_path,
                        filter=
                        f'python (*.py);;{self.language_dict["title"][1]} (*)'
                    ).filename[0]
                    if filename:
                        self.update_last_path(filename)
                else:
                    filename = self.current_channel_instruments_entry.text()
                original_filename = filename
                if not os.path.exists(filename):
                    filename = os.path.join(self.current_project_file_path,
                                            filename)
                if filename and os.path.exists(filename):
                    try:
                        current_instrument = importfile(filename).Synth()
                        self.channel_instrument_names[current_ind] = filename
                        self.channel_instruments[
                            current_ind] = current_instrument
                        self.current_channel_instruments_entry.clear()
                        self.current_channel_instruments_entry.setText(
                            filename)
                        self.current_channel_instruments_entry.setCursorPosition(
                            0)
                        current_msg = self.language_dict["msg"][10].split('|')
                        self.show_msg(
                            f'{current_msg[0]}{os.path.basename(filename)}{current_msg[1]}{current_ind+1}'
                        )
                    except:
                        self.show_msg(
                            self.language_dict["python instrument"][1])
        else:
            self.show_msg(self.language_dict['msg'][8])

    def import_instrument_parameters(self):
        current_ind = self.choose_channels.currentRow()
        if current_ind < 0 or not self.channel_list_focus:
            self.show_msg(self.language_dict['msg'][8])
            return
        filename = Dialog(
            caption=self.language_dict['title'][17],
            directory=self.last_path,
            filter=
            f'Musicpy Daw parameters (*.mdparam);;{self.language_dict["title"][1]} (*)'
        ).filename[0]
        if filename:
            self.update_last_path(filename)
            try:
                with open(filename, encoding='utf-8') as f:
                    data = json.load(f)
                file_path = data['file_path']
                self.channel_dict[current_ind] = data['channel_dict']
                self.channel_instrument_names[current_ind] = file_path
                self.reload_channel_sounds(current_ind)
                current_instrument = self.channel_instruments[current_ind]
                current_type = data['type']
                if current_type == 'SoundFont':
                    current_soundfont_info = data['SoundFont parameters']
                    current_instrument.change(
                        channel=current_soundfont_info['channel'],
                        sfid=current_soundfont_info['sfid'],
                        bank=current_soundfont_info['bank'],
                        preset=current_soundfont_info['preset'])
                elif current_type == 'python instrument':
                    current_python_instrument_info = data[
                        'python instrument parameters']
                    current_instrument.instrument_parameters.update(
                        current_python_instrument_info['instrument_parameters']
                    )
                    current_instrument.effect_parameters.update(
                        current_python_instrument_info['effect_parameters'])
                    current_instrument.enabled = current_python_instrument_info[
                        'enabled']
                self.current_channel_instruments_entry.setText(
                    self.channel_instrument_names[current_ind])
            except:
                output(traceback.format_exc())
                self.show_msg(self.language_dict["msg"][30])

    def import_musicpy_code(self):
        filename = Dialog(
            caption=self.language_dict['title'][9],
            directory=self.last_path,
            filter=
            f'{self.language_dict["title"][19]} (*.txt);;{self.language_dict["title"][1]} (*)'
        ).filename[0]
        if filename:
            self.update_last_path(filename)
            try:
                with open(filename, encoding='utf-8', errors='ignore') as f:
                    self.set_musicpy_code_text.clear()
                    self.set_musicpy_code_text.insertPlainText(f.read())
            except:
                self.set_musicpy_code_text.clear()
                self.show_msg(self.language_dict["msg"][12])

    def save_current_instrument_parameters(self):
        current_ind = self.choose_channels.currentRow()
        if current_ind < 0 or not self.channel_list_focus:
            self.show_msg(self.language_dict['msg'][8])
            return
        filename = Dialog(
            caption=self.language_dict['file'][8],
            directory=self.last_path,
            filter=
            f"Musicpy Daw Parameters (*.mdparam);; {self.language_dict['title'][1]} (*)",
            default_filename=f"{self.language_dict['untitled']}.mdparam",
            mode=2).filename[0]
        if filename:
            current_instrument = self.channel_instruments[current_ind]
            if current_instrument is None:
                return
            current_instrument_name = self.channel_instrument_names[
                current_ind]
            parameter_dict = {}
            parameter_dict['file_path'] = current_instrument_name
            if isinstance(current_instrument, dict):
                parameter_dict['type'] = 'folder'
            elif isinstance(current_instrument, rs.sf2_loader):
                parameter_dict['type'] = 'SoundFont'
                current_info = {
                    'channel': current_instrument.current_channel,
                    'sfid': current_instrument.current_sfid,
                    'bank': current_instrument.current_bank,
                    'preset': current_instrument.current_preset
                }
                parameter_dict['SoundFont parameters'] = copy(current_info)
            elif isinstance(current_instrument, mdi):
                parameter_dict['type'] = 'mdi'
            elif current_instrument.__class__.__name__ == 'Synth':
                parameter_dict['type'] = 'python instrument'
                parameter_dict['python instrument parameters'] = {
                    'instrument_parameters':
                    current_instrument.instrument_parameters,
                    'effect_parameters': current_instrument.effect_parameters,
                    'enabled': current_instrument.enabled
                }
            else:
                return
            current_channel_dict = self.channel_dict[current_ind]
            parameter_dict['channel_dict'] = current_channel_dict
            self.update_last_path(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(parameter_dict,
                          f,
                          indent=4,
                          separators=(',', ': '),
                          ensure_ascii=False)

    def cut(self):
        self.set_musicpy_code_text.cut()

    def copy(self):
        self.set_musicpy_code_text.copy()

    def paste(self):
        self.set_musicpy_code_text.paste()

    def choose_all(self):
        self.set_musicpy_code_text.selectAll()

    def inputs_undo(self):
        self.set_musicpy_code_text.undo()

    def inputs_redo(self):
        self.set_musicpy_code_text.redo()

    def open_project_file(self, filename=None):
        if not self.default_load:
            return
        self.show_msg('')
        if not filename:
            filename = Dialog(
                caption=self.language_dict['title'][11],
                directory=self.last_path,
                filter=
                f"Musicpy Daw Project (*.mdp);;{self.language_dict['title'][10]} (.json);;{self.language_dict['title'][1]} (*)"
            ).filename[0]
        if filename:
            self.update_last_path(filename)
            try:
                with open(filename, encoding='utf-8', errors='ignore') as f:
                    self.project_dict = json.load(f)
            except:
                self.set_musicpy_code_text.clear()
                self.show_msg(self.language_dict["msg"][13])
                return
            self.current_project_file_path = os.path.dirname(filename)
        else:
            return
        self.default_load = False
        self.channel_list_focus = False
        self.clear_all_channels(1)
        self.channel_num = self.project_dict['channel_num']
        self.init_channels(self.channel_num)
        self.channel_names = self.project_dict['channel_names']
        self.channel_instrument_names = self.project_dict[
            'channel_instrument_names']
        self.channel_enabled = self.project_dict['channel_enabled']
        self.channel_dict = self.project_dict['channel_dict']
        self.current_bpm = self.project_dict['current_bpm']
        if isinstance(self.current_bpm,
                      float) and self.current_bpm.is_integer():
            self.current_bpm = int(self.current_bpm)
        self.change_current_bpm_entry.clear()
        self.change_current_bpm_entry.setText(str(self.current_bpm))
        self.set_musicpy_code_text.clear()
        self.set_musicpy_code_text.setPlainText(
            self.project_dict['current_musicpy_code'])
        self.current_channel_name_label.activateWindow()
        self.choose_channels.clear()
        for current_ind in range(self.channel_num):
            self.choose_channels.insertItem(current_ind,
                                            self.channel_names[current_ind])
        for i in range(self.channel_num):
            self.reload_channel_sounds(i)
        self.waiting_for_open_project_file(filename)

    def waiting_for_open_project_file(self, filename):
        if self.current_loading_num != 0:
            self.after(200,
                       lambda: self.waiting_for_open_project_file(filename))
        else:
            self.current_channel_instruments_entry.clear()
            self.choose_channels.clearSelection()
            current_project_name = os.path.basename(filename)
            self.current_project_name.configure(text=current_project_name)
            self.project_name = current_project_name
            self.project_name_file_path = filename
            current_soundfonts = self.project_dict['soundfont']
            for each in current_soundfonts:
                current_soundfont = self.channel_instruments[int(each)]
                if current_soundfont:
                    current_soundfont_info = current_soundfonts[each]
                    current_bank = current_soundfont_info['bank']
                    current_soundfont.change_bank(current_bank)
                    try:
                        current_soundfont.current_preset_name, current_soundfont.current_preset_ind = current_soundfont.get_all_instrument_names(
                            get_ind=True, mode=1, return_mode=1)
                    except:
                        current_soundfont.current_preset_name, current_soundfont.current_preset_ind = [], []
                    current_soundfont.change(
                        channel=current_soundfont_info['channel'],
                        sfid=current_soundfont_info['sfid'],
                        bank=current_soundfont_info['bank'],
                        preset=current_soundfont_info['preset'])
            current_python_instruments = self.project_dict[
                'python instruments']
            for each in current_python_instruments:
                current_python_instrument = self.channel_instruments[int(each)]
                current_python_instrument_info = current_python_instruments[
                    each]
                current_python_instrument.instrument_parameters.update(
                    current_python_instrument_info['instrument_parameters'])
                current_python_instrument.effect_parameters.update(
                    current_python_instrument_info['effect_parameters'])
            current_mixer_effects = self.project_dict['mixer']
            current_master_mixer_effects = current_mixer_effects['master']
            current_channel_mixer_effects = current_mixer_effects['channels']
            for i, each in enumerate(current_channel_mixer_effects):
                for j in each:
                    current_file_path = j['file_path']
                    current_effect = importfile(current_file_path).Synth()
                    current_effect.file_path = current_file_path
                    current_effect.instrument_parameters.update(
                        j['instrument_parameters'])
                    current_effect.effect_parameters.update(
                        j['effect_parameters'])
                    current_effect.enabled = j['enabled']
                    self.channel_effects[i].append(current_effect)
            for j in current_master_mixer_effects:
                current_file_path = j['file_path']
                current_effect = importfile(current_file_path).Synth()
                current_effect.file_path = current_file_path
                current_effect.instrument_parameters.update(
                    j['instrument_parameters'])
                current_effect.effect_parameters.update(j['effect_parameters'])
                current_effect.enabled = j['enabled']
                self.master_effects.append(current_effect)
            self.show_msg(self.language_dict["msg"][14])
            self.default_load = True
            self.project_dict = self.get_project_dict()

    def get_project_dict(self):
        project_dict = {}
        project_dict['channel_num'] = copy(self.channel_num)
        project_dict['channel_names'] = copy(self.channel_names)
        project_dict['channel_instrument_names'] = copy(
            self.channel_instrument_names)
        project_dict['channel_dict'] = copy(self.channel_dict)
        project_dict['channel_enabled'] = copy(self.channel_enabled)
        project_dict['current_bpm'] = copy(self.current_bpm)
        project_dict['current_musicpy_code'] = copy(
            self.set_musicpy_code_text.toPlainText())
        project_dict['soundfont'] = {}
        project_dict['python instruments'] = {}
        for i in range(len(self.channel_instruments)):
            current_instrument = self.channel_instruments[i]
            if isinstance(current_instrument, rs.sf2_loader):
                current_info = {
                    'channel': current_instrument.current_channel,
                    'sfid': current_instrument.current_sfid,
                    'bank': current_instrument.current_bank,
                    'preset': current_instrument.current_preset
                }
                project_dict['soundfont'][i] = copy(current_info)
            elif current_instrument.__class__.__name__ == 'Synth':
                project_dict['python instruments'][i] = {
                    'instrument_parameters':
                    copy(current_instrument.instrument_parameters),
                    'effect_parameters':
                    copy(current_instrument.effect_parameters)
                }
        current_master_effects = [{
            'file_path': k.file_path,
            'instrument_parameters': k.instrument_parameters,
            'effect_parameters': k.effect_parameters,
            'enabled': k.enabled
        } for k in copy(self.master_effects)]
        current_channel_effects = [[{
            'file_path': k.file_path,
            'instrument_parameters': k.instrument_parameters,
            'effect_parameters': k.effect_parameters,
            'enabled': k.enabled
        } for k in each] for each in copy(self.channel_effects)]
        project_dict['mixer'] = {
            'master': current_master_effects,
            'channels': current_channel_effects
        }
        return project_dict

    def save_as_project_file(self, new=False):
        if not self.default_load:
            return
        self.show_msg('')
        self.project_dict = self.get_project_dict()
        if not new and self.project_name_file_path:
            with open(self.project_name_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.project_dict,
                          f,
                          indent=4,
                          separators=(',', ': '),
                          ensure_ascii=False)
            self.show_msg(self.language_dict["msg"][15])
            return
        else:
            filename = Dialog(
                caption=self.language_dict['title'][12]
                if new else self.language_dict['title'][18],
                directory=self.last_path,
                filter=
                f"Musicpy Daw Project (*.mdp);;{self.language_dict['title'][10]} (*.json);;{self.language_dict['title'][1]} (*)",
                default_filename=os.path.splitext(self.project_name)[0],
                mode=2).filename[0]
            if filename:
                self.update_last_path(filename)
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.project_dict,
                              f,
                              indent=4,
                              separators=(',', ': '),
                              ensure_ascii=False)
                self.show_msg(self.language_dict["msg"][15])
                current_project_name = os.path.basename(filename)
                self.current_project_name.configure(text=current_project_name)
                self.project_name = current_project_name
                self.project_name_file_path = filename

    def save_current_musicpy_code(self):
        filename = Dialog(
            caption=self.language_dict['title'][13],
            directory=self.last_path,
            filter=f"{self.language_dict['title'][1]} (*)",
            default_filename=f"{self.language_dict['untitled']}.txt",
            mode=2).filename[0]
        if filename:
            self.update_last_path(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.set_musicpy_code_text.toPlainText())

    def file_top_make_menu(self, mode='file'):
        if mode == 'file':
            self.file_menu.popup(QtGui.QCursor().pos())
        elif mode == 'options':
            self.options_menu.popup(QtGui.QCursor().pos())
        elif mode == 'tools':
            self.tools_menu.popup(QtGui.QCursor().pos())

    def import_channel_settings(self, event, text=None):
        current_ind = self.choose_channels.currentIndex().row()
        if current_ind < self.channel_num and self.channel_list_focus:
            if text is None:
                filename = Dialog(
                    caption=self.language_dict['title'][14],
                    directory=self.last_path,
                    filter=
                    f"{self.language_dict['title'][19]} (*.txt);;{self.language_dict['title'][1]} (*)"
                ).filename[0]
                if filename:
                    self.update_last_path(filename)
                    with open(filename, encoding='utf-8') as f:
                        data = f.read()
                else:
                    return
            else:
                data = text
        else:
            self.show_msg(self.language_dict['msg'][8])
            return
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

    def import_soundfont_file(self, mode=0, current_ind=None, sound_path=None):
        has_current_ind = False
        if current_ind is not None:
            has_current_ind = True
        else:
            current_ind = self.choose_channels.currentIndex().row()
        if current_ind < self.channel_num and (self.channel_list_focus
                                               or has_current_ind):
            self.show_msg('')
            if sound_path is not None:
                original_sound_path = sound_path
                if not os.path.exists(sound_path):
                    sound_path = os.path.join(self.current_project_file_path,
                                              sound_path)
                self.show_msg(
                    f'{self.language_dict["msg"][33]}{self.channel_names[current_ind]} ...'
                )
                try:
                    current_soundfont = rs.sf2_loader(sound_path)
                    current_soundfont.all_instruments_dict = current_soundfont.all_instruments(
                    )
                    current_soundfont.all_available_banks = list(
                        current_soundfont.all_instruments_dict.keys())
                    try:
                        current_soundfont.current_preset_name, current_soundfont.current_preset_ind = current_soundfont.get_all_instrument_names(
                            get_ind=True, return_mode=1)
                    except:
                        current_soundfont.current_preset_name, current_soundfont.current_preset_ind = [], []
                except:
                    self.show_msg(self.language_dict["msg"][30])
                    return
                self.channel_instruments[current_ind] = current_soundfont
                self.channel_instrument_names[
                    current_ind] = original_sound_path
                current_msg = self.language_dict["msg"][10].split('|')
                self.show_msg(
                    f'{current_msg[0]}{os.path.basename(sound_path)}{current_msg[1]}{current_ind+1}'
                )
            else:
                if mode == 0:
                    sound_path = Dialog(
                        caption=self.language_dict['title'][17],
                        directory=self.last_path,
                        filter=
                        f"SoundFont (*.sf2 *.sf3 *.dls);;{self.language_dict['title'][1]} (*)"
                    ).filename[0]
                    if not sound_path:
                        return
                    self.update_last_path(sound_path)
                else:
                    sound_path = self.current_channel_instruments_entry.text()
                original_sound_path = sound_path
                if not os.path.exists(sound_path):
                    sound_path = os.path.join(self.current_project_file_path,
                                              sound_path)
                if sound_path and os.path.exists(sound_path):
                    try:
                        self.show_msg(
                            f'{self.language_dict["msg"][33]}{self.channel_names[current_ind]} ...'
                        )
                        current_soundfont = rs.sf2_loader(sound_path)
                        current_soundfont.all_instruments_dict = current_soundfont.all_instruments(
                        )
                        current_soundfont.all_available_banks = list(
                            current_soundfont.all_instruments_dict.keys())
                        try:
                            current_soundfont.current_preset_name, current_soundfont.current_preset_ind = current_soundfont.get_all_instrument_names(
                                get_ind=True, return_mode=1)
                        except:
                            current_soundfont.current_preset_name, current_soundfont.current_preset_ind = [], []
                        self.channel_instruments[
                            current_ind] = current_soundfont
                        self.channel_instrument_names[
                            current_ind] = original_sound_path
                        self.current_channel_instruments_entry.clear()
                        self.current_channel_instruments_entry.setText(
                            original_sound_path)
                        self.current_channel_instruments_entry.setCursorPosition(
                            0)
                        current_msg = self.language_dict["msg"][10].split('|')
                        self.show_msg(
                            f'{current_msg[0]}{os.path.basename(sound_path)}{current_msg[1]}{current_ind+1}'
                        )
                        self.choose_channels.setCurrentRow(current_ind)
                    except Exception as e:
                        output(traceback.format_exc())
                        self.show_msg(self.language_dict["msg"][30])
                        return
                else:
                    return
        else:
            self.show_msg(self.language_dict['msg'][8])

    def configure_soundfont_file(self):
        if self.configure_soundfont_file_window is not None and self.configure_soundfont_file_window.isVisible(
        ):
            self.configure_soundfont_file_window.activateWindow()
        else:
            current_ind = self.choose_channels.currentIndex().row()
            if current_ind < self.channel_num and self.channel_list_focus:
                current_soundfont = self.channel_instruments[current_ind]
                if isinstance(current_soundfont, rs.sf2_loader):
                    self.configure_soundfont_file_window = SoundFont_window(
                        self, current_soundfont=current_soundfont)
            else:
                self.show_msg(self.language_dict['msg'][8])

    def configure_instrument(self):
        self.configure_instrument_menubar.popup(QtGui.QCursor().pos())

    def open_export_menu(self):
        self.export_menubar.popup(QtGui.QCursor().pos())

    def ask_other_format(self, mode=0):
        self.ask_other_format_window = Ask_other_format_window(self, mode=mode)

    def export_audio_file(self,
                          obj=None,
                          mode='wav',
                          action='export',
                          channel_num=0,
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
        if not self.channel_instruments:
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
            filename = Dialog(
                caption=self.language_dict['title'][3],
                directory=self.last_path,
                filter=f"{self.language_dict['title'][1]} (*)",
                default_filename=
                f"{os.path.splitext(self.project_name)[0]}.{mode}",
                mode=2).filename[0]
            if not filename:
                return
            self.update_last_path(filename)
        if obj is None:
            obj = self.play_current_musicpy_code(mode=1)
        if isinstance(obj, chord):
            obj = ['chord', obj, channel_num]
        elif isinstance(obj, piece):
            obj = ['piece', obj]
        else:
            self.show_msg(self.language_dict["msg"][20])
            return
        if action == 'export':
            self.show_msg(f'{self.language_dict["msg"][21]}{filename}')
        if soundfont_args is None:
            soundfont_args = current_settings.default_soundfont_args
        types = obj[0]
        current_chord = obj[1]

        if types == 'chord':
            current_channel_num = obj[2]
            current_bpm = self.current_bpm
            current_chord = copy(current_chord)
            current_chord.normalize_tempo(bpm=current_bpm)
            for each in current_chord:
                if isinstance(each, AudioSegment):
                    each.duration = self.real_time_to_bar(
                        len(each), current_bpm)
                    each.volume = 127

            current_instruments = self.channel_instruments[current_channel_num]
            if not self.channel_enabled[current_channel_num]:
                current_chord.set_volume(0)
            if not all_has_audio(current_chord) and isinstance(
                    current_instruments, rs.sf2_loader):
                if action == 'export':
                    current_msg = self.language_dict["msg"][27].split('|')
                    self.show_msg(
                        f'{current_msg[0]}{self.language_dict["track"]} 1/1 {self.language_dict["channel"]} {current_channel_num + 1} (soundfont) '
                    )
                silent_audio = current_instruments.export_chord(
                    current_chord,
                    bpm=current_bpm,
                    start_time=current_chord.start_time,
                    get_audio=True,
                    effects=current_chord.effects
                    if check_effect(current_chord) else None,
                    length=length,
                    extra_length=extra_length,
                    **soundfont_args)
                current_effects = self.channel_effects[current_channel_num]
                for each_effect in current_effects:
                    if each_effect.enabled:
                        try:
                            silent_audio = each_effect.apply_effect(
                                silent_audio)
                        except:
                            output(traceback.format_exc())
            else:
                current_silent_audio = self.channel_to_audio(
                    current_chord,
                    current_channel_num=current_channel_num,
                    current_bpm=current_bpm,
                    mode=action,
                    length=length,
                    extra_length=extra_length)
                current_effects = self.channel_effects[current_channel_num]
                for each_effect in current_effects:
                    if each_effect.enabled:
                        try:
                            current_silent_audio = each_effect.apply_effect(
                                current_silent_audio)
                        except:
                            output(traceback.format_exc())
                current_start_time = self.bar_to_real_time(
                    current_chord.start_time, current_bpm, 1)
                silent_audio = AudioSegment.silent(
                    duration=len(current_silent_audio) + current_start_time)
                silent_audio = silent_audio.overlay(
                    current_silent_audio, position=current_start_time)
            for each_effect in self.master_effects:
                if each_effect.enabled:
                    try:
                        silent_audio = each_effect.apply_effect(silent_audio)
                    except:
                        output(traceback.format_exc())
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
            current_channels = current_chord.daw_channels if current_chord.daw_channels else [
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
            instruments_num = len(self.channel_instruments)
            track_number = len(current_chord)
            silent_audio = None
            for i in range(track_number):
                current_channel_number = current_channels[i]
                if current_channel_number >= instruments_num:
                    self.show_msg(
                        f'{self.language_dict["track"]} {i+1} : {self.language_dict["msg"][25]}{current_channel_number+1}'
                    )
                    continue
                current_instruments = self.channel_instruments[
                    current_channel_number]
                current_track = current_tracks[i]
                if not self.channel_enabled[current_channel_number]:
                    current_track.set_volume(0)
                if not all_has_audio(current_track) and isinstance(
                        current_instruments, rs.sf2_loader):
                    if action == 'export':
                        current_msg = self.language_dict["msg"][27].split('|')
                        self.show_msg(
                            f'{current_msg[0]}{self.language_dict["track"]} {i+1}/{track_number} {self.language_dict["channel"]} {current_channels[i] + 1} (soundfont)'
                        )
                    current_instrument = current_chord.instruments_numbers[i]
                    current_channel = current_chord.channels[
                        i] if current_chord.channels else current_instruments.current_channel
                    current_sfid, current_bank, current_preset = current_instruments.channel_info(
                        current_channel)
                    if current_sfid == 0:
                        current_instruments.change_sfid(
                            current_instruments.sfid_list[0], current_channel)
                        current_sfid, current_bank, current_preset = current_instruments.channel_info(
                            current_channel)
                    if isinstance(current_instrument, int):
                        current_instrument = [
                            current_instrument - 1, current_bank
                        ]
                    else:
                        current_instrument = [current_instrument[0] - 1
                                              ] + current_instrument[1:]
                    current_instruments.change(
                        channel=current_channel,
                        sfid=(current_instrument[2]
                              if len(current_instrument) > 2 else None),
                        bank=current_instrument[1],
                        preset=current_instrument[0],
                        mode=1)
                    current_silent_audio = current_instruments.export_chord(
                        current_track,
                        bpm=current_bpm,
                        get_audio=True,
                        channel=current_channel,
                        effects=current_track.effects
                        if check_effect(current_track) else None,
                        pan=current_pan[i],
                        volume=current_volume[i],
                        length=None if not track_lengths else track_lengths[i],
                        extra_length=None
                        if not track_extra_lengths else track_extra_lengths[i],
                        **soundfont_args)
                    current_instruments.change(current_channel,
                                               current_sfid,
                                               current_bank,
                                               current_preset,
                                               mode=1)

                else:
                    current_silent_audio = self.channel_to_audio(
                        current_track,
                        current_channel_num=current_channel_number,
                        current_bpm=current_bpm,
                        current_pan=current_pan[i],
                        current_volume=current_volume[i],
                        mode=action,
                        length=None if not track_lengths else track_lengths[i],
                        extra_length=None
                        if not track_extra_lengths else track_extra_lengths[i],
                        track_ind=i,
                        whole_track_number=track_number)
                current_effects = self.channel_effects[current_channel_number]
                for each_effect in current_effects:
                    if each_effect.enabled:
                        try:
                            current_silent_audio = each_effect.apply_effect(
                                current_silent_audio)
                        except:
                            output(traceback.format_exc())
                current_start_time = self.bar_to_real_time(
                    current_start_times[i] + current_track.start_time,
                    current_bpm, 1)
                current_audio_duration = current_start_time + len(
                    current_silent_audio)
                if silent_audio is None:
                    new_whole_duration = current_audio_duration
                    silent_audio = AudioSegment.silent(
                        duration=new_whole_duration)
                    silent_audio = silent_audio.overlay(
                        current_silent_audio, position=current_start_time)
                else:
                    silent_audio_duration = len(silent_audio)
                    new_whole_duration = max(current_audio_duration,
                                             silent_audio_duration)
                    new_silent_audio = AudioSegment.silent(
                        duration=new_whole_duration)
                    new_silent_audio = new_silent_audio.overlay(silent_audio)
                    new_silent_audio = new_silent_audio.overlay(
                        current_silent_audio, position=current_start_time)
                    silent_audio = new_silent_audio
            if check_effect(current_chord):
                silent_audio = process_effect(silent_audio,
                                              current_chord.effects,
                                              bpm=current_bpm)
            for each_effect in self.master_effects:
                if each_effect.enabled:
                    try:
                        silent_audio = each_effect.apply_effect(silent_audio)
                    except:
                        output(traceback.format_exc())
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
                    if current_settings.export_fadeout_use_ratio:
                        current_fadeout_time = each.duration * current_settings.export_audio_fadeout_time_ratio
                    else:
                        current_fadeout_time = self.real_time_to_bar(
                            current_settings.export_audio_fadeout_time, bpm)
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
                         current_bpm=None,
                         current_pan=None,
                         current_volume=None,
                         mode='export',
                         length=None,
                         extra_length=None,
                         track_ind=0,
                         whole_track_number=1):
        if len(self.channel_instruments) <= current_channel_num:
            self.show_msg(
                f'{self.language_dict["msg"][25]}{current_channel_num+1}')
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
        current_instrument = self.channel_instruments[current_channel_num]
        current_sound_path = self.channel_instrument_names[current_channel_num]
        current_position = 0
        whole_length = len(current_chord)
        if current_settings.show_convert_progress:
            counter = 1
        current_msg = self.language_dict["msg"][27].split('|')
        for i in range(whole_length):
            if mode == 'export' and current_settings.show_convert_progress:
                self.show_msg(
                    f'{current_msg[0]}{round((counter / whole_length) * 100, 3):.3f}{current_msg[1]} {self.language_dict["track"]} {track_ind+1}/{whole_track_number} {self.language_dict["channel"]} {current_channel_num + 1}'
                )
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
                    duration * current_settings.export_audio_fadeout_time_ratio
                ) if current_settings.export_fadeout_use_ratio else int(
                    current_settings.export_audio_fadeout_time)
                if isinstance(each, AudioSegment):
                    current_sound = each[:duration]
                else:
                    if current_instrument.__class__.__name__ == 'Synth':
                        current_sound = current_instrument.generate_sound(
                            each, current_bpm)
                    else:
                        each_name = str(each)
                        if each_name not in current_instrument:
                            each_name = str(~each)
                        if each_name not in current_instrument:
                            current_position += interval
                            continue
                        current_sound = current_instrument[each_name]
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
        return current_silent_audio

    def export_midi_file(self, event, current_chord=None, write_args={}):
        self.show_msg('')
        filename = Dialog(
            caption=self.language_dict['title'][15],
            directory=self.last_path,
            filter=f"{self.language_dict['title'][1]} (*)",
            default_filename=f"{os.path.splitext(self.project_name)[0]}.mid",
            mode=2).filename[0]
        if not filename:
            return
        self.update_last_path(filename)
        self.show_msg(f'{self.language_dict["msg"][21]}{filename}')
        if current_chord is None:
            current_chord = self.play_current_musicpy_code(mode=1)
        if current_chord is None:
            return
        write(current_chord, self.current_bpm, name=filename, **write_args)
        self.show_msg(f'{self.language_dict["msg"][24]}{filename}')

    def clear_current_channel(self):
        current_ind = self.choose_channels.currentIndex().row()
        if current_ind < self.channel_num and self.channel_list_focus:
            self.choose_channels.takeItem(current_ind)
            self.choose_channels.insertItem(current_ind,
                                            f'Channel {current_ind+1}')
            self.channel_names[current_ind] = f'Channel {current_ind+1}'
            self.channel_instrument_names[current_ind] = ''
            current_instrument = self.channel_instruments[current_ind]
            if isinstance(current_instrument, rs.sf2_loader):
                current_instrument.synth.delete()
            self.channel_instruments[current_ind] = None
            self.channel_effects[current_ind].clear()
            self.channel_enabled[current_ind] = True
            self.channel_dict[current_ind] = copy(current_settings.notedict)
            self.current_channel_name_entry.clear()
            self.current_channel_instruments_entry.clear()
        else:
            self.show_msg(self.language_dict['msg'][8])
            return

    def clear_current_instrument(self):
        current_ind = self.choose_channels.currentIndex().row()
        if current_ind < self.channel_num and self.channel_list_focus:
            self.channel_instrument_names[current_ind] = ''
            current_instrument = self.channel_instruments[current_ind]
            if isinstance(current_instrument, rs.sf2_loader):
                current_instrument.synth.delete()
            self.channel_instruments[current_ind] = None
            self.channel_dict[current_ind] = copy(current_settings.notedict)
            self.current_channel_instruments_entry.clear()
        else:
            self.show_msg(self.language_dict['msg'][8])
            return

    def clear_all_channels(self, mode=0):
        if mode == 0:
            if_clear = QtWidgets.QMessageBox.question(
                self, self.language_dict['other'][0],
                self.language_dict['other'][1])
            if if_clear == QtWidgets.QMessageBox.Yes:
                if_clear = True
            else:
                if_clear = False
        else:
            if_clear = True
        if if_clear:
            self.stop_playing()
            self.choose_channels.clear()
            self.channel_names.clear()
            self.channel_instrument_names.clear()
            for i in self.channel_instruments:
                if isinstance(i, rs.sf2_loader):
                    i.synth.delete()
            self.channel_instruments.clear()
            self.channel_dict.clear()
            self.channel_effects.clear()
            self.master_effects.clear()
            self.channel_enabled.clear()
            self.channel_num = 0
            self.current_channel_name_entry.clear()
            self.current_channel_instruments_entry.clear()
            self.check_enable_button.setChecked(False)

    def delete_channel(self):
        current_ind = self.choose_channels.currentIndex().row()
        if current_ind >= 0 and current_ind < self.channel_num and self.channel_list_focus:
            self.choose_channels.takeItem(current_ind)
            new_ind = min(current_ind, self.channel_num - 2)
            self.choose_channels.setCurrentRow(self.choose_channels.count() -
                                               1)
            del self.channel_names[current_ind]
            del self.channel_instrument_names[current_ind]
            current_instrument = self.channel_instruments[current_ind]
            if isinstance(current_instrument, rs.sf2_loader):
                current_instrument.synth.delete()
            del self.channel_instruments[current_ind]
            del self.channel_dict[current_ind]
            del self.channel_effects[current_ind]
            del self.channel_enabled[current_ind]
            self.channel_num -= 1
            if self.channel_num > 0:
                self.show_current_channel()
            else:
                self.current_channel_name_entry.clear()
                self.current_channel_instruments_entry.clear()
        else:
            self.show_msg(self.language_dict['msg'][8])
            return

    def add_new_channel(self):
        self.channel_num += 1
        current_channel_name = f'{self.language_dict["channel"]} {self.channel_num}'
        self.choose_channels.addItem(current_channel_name)
        self.choose_channels.clearSelection()
        self.choose_channels.setCurrentRow(self.choose_channels.count() - 1)
        self.channel_names.append(current_channel_name)
        self.channel_instrument_names.append('')
        self.channel_instruments.append(None)
        self.channel_dict.append(copy(current_settings.notedict))
        self.channel_effects.append([])
        self.channel_enabled.append(True)
        self.show_current_channel()

    def init_channels(self, num=1):
        self.channel_num = num
        for i in range(self.channel_num):
            current_channel_name = f'{self.language_dict["channel"]} {i+1}'
            self.choose_channels.insertItem(i, current_channel_name)
            self.channel_names.append(current_channel_name)
            self.channel_instrument_names.append('')
            self.channel_instruments.append(None)
            self.channel_dict.append(copy(current_settings.notedict))
            self.channel_effects.append([])
            self.channel_enabled.append(True)

    def change_channel_dict(self):
        if self.change_dict_window is not None and self.change_dict_window.isVisible(
        ):
            self.change_dict_window.activateWindow()
        else:
            current_ind = self.choose_channels.currentIndex().row()
            self.current_channel_dict_num = current_ind
            if current_ind < self.channel_num and self.channel_list_focus:
                self.change_dict_window = Channel_dict_window(
                    self, current_ind)
            else:
                self.show_msg(self.language_dict['msg'][8])
                return

    def closeEvent(self, event):
        current_text = self.set_musicpy_code_text.toPlainText()
        if not self.is_changed():
            event.accept()
            os._exit(0)
        else:
            event.ignore()
            self.close_window()

    def close_window(self):
        self.ask_save_window = Ask_save_window(self)

    def is_changed(self):
        if not self.default_load:
            return False
        current_project_dict = self.get_project_dict()
        if current_project_dict != self.project_dict:
            return True
        else:
            return False

    def save_and_quit(self):
        self.save_as_project_file()
        self.ask_save_window.close()
        self.close()
        os._exit(0)

    def reload_channel_sounds(self, current_ind=None):
        if current_ind is None:
            current_mode = 0
        else:
            current_mode = 1
        self.show_msg('')
        current_ind = self.current_channel_dict_num if not current_mode else current_ind
        sound_path = self.channel_instrument_names[current_ind]
        original_sound_path = sound_path
        if not os.path.exists(sound_path):
            sound_path = os.path.join(self.current_project_file_path,
                                      sound_path)
            if not os.path.exists(sound_path):
                return
        if os.path.isfile(sound_path):
            current_extension = os.path.splitext(sound_path)[1][1:].lower()
            if current_extension == 'mdi':
                self.import_mdi_file(current_ind=current_ind,
                                     sound_path=original_sound_path)
            elif current_extension in ['sf2', 'sf3', 'dls']:
                self.import_soundfont_file(current_ind=current_ind,
                                           sound_path=original_sound_path)
            elif current_extension == 'py':
                self.import_python_instrument(current_ind=current_ind,
                                              sound_path=original_sound_path)
        else:
            try:
                self.show_msg(
                    f'{self.language_dict["msg"][28]}{self.channel_names[current_ind]} ...'
                )

                notedict = self.channel_dict[current_ind]
                current_queue = multiprocessing.Queue()
                current_process = multiprocessing.Process(
                    target=load_audiosegments,
                    args=(notedict, sound_path, current_queue))
                current_process.start()
                self.current_loading_num += 1
                self.wait_for_load_audiosegments(current_queue, current_ind,
                                                 current_mode,
                                                 original_sound_path)
            except Exception as e:
                output(traceback.format_exc())
                self.show_msg(self.language_dict["msg"][30])

    def change_current_channel_name(self):
        current_ind = self.choose_channels.currentIndex().row()
        if current_ind < self.channel_num and self.channel_list_focus:
            current_channel_name = self.current_channel_name_entry.text()
            self.choose_channels.takeItem(current_ind)
            self.choose_channels.insertItem(current_ind, current_channel_name)
            self.choose_channels.setCurrentRow(self.choose_channels.count() -
                                               1)
            self.channel_names[current_ind] = current_channel_name
        else:
            self.show_msg(self.language_dict['msg'][8])
            return

    def show_current_channel(self):
        self.channel_list_focus = True
        current_ind = self.choose_channels.currentIndex().row()
        if current_ind >= 0 and current_ind < self.channel_num and self.channel_list_focus:
            self.current_channel_name_entry.clear()
            self.current_channel_name_entry.setText(
                self.channel_names[current_ind])
            self.current_channel_instruments_entry.clear()
            self.current_channel_instruments_entry.setText(
                self.channel_instrument_names[current_ind])
            self.current_channel_instruments_entry.setCursorPosition(0)
            self.check_enable_button.setChecked(
                self.channel_enabled[current_ind])

    def cancel_choose_channels(self):
        self.choose_channels.clearSelection()
        self.current_channel_name_entry.clear()
        self.current_channel_instruments_entry.clear()
        self.current_channel_name_label.activateWindow()
        self.channel_list_focus = False
        self.check_enable_button.setChecked(False)

    def import_midi_file_func(self):
        self.show_msg('')
        filename = Dialog(
            caption=self.language_dict['title'][16],
            directory=self.last_path,
            filter=f"MIDI (*.mid);;{self.language_dict['title'][1]} (*)"
        ).filename[0]
        if filename:
            self.update_last_path(filename)
            current_text = self.set_musicpy_code_text.toPlainText()
            if current_text[current_text.rfind('\n') + 1:]:
                self.set_musicpy_code_text.appendPlainText(
                    f'\nnew_midi_file = read("{filename}")\n')
            else:
                self.set_musicpy_code_text.appendPlainText(
                    f'new_midi_file = read("{filename}")\n')
            self.set_musicpy_code_text.activateWindow()
            self.set_musicpy_code_text.moveCursor(QtGui.QTextCursor.End)

    def import_instrument_func(self):
        sound_path = self.current_channel_instruments_entry.text()
        if not os.path.exists(sound_path):
            sound_path = os.path.join(self.current_project_file_path,
                                      sound_path)
        if os.path.isdir(sound_path):
            self.import_instrument_folder(1)
        elif os.path.isfile(sound_path):
            current_extension = os.path.splitext(sound_path)[1][1:].lower()
            if current_extension == 'mdi':
                self.import_mdi_file(1)
            elif current_extension in ['sf2', 'sf3', 'dls']:
                self.import_soundfont_file(1)
            elif current_extension == 'py':
                self.import_python_instrument(1)
        else:
            self.show_msg(self.language_dict["msg"][30])

    def import_instrument(self, mode=0):
        self.import_instrument_menubar.popup(QtGui.QCursor().pos())

    def import_instrument_folder(self, mode=0):
        current_ind = self.choose_channels.currentIndex().row()
        if current_ind < self.channel_num and self.channel_list_focus:
            self.show_msg('')
            if mode == 0:
                sound_path = Dialog(caption=self.language_dict['title'][17],
                                    directory=self.last_path,
                                    mode=1).directory
                if not sound_path:
                    return
                self.update_last_path(sound_path)
            else:
                sound_path = self.current_channel_instruments_entry.text()
            original_sound_path = sound_path
            if not os.path.exists(sound_path):
                sound_path = os.path.join(self.current_project_file_path,
                                          sound_path)
            if sound_path and os.path.exists(sound_path):
                try:
                    self.show_msg(
                        f'{self.language_dict["msg"][33]}{self.channel_names[current_ind]} ...'
                    )
                    sound_path = sound_path
                    notedict = self.channel_dict[current_ind]
                    current_queue = multiprocessing.Queue()
                    current_process = multiprocessing.Process(
                        target=load_audiosegments,
                        args=(notedict, sound_path, current_queue))
                    current_process.start()
                    self.current_loading_num += 1
                    self.wait_for_load_audiosegments(current_queue,
                                                     current_ind, None,
                                                     original_sound_path)
                except Exception as e:
                    output(traceback.format_exc())
                    self.show_msg(self.language_dict["msg"][30])
        else:
            self.show_msg(self.language_dict['msg'][8])

    def bar_to_real_time(self, bar, bpm, mode=0):
        # return time in ms
        return int((60000 / bpm) *
                   (bar * 4)) if mode == 0 else (60000 / bpm) * (bar * 4)

    def real_time_to_bar(self, time, bpm):
        return (time / (60000 / bpm)) / 4

    def change_current_bpm(self, mode=0):
        self.show_msg('')
        current_bpm = self.change_current_bpm_entry.text()
        try:
            current_bpm = float(current_bpm)
            if current_bpm.is_integer():
                current_bpm = int(current_bpm)
            self.current_bpm = current_bpm
            if mode == 0:
                self.show_msg(f'{self.language_dict["msg"][34]}{current_bpm}')
        except:
            if mode == 0:
                self.show_msg(self.language_dict["msg"][35])

    def play_note_func(self, name, duration, volume, channel=0):
        if not self.channel_enabled[channel]:
            return
        note_sounds = self.channel_instruments[channel]
        if name in note_sounds:
            current_sound = note_sounds[name]
            if current_sound:
                current_sound = pygame.mixer.Sound(
                    buffer=current_sound.raw_data)
                current_sound.set_volume(current_settings.global_volume *
                                         volume / 127)
                duration_time = self.bar_to_real_time(duration,
                                                      self.current_bpm,
                                                      mode=1)
                current_sound.play()
                current_fadeout_time = int(
                    duration_time *
                    current_settings.play_audio_fadeout_time_ratio
                ) if current_settings.play_fadeout_use_ratio else int(
                    current_settings.play_audio_fadeout_time)
                current_id = threading.Timer(
                    duration_time / 1000,
                    lambda: current_sound.fadeout(current_fadeout_time)
                    if current_fadeout_time != 0 else current_sound.stop())
                current_id.start()
                self.current_playing.append(current_id)

    def stop_playing(self):
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        if self.current_playing:
            for each in self.current_playing:
                each.cancel()
            self.current_playing.clear()
        if self.piece_playing:
            for each in self.piece_playing:
                each.cancel()
            self.piece_playing.clear()

    def play_current_musicpy_code(self, mode=0):
        if not self.default_load:
            return
        self.show_msg('')
        if not self.channel_instruments:
            self.show_msg(self.language_dict["msg"][18])
            return

        self.stop_playing()
        global global_play
        global_play = False
        current_notes = self.set_musicpy_code_text.toPlainText()
        current_channel_num = 0
        current_bpm = self.current_bpm
        lines = current_notes.split('\n')
        find_command = False
        current_chord = None
        for k in range(len(lines)):
            each = lines[k].lstrip(' ')
            if each.startswith('play '):
                find_command = True
                current_chord = each[5:]
                lines[k] = ''
            elif each.startswith('play(') or each.startswith(
                    'export(') or each.startswith(
                        'play_midi(') or each.startswith('output('):
                find_command = True
        if find_command:
            current_notes = '\n'.join(lines)
        try:
            exec(current_notes, globals(), globals())
        except Exception as e:
            self.show_msg(self.language_dict["msg"][4])
            output(traceback.format_exc())
            return
        if current_chord is None:
            return
        try:
            current_chord = eval(current_chord)
        except:
            self.show_msg(self.language_dict["msg"][4])
            output(traceback.format_exc())
            return
        if isinstance(current_chord, tuple):
            length = len(current_chord)
            if length > 1:
                if length == 2:
                    current_chord, current_bpm = current_chord
                elif length == 3:
                    current_chord, current_bpm, current_channel_num = current_chord
                if isinstance(current_bpm, (int, float)):
                    if isinstance(current_bpm,
                                  float) and current_bpm.is_integer():
                        current_bpm = int(current_bpm)
                    self.change_current_bpm_entry.clear()
                    self.change_current_bpm_entry.setText(str(current_bpm))
                    self.change_current_bpm(1)
        if mode == 0:
            try:
                self.play_musicpy_sounds(current_chord, current_bpm,
                                         current_channel_num)
            except Exception as e:
                if not global_play:
                    self.show_msg(self.language_dict["msg"][4])
                    output(traceback.format_exc())
        elif mode == 1:
            return current_chord

    def play_musicpy_sounds(self,
                            current_chord,
                            current_bpm=None,
                            current_channel_num=None,
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
            current_instrument = self.channel_instruments[current_channel_num]
            if check_special(current_chord) or isinstance(
                    current_instrument, rs.sf2_loader
            ) or current_instrument.__class__.__name__ == 'Synth' or self.channel_effects[
                    current_channel_num]:
                self.export_audio_file(action='play',
                                       channel_num=current_channel_num,
                                       obj=current_chord,
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
            current_bpm = current_chord.bpm
            if isinstance(current_bpm, float) and current_bpm.is_integer():
                current_bpm = int(current_bpm)
            self.change_current_bpm_entry.clear()
            self.change_current_bpm_entry.setText(str(current_bpm))
            self.change_current_bpm(1)
            current_channel_nums = current_chord.daw_channels if current_chord.daw_channels else [
                i for i in range(len(current_chord))
            ]
            if check_special(current_chord) or any(
                    isinstance(self.channel_instruments[i], rs.sf2_loader) or
                    self.channel_instruments[i].__class__.__name__ == 'Synth'
                    for i in current_channel_nums) or any(
                        i for i in self.channel_effects):
                self.export_audio_file(action='play',
                                       obj=current_chord,
                                       length=length,
                                       extra_length=extra_length,
                                       track_lengths=track_lengths,
                                       track_extra_lengths=track_extra_lengths,
                                       soundfont_args=soundfont_args)
                self.show_msg(self.language_dict["msg"][22])
                return
            else:
                current_tracks = current_chord.tracks
                current_start_times = current_chord.start_times
                if isinstance(current_bpm, float) and current_bpm.is_integer():
                    current_bpm = int(current_bpm)
                self.change_current_bpm_entry.clear()
                self.change_current_bpm_entry.setText(str(current_bpm))
                self.change_current_bpm(1)
                for each in range(len(current_chord)):
                    current_time = self.bar_to_real_time(
                        current_start_times[each] +
                        current_tracks[each].start_time,
                        self.current_bpm,
                        mode=1)
                    current_id = threading.Timer(
                        current_time / 1000,
                        lambda each=each: self.play_channel(
                            current_tracks[each], current_channel_nums[each]))
                    current_id.start()
                    self.piece_playing.append(current_id)
        self.show_msg(self.language_dict["msg"][22])

    def play_channel(self, current_chord, current_channel_num=0, start_time=0):
        if len(self.channel_instruments) <= current_channel_num:
            self.show_msg(
                f'{self.language_dict["msg"][25]}{current_channel_num+1}')
            return
        if not self.channel_instruments[current_channel_num]:
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
                current_id = threading.Timer(
                    current_time / 1000,
                    lambda each=each, duration=duration, volume=volume: self.
                    play_note_func(f'{standardize_note(each.name)}{each.num}',
                                   duration, volume, current_channel_num))
                current_id.start()
                self.current_playing.append(current_id)
                current_time += self.bar_to_real_time(current_intervals[i],
                                                      self.current_bpm, 1)

    def open_change_settings(self):
        if self.current_config_window is not None and self.current_config_window.isVisible(
        ):
            self.current_config_window.activateWindow()
        else:
            os.chdir(abs_path)
            self.current_config_window = config_window(
                config_path=settings_path, dpi=self.dpi, parent=self)
            self.current_config_window.setStyleSheet(self.get_stylesheet())

    def instruments(self, ind):
        return self.channel_instruments[ind]

    def instrument_names(self, ind):
        return self.channel_instrument_names[ind]

    def open_debug_window(self):
        self.debug_window = Debug_window(self)

    def init_skin(self, skin):
        os.chdir(abs_path)
        with open(f'scripts/skins/{skin}.json') as f:
            current_skin_dict = json.load(f)
        vars(current_settings).update(current_skin_dict)

    def change_skin(self, skin):
        os.chdir(abs_path)
        with open(f'scripts/skins/{skin}.json') as f:
            current_skin_dict = json.load(f)
        vars(current_settings).update(current_skin_dict)

        current_stylesheet = self.get_stylesheet()
        self.setStyleSheet(current_stylesheet)

        self.init_menu()

        current_settings.current_skin = skin
        change_parameter('current_skin', skin, settings_path)

    def change_enabled(self):
        current_ind = self.choose_channels.currentIndex().row()
        if current_ind >= 0:
            self.channel_enabled[
                current_ind] = self.check_enable_button.isChecked()


class mdi:

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
        if self.sounds.sample_width != 2:
            self.sounds = self.sounds.set_sample_width(2)
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
                                                       sr=self.sample_rate,
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
            result = result.set_frame_rate(current_settings.frequency)
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
            converting_note = current_daw.language_dict['Converting note']
            if pitch_shifter:
                current_daw.pitch_shifter_window.show_msg(
                    f'{converting_note} {current_note_name} ...')
            else:
                current_daw.show_msg(
                    f'{converting_note} {current_note_name} ...')
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
        Exporting = current_daw.language_dict['Exporting']
        for each in current_dict:
            if pitch_shifter:
                current_daw.pitch_shifter_window.show_msg(
                    f'{Exporting} {each} ...')
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
        if self.sounds.sample_width != 2:
            self.sounds = self.sounds.set_sample_width(2)
        self.sample_width = self.sounds.sample_width

    def __len__(self):
        return len(self.sounds)

    def play(self):
        play_audio(self)

    def stop(self):
        pygame.mixer.stop()


class Dialog(QtWidgets.QMainWindow):

    def __init__(self,
                 caption,
                 directory='',
                 filter=None,
                 default_filename=None,
                 mode=0):
        super().__init__()
        if mode == 0:
            self.filename = QtWidgets.QFileDialog.getOpenFileName(
                self, caption=caption, directory=directory, filter=filter)
        elif mode == 1:
            self.directory = QtWidgets.QFileDialog.getExistingDirectory(
                self, caption=caption, directory=directory)
        elif mode == 2:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(
                self,
                caption,
                os.path.join(directory, default_filename),
                filter=filter)


class Button(QtWidgets.QPushButton):

    def __init__(self, *args, command=None, x=None, y=None, **kwargs):
        super().__init__(*args, **kwargs)
        if command is not None:
            self.clicked.connect(command)
        if x is not None and y is not None:
            self.move(x, y)
        self.adjustSize()

    def place(self, x, y):
        self.move(x, y)


class Label(QtWidgets.QLabel):

    def __init__(self, *args, x=None, y=None, **kwargs):
        super().__init__(*args, **kwargs)
        if x is not None and y is not None:
            self.move(x, y)
        self.adjustSize()

    def place(self, x, y):
        self.move(x, y)

    def configure(self, text):
        self.setText(text)
        self.adjustSize()


class Slider(QtWidgets.QSlider):

    def __init__(self,
                 *args,
                 value=None,
                 command=None,
                 x=None,
                 y=None,
                 range=[0, 100],
                 width=200,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.setRange(*range)
        self.setFixedWidth(width)
        if value is not None:
            self.setValue(value)
        if command is not None:
            self.valueChanged.connect(command)
        if x is not None and y is not None:
            self.move(x, y)

    def place(self, x, y):
        self.move(x, y)

    def change(self, value):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)


class CheckBox(QtWidgets.QCheckBox):

    def __init__(self,
                 *args,
                 value=None,
                 command=None,
                 x=None,
                 y=None,
                 font=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        if value is not None:
            self.setChecked(value)
        if command is not None:
            self.clicked.connect(command)
        if x is not None and y is not None:
            self.move(x, y)
        if font is not None:
            self.setFont(font)
        self.adjustSize()

    def place(self, x, y):
        self.move(x, y)


class LineEdit(QtWidgets.QLineEdit):

    def __init__(self,
                 *args,
                 x=None,
                 y=None,
                 width=None,
                 height=None,
                 font=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        if x is not None and y is not None:
            self.move(x, y)
        if width is not None:
            self.setFixedWidth(width)
        if height is not None:
            self.setFixedHeight(height)
        if font is not None:
            self.setFont(font)
        self.adjustSize()

    def place(self, x, y):
        self.move(x, y)


class CustomTextEdit(QtWidgets.QPlainTextEdit):

    def __init__(self,
                 parent=None,
                 pairing_symbols=[],
                 custom_actions=[],
                 size=None,
                 font=None,
                 place=None):
        super().__init__(parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__contextMenu)
        self._completer = None
        self.pairing_symbols = pairing_symbols
        self.pairing_symbols_left = [each[0] for each in self.pairing_symbols]
        self.completion_prefix = ''
        self.default_completer_keys = [
            QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Escape,
            QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab
        ]
        self.special_words = "~!@#$%^&*()+{}|:\"<>?,./;'[]\\-="
        self.current_completion_words = function_names
        self.custom_actions = custom_actions
        if size is not None:
            self.setFixedSize(*size)
        if font is not None:
            self.setFont(font)
        if place is not None:
            self.move(*place)
        self.input_completer = QtWidgets.QCompleter(function_names)
        self.setCompleter(self.input_completer)

    def __contextMenu(self):
        self._normalMenu = self.createStandardContextMenu()
        self._normalMenu.clear()
        self._addCustomMenuItems(self._normalMenu)
        self._normalMenu.exec_(QtGui.QCursor.pos())

    def _addCustomMenuItems(self, menu):
        for i in self.custom_actions:
            if isinstance(i, QtWidgets.QAction):
                menu.addAction(i)
            elif isinstance(i, QtWidgets.QMenu):
                menu.addMenu(i)

    def setCompleter(self, completer):

        self._completer = completer
        completer.setWidget(self)
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.activated.connect(self.insertCompletion)

    def insertCompletion(self, completion):
        if self._completer.widget() is not self:
            return

        tc = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)

        if self.completion_prefix.lower() != completion[-extra:].lower():
            tc.insertText(completion[-extra:])
            self.setTextCursor(tc)
        if self.current_completion_words != function_names:
            self._completer.setModel(
                QtCore.QStringListModel(function_names, self._completer))
            self.current_completion_words = function_names

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, e):
        if self._completer is not None:
            self._completer.setWidget(self)
        super().focusInEvent(e)

    def keyPressEvent(self, e):

        isShortcut = False
        current_text = e.text()

        if current_text and current_text[-1] in self.pairing_symbols_left:
            self._completer.popup().hide()
            ind = self.pairing_symbols_left.index(current_text[-1])
            current_pairing_symbol = self.pairing_symbols[ind][1]
            super().keyPressEvent(e)
            self.insertPlainText(current_pairing_symbol)
            self.moveCursor(QtGui.QTextCursor.PreviousCharacter)
            return

        if self._completer is not None and self._completer.popup().isVisible():
            if e.key() in self.default_completer_keys:
                e.ignore()
                return

        if e.key() == QtCore.Qt.Key_Period:
            current_whole_text = self.toPlainText()
            current_row = current_whole_text.split('\n')[-1].replace(' ', '')
            current_word = current_row.split(',')[-1]
            try:
                exec(current_whole_text, globals(), globals())
                words = dir(eval(current_word))
                super().keyPressEvent(e)
                self._completer.setModel(
                    QtCore.QStringListModel(words, self._completer))
                self.current_completion_words = words
                isShortcut = True
            except:
                pass

        if self._completer is None or not isShortcut:
            super().keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (QtCore.Qt.ControlModifier
                                       | QtCore.Qt.ShiftModifier)
        if self._completer is None or (ctrlOrShift and not current_text):
            return
        hasModifier = (e.modifiers() !=
                       QtCore.Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()
        self.completion_prefix = completionPrefix
        if not isShortcut and (hasModifier or len(current_text) == 0
                               or len(completionPrefix) < 1
                               or current_text[-1] in self.special_words):
            self._completer.popup().hide()
            if self.current_completion_words != function_names:
                self._completer.setModel(
                    QtCore.QStringListModel(function_names, self._completer))
                self.current_completion_words = function_names
            return

        if completionPrefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completionPrefix)
            self._completer.popup().setCurrentIndex(
                self._completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(
            self._completer.popup().sizeHintForColumn(0) +
            self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)

    def zoom(self, delta):
        if delta < 0:
            self.zoomOut(1)
        elif delta > 0:
            self.zoomIn(1)

    def wheelEvent(self, event):
        if (event.modifiers() & QtCore.Qt.ControlModifier):
            self.zoom(event.angleDelta().y())
        else:
            super().wheelEvent(event)


class Channel(QtWidgets.QListWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            super().mousePressEvent(event)
            current_daw.show_current_channel()
        if event.button() == QtCore.Qt.RightButton:
            current_daw.cancel_choose_channels()


class Start_window(QtWidgets.QMainWindow):

    def __init__(self, dpi=None):
        super().__init__()
        self.dpi = dpi
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setStyleSheet('background-color: gainsboro;')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumSize(500, 220)
        self.title_label = Label(self,
                                 text='Musicpy Daw',
                                 font=set_font(QtGui.QFont('Consolas', 30),
                                               self.dpi))
        self.title_label.move(120, 80)
        pygame.mixer.quit()
        pygame.mixer.init(current_settings.frequency,
                          current_settings.sound_size,
                          current_settings.channel, current_settings.buffer)
        pygame.mixer.set_num_channels(current_settings.maxinum_channels)
        QtCore.QTimer.singleShot(500, open_main_window)
        self.show()


class Channel_dict_window(QtWidgets.QMainWindow):

    def __init__(self, parent=None, current_ind=0):
        super().__init__()
        self.parent = parent
        self.current_ind = current_ind
        self.current_font = self.parent.current_font
        self.language_dict = self.parent.language_dict
        self.setStyleSheet(self.parent.get_stylesheet())
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setStyleSheet(
            f'background-color: {current_settings.background_color}')
        self.setWindowTitle(self.language_dict['change_channel_dict'][0])
        self.setMinimumSize(500, 300)
        self.activateWindow()
        current_dict = self.parent.channel_dict[current_ind]
        self.parent.current_dict = current_dict
        self.dict_configs = QtWidgets.QListWidget(self)
        self.dict_configs.setFont(self.current_font)
        self.dict_configs.clicked.connect(self.show_current_dict_configs)
        self.dict_configs.setFixedHeight(185)
        self.dict_configs.move(0, 0)
        for i, each in enumerate(current_dict):
            self.dict_configs.insertItem(i, each)
        self.current_note_name = Label(
            self, text=self.language_dict['change_channel_dict'][1])
        self.current_note_name.place(x=200, y=5)
        self.current_note_name_entry = LineEdit(self,
                                                width=70,
                                                x=300,
                                                y=0,
                                                font=self.current_font)
        self.current_note_value = Label(
            self, text=self.language_dict['change_channel_dict'][2])
        self.current_note_value.place(x=200, y=50)
        self.current_note_value_entry = LineEdit(self,
                                                 width=70,
                                                 x=300,
                                                 y=50,
                                                 font=self.current_font)
        self.change_current_note_name_button = Button(
            self,
            text=self.language_dict['change_channel_dict'][3],
            command=self.change_current_note_name)
        self.change_current_note_value_button = Button(
            self,
            text=self.language_dict['change_channel_dict'][4],
            command=self.change_current_note_value)
        self.add_new_note_button = Button(
            self,
            text=self.language_dict['change_channel_dict'][5],
            command=self.add_new_note)
        self.remove_note_button = Button(
            self,
            text=self.language_dict['change_channel_dict'][6],
            command=self.remove_note)
        self.new_note_name_entry = LineEdit(self,
                                            width=70,
                                            x=320,
                                            y=150,
                                            font=self.current_font)
        self.reset_dict_button = Button(
            self,
            text=self.language_dict['change_channel_dict'][9],
            command=self.reset_dict)
        self.change_current_note_name_button.place(x=200, y=100)
        self.change_current_note_value_button.place(x=350, y=100)
        self.add_new_note_button.place(x=200, y=150)
        self.remove_note_button.place(x=200, y=200)
        self.reset_dict_button.place(x=350, y=250)
        self.reload_channel_sounds_button = Button(
            self,
            text=self.language_dict['change_channel_dict'][7],
            command=self.parent.reload_channel_sounds)
        self.reload_channel_sounds_button.place(x=200, y=250)
        self.clear_all_notes_button = Button(
            self,
            text=self.language_dict['change_channel_dict'][8],
            command=self.clear_all_notes)
        self.clear_all_notes_button.place(x=350, y=200)
        self.show()

    def show_current_dict_configs(self):
        current_note = self.dict_configs.currentItem().text()
        if current_note in self.parent.current_dict:
            self.current_note_name_entry.clear()
            self.current_note_name_entry.setText(current_note)
            self.current_note_value_entry.clear()
            self.current_note_value_entry.setText(
                self.parent.current_dict[current_note])

    def change_current_note_name(self):
        current_note = self.dict_configs.currentItem().text()
        current_ind_whole = self.dict_configs.currentIndex()
        current_ind = current_ind_whole.row()
        current_note_name = self.current_note_name_entry.text()
        if current_note_name and current_note_name != current_note:
            current_keys = list(self.parent.current_dict.keys())
            current_keys[current_ind] = current_note_name
            self.parent.current_dict[
                current_note_name] = self.parent.current_dict[current_note]
            del self.parent.current_dict[current_note]
            self.parent.current_dict = {
                i: self.parent.current_dict[i]
                for i in current_keys
            }
            self.parent.channel_dict[
                self.parent.
                current_channel_dict_num] = self.parent.current_dict
            self.dict_configs.clear()
            self.dict_configs.addItems(list(self.parent.current_dict.keys()))
            self.dict_configs.setCurrentRow(current_ind)

    def change_current_note_value(self):
        current_note = self.dict_configs.currentItem().text()
        if not current_note:
            return
        current_note_value_before = self.parent.current_dict[current_note]
        current_note_value = self.current_note_value_entry.text()
        if current_note_value != current_note_value_before:
            self.parent.current_dict[current_note] = current_note_value

    def add_new_note(self):
        current_note_name = self.new_note_name_entry.text()
        if current_note_name and current_note_name not in self.parent.current_dict:
            self.parent.current_dict[current_note_name] = ''
            self.dict_configs.addItem(current_note_name)
            current_ind = len(self.parent.current_dict) - 1
            self.dict_configs.setCurrentRow(current_ind)
            self.show_current_dict_configs()

    def remove_note(self):
        current_note = self.dict_configs.currentItem().text()
        if current_note not in self.parent.current_dict:
            return
        del self.parent.current_dict[current_note]
        current_ind = self.dict_configs.currentIndex().row()
        self.dict_configs.takeItem(current_ind)
        new_ind = min(current_ind, len(self.parent.current_dict) - 1)
        self.dict_configs.setCurrentRow(new_ind)
        self.show_current_dict_configs()

    def clear_all_notes(self):
        self.dict_configs.clear()
        self.parent.current_dict.clear()
        self.current_note_name_entry.clear()
        self.current_note_value_entry.clear()

    def reset_dict(self):
        current_ind = self.current_ind
        self.parent.channel_dict[current_ind] = copy(current_settings.notedict)
        current_dict = self.parent.channel_dict[current_ind]
        self.dict_configs.clear()
        for each in current_dict:
            self.dict_configs.addItem(each)
        self.parent.current_dict = current_dict


class SoundFont_window(QtWidgets.QMainWindow):

    def __init__(self, parent=None, current_soundfont=None):
        super().__init__()
        self.parent = parent
        self.current_font = self.parent.current_font
        self.language_dict = self.parent.language_dict
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setStyleSheet(self.parent.get_stylesheet())
        self.setWindowTitle(self.language_dict['configure_instrument'][0])
        self.setMinimumSize(700, 300)
        self.activateWindow()
        self.preset_configs = QtWidgets.QListWidget(self)
        self.preset_configs.setFixedSize(185, 160)
        self.preset_configs.move(200, 30)
        self.preset_configs.setFont(self.current_font)
        self.preset_configs.clicked.connect(self.show_current_preset_configs)
        self.bank_configs = QtWidgets.QListWidget(self)
        self.bank_configs.setFixedSize(185, 160)
        self.bank_configs.move(0, 30)
        self.bank_configs.setFont(self.current_font)
        self.bank_configs.clicked.connect(self.show_current_bank_configs)
        self.current_all_available_banks = current_soundfont.all_available_banks
        self.current_preset_ind = current_soundfont.current_preset_ind
        self.preset_configs.addItems(current_soundfont.current_preset_name)
        self.bank_configs.addItems(
            [str(i) for i in current_soundfont.all_available_banks])
        self.current_bank = Label(
            self, text=self.language_dict['configure_instrument'][1])
        self.current_bank.place(x=400, y=30)
        self.current_bank_entry = LineEdit(self,
                                           width=70,
                                           font=self.current_font)
        self.current_bank_entry.setText(str(current_soundfont.current_bank))
        self.current_bank_entry.place(x=500, y=30)
        self.current_preset = Label(
            self, text=self.language_dict['configure_instrument'][2])
        self.current_preset.place(x=400, y=80)
        self.current_preset_entry = LineEdit(self,
                                             width=70,
                                             font=self.current_font)
        self.current_preset_entry.setText(
            str(current_soundfont.current_preset + 1))
        self.current_preset_entry.place(x=500, y=80)
        if current_soundfont.current_preset in current_soundfont.current_preset_ind:
            current_preset_ind = current_soundfont.current_preset_ind.index(
                current_soundfont.current_preset)
            self.preset_configs.clearSelection()
            self.preset_configs.setCurrentRow(current_preset_ind)
            self.bank_configs.clearSelection()
            self.bank_configs.setCurrentRow(
                current_soundfont.all_available_banks.index(
                    current_soundfont.current_bank))
        self.change_current_bank_button = Button(
            self,
            text=self.language_dict['configure_instrument'][3],
            command=self.change_current_bank)
        self.change_current_preset_button = Button(
            self,
            text=self.language_dict['configure_instrument'][4],
            command=self.change_current_preset)
        self.listen_preset_button = Button(
            self,
            text=self.language_dict['configure_instrument'][5],
            command=self.listen_preset)
        self.change_current_bank_button.place(x=400, y=130)
        self.change_current_preset_button.place(x=520, y=130)
        self.listen_preset_button.place(x=400, y=180)
        self.preset_label = Label(self, text='Presets')
        self.preset_label.place(x=200, y=0)
        self.bank_label = Label(self, text='Banks')
        self.bank_label.place(x=0, y=0)
        self.show()

    def change_current_bank(self, mode=0):
        current_ind = self.parent.choose_channels.currentIndex().row()
        if mode == 0:
            current_bank = self.current_bank_entry.text()
            if not current_bank.isdigit():
                return
            else:
                current_bank = int(current_bank)
        elif mode == 1:
            current_bank_ind = self.bank_configs.currentRow()
            current_bank = self.current_all_available_banks[current_bank_ind]
        current_soundfont = self.parent.channel_instruments[current_ind]
        if current_bank == current_soundfont.current_bank:
            return
        current_soundfont.change(bank=current_bank, preset=0, correct=False)
        try:
            current_soundfont.current_preset_name, current_soundfont.current_preset_ind = current_soundfont.get_all_instrument_names(
                get_ind=True, mode=1, return_mode=1)
        except:
            current_soundfont.current_preset_name, current_soundfont.current_preset_ind = [], []
        self.current_preset_ind = current_soundfont.current_preset_ind
        self.current_preset_entry.clear()
        self.current_preset_entry.setText(
            '1' if not current_soundfont.current_preset_ind else str(
                current_soundfont.current_preset_ind[0] + 1))
        self.preset_configs.clear()
        self.preset_configs.addItems(current_soundfont.current_preset_name)
        self.preset_configs.clearSelection()
        self.preset_configs.setCurrentRow(0)

    def change_current_preset(self, mode=0):
        current_ind = self.parent.choose_channels.currentIndex().row()
        if mode == 1:
            current_preset = str(
                self.current_preset_ind[self.preset_configs.currentRow()] + 1)
        else:
            current_preset = self.current_preset_entry.text()
        current_soundfont = self.parent.channel_instruments[current_ind]
        if current_preset.isdigit():
            current_preset = int(current_preset)
            current_soundfont.change(preset=current_preset - 1)
            if current_preset - 1 in current_soundfont.current_preset_ind:
                self.preset_configs.clearSelection()
                current_preset_ind = current_soundfont.current_preset_ind.index(
                    current_preset - 1)
                self.preset_configs.setCurrentRow(current_preset_ind)

    def listen_preset(self):
        current_ind = self.parent.choose_channels.currentIndex().row()
        current_soundfont = self.parent.channel_instruments[current_ind]
        current_soundfont.play_note('C5')

    def show_current_preset_configs(self):
        current_ind = self.preset_configs.currentIndex().row()
        self.current_preset_entry.clear()
        self.current_preset_entry.setText(
            str(self.current_preset_ind[current_ind] + 1))
        self.change_current_preset(1)

    def show_current_bank_configs(self):
        current_ind = self.bank_configs.currentIndex().row()
        current_bank = self.current_all_available_banks[current_ind]
        self.current_bank_entry.clear()
        self.current_bank_entry.setText(str(current_bank))
        self.change_current_bank(mode=1)


class Ask_save_window(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.current_font = self.parent.current_font
        self.language_dict = self.parent.language_dict
        self.setStyleSheet(self.parent.get_stylesheet())
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setMinimumSize(400, 150)
        self.ask_save_label = Label(self,
                                    text=self.language_dict['ask save'][0])
        self.ask_save_label.place(x=0, y=30)
        self.save_button = Button(self,
                                  text=self.language_dict['ask save'][1],
                                  command=self.parent.save_and_quit)
        self.not_save_button = Button(self,
                                      text=self.language_dict['ask save'][2],
                                      command=self.close_all)
        self.cancel_button = Button(self,
                                    text=self.language_dict['ask save'][3],
                                    command=self.close)
        self.save_button.place(x=0, y=100)
        self.not_save_button.place(x=90, y=100)
        self.cancel_button.place(x=200, y=100)
        self.activateWindow()
        self.show()

    def close_all(self):
        self.close()
        self.parent.close()
        os._exit(0)


class Ask_other_format_window(QtWidgets.QMainWindow):

    def __init__(self, parent=None, mode=0):
        super().__init__()
        self.parent = parent
        self.current_font = self.parent.current_font
        self.language_dict = self.parent.language_dict
        self.setStyleSheet(self.parent.get_stylesheet())
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setMinimumSize(470, 200)
        self.setWindowTitle(self.language_dict['ask other format'][0])
        self.ask_other_format_label = Label(
            self, text=self.language_dict['ask other format'][1])
        self.ask_other_format_label.place(x=0, y=50)
        self.ask_other_format_entry = LineEdit(self,
                                               width=140,
                                               font=self.current_font)
        self.ask_other_format_entry.place(x=100, y=100)
        self.ask_other_format_ok_button = Button(
            self,
            text=self.language_dict['ask other format'][2],
            command=self.read_other_format
            if mode == 0 else self.pitch_shifter_read_other_format)
        self.ask_other_format_cancel_button = Button(
            self,
            text=self.language_dict['ask other format'][3],
            command=self.close)
        self.ask_other_format_ok_button.place(x=60, y=150)
        self.ask_other_format_cancel_button.place(x=200, y=150)
        self.show()

    def read_other_format(self):
        current_format = self.ask_other_format_entry.text()
        self.close()
        if current_format:
            self.parent.export_audio_file(mode=current_format)

    def pitch_shifter_read_other_format(self):
        current_format = self.ask_other_format_entry.text()
        self.close()
        if current_format:
            self.parent.pitch_shifter_window.export_pitch_audio_file(
                mode=current_format)


class Debug_window(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.current_font = self.parent.current_font
        self.language_dict = self.parent.language_dict
        self.setStyleSheet(self.parent.get_stylesheet())
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setWindowTitle(self.language_dict['debug window'])
        self.setMinimumSize(700, 400)
        self.activateWindow()
        self.output_text = QtWidgets.QPlainTextEdit(self)
        self.output_text.setFont(self.current_font)
        self.output_text.setFixedSize(612, 285)
        self.output_text.move(20, 20)
        self.clear_text_button = Button(self,
                                        text=self.language_dict['debug clear'],
                                        command=self.output_text.clear)
        self.clear_text_button.place(x=600, y=350)
        self.show()


class Pitch_shifter_window(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.current_font = self.parent.current_font
        self.language_dict = self.parent.language_dict
        self.setStyleSheet(self.parent.get_stylesheet())
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setWindowTitle(self.language_dict['pitch shifter'][0])
        self.setMinimumSize(700, 400)
        self.activateWindow()

        self.import_current_pitch_label = Label(
            self, text=self.language_dict['pitch shifter'][1])
        self.import_current_pitch_label.place(x=0, y=50)
        self.import_current_pitch_button = Button(
            self,
            text=self.language_dict['pitch shifter'][2],
            command=self.pitch_shifter_import_pitch)
        self.import_current_pitch_button.place(x=0, y=100)
        self.msg = Label(self, text=self.language_dict['pitch shifter'][3])
        self.msg.place(x=0, y=350)

        self.default_pitch_entry = LineEdit(self,
                                            width=70,
                                            font=self.current_font)
        self.default_pitch_entry.setText('C5')
        self.default_pitch_entry.place(x=160, y=150)
        self.change_default_pitch_button = Button(
            self,
            text=self.language_dict['pitch shifter'][4],
            command=self.pitch_shifter_change_default_pitch)
        self.change_default_pitch_button.place(x=0, y=150)
        self.change_pitch_button = Button(
            self,
            text=self.language_dict['pitch shifter'][5],
            command=self.pitch_shifter_change_pitch)
        self.change_pitch_button.place(x=0, y=200)
        self.pitch_entry = LineEdit(self, width=70, font=self.current_font)
        self.pitch_entry.setText('C5')
        self.pitch_entry.place(x=160, y=200)
        self.has_load = False

        self.play_button = Button(self,
                                  text=self.language_dict['pitch shifter'][6],
                                  command=self.pitch_shifter_play)
        self.stop_button = Button(self,
                                  text=self.language_dict['pitch shifter'][7],
                                  command=self.pitch_shifter_stop)
        self.play_button.place(x=250, y=150)
        self.stop_button.place(x=350, y=150)
        self.shifted_play_button = Button(
            self,
            text=self.language_dict['pitch shifter'][6],
            command=self.pitch_shifter_play_shifted)
        self.shifted_stop_button = Button(
            self,
            text=self.language_dict['pitch shifter'][7],
            command=self.pitch_shifter_stop_shifted)
        self.shifted_play_button.place(x=250, y=200)
        self.shifted_stop_button.place(x=350, y=200)
        self.pitch_shifter_playing = False
        self.pitch_shifter_shifted_playing = False
        self.current_pitch_note = N('C5')

        self.shifted_export_button = Button(
            self,
            text=self.language_dict['export'],
            command=self.pitch_shifter_export_shifted)
        self.shifted_export_button.place(x=450, y=200)
        self.export_sound_files_button = Button(
            self,
            text=self.language_dict['pitch shifter'][8],
            command=self.pitch_shifter_export_sound_files)
        self.export_sound_files_button.place(x=0, y=250)

        self.export_sound_files_from = LineEdit(self,
                                                width=70,
                                                font=self.current_font)
        self.export_sound_files_to = LineEdit(self,
                                              width=70,
                                              font=self.current_font)
        self.export_sound_files_from.setText('A0')
        self.export_sound_files_to.setText('C8')
        self.export_sound_files_from.place(x=230, y=250)
        self.export_sound_files_to.place(x=345, y=250)
        self.export_sound_files_label = Label(
            self, text=self.language_dict['pitch shifter'][9])
        self.export_sound_files_label.place(x=315, y=255)

        self.change_folder_name_button = Button(
            self,
            text=self.language_dict['pitch shifter'][10],
            command=self.pitch_shifter_change_folder_name)
        self.change_folder_name_button.place(x=0, y=300)
        self.folder_name = LineEdit(self, width=210, font=self.current_font)
        self.folder_name.setText(self.language_dict['Untitled'])
        self.folder_name.place(x=280, y=300)
        self.pitch_shifter_folder_name = self.language_dict['Untitled']
        self.show()

    def show_msg(self, text=''):
        self.msg.setText(text)
        self.msg.adjustSize()
        self.msg.repaint()
        app.processEvents()

    def pitch_shifter_change_folder_name(self):
        self.pitch_shifter_folder_name = self.folder_name.text()
        self.show_msg(
            f'{self.language_dict["msg"][38]}{self.pitch_shifter_folder_name}')

    def pitch_shifter_export_sound_files(self):
        if not self.has_load:
            self.show_msg(self.language_dict["msg"][39])
            return
        try:
            start = N(self.export_sound_files_from.text())
            end = N(self.export_sound_files_to.text())
        except:
            self.show_msg(self.language_dict["msg"][40])
            return
        file_path = Dialog(caption=self.language_dict['title'][2],
                           directory=self.parent.last_path,
                           mode=1).directory
        if not file_path:
            return
        self.parent.update_last_path(file_path)
        self.current_pitch.export_sound_files(file_path,
                                              self.pitch_shifter_folder_name,
                                              start,
                                              end,
                                              pitch_shifter=True)
        current_path = f'{file_path}/{self.pitch_shifter_folder_name}'
        self.show_msg(f'{self.language_dict["msg"][24]}{current_path}')

    def pitch_shifter_play(self):
        if self.has_load:
            if self.pitch_shifter_playing:
                self.pitch_shifter_stop()
            play_audio(self.current_pitch)
            self.pitch_shifter_playing = True

    def pitch_shifter_stop(self):
        if self.pitch_shifter_playing:
            pygame.mixer.stop()
            self.pitch_shifter_playing = False

    def pitch_shifter_play_shifted(self):
        if self.has_load:
            if self.pitch_shifter_shifted_playing:
                self.pitch_shifter_stop_shifted()
            play_audio(self.new_pitch)
            self.pitch_shifter_shifted_playing = True

    def pitch_shifter_stop_shifted(self):
        if self.pitch_shifter_shifted_playing:
            pygame.mixer.stop()
            self.pitch_shifter_shifted_playing = False

    def pitch_shifter_export_shifted(self):
        export_audio_file_menubar = self.parent.get_menu(actions=[
            self.parent.get_action(
                text=self.language_dict['export audio formats'][0],
                command=lambda: self.export_pitch_audio_file(mode='wav')),
            self.parent.get_action(
                text=self.language_dict['export audio formats'][1],
                command=lambda: self.export_pitch_audio_file(mode='mp3')),
            self.parent.get_action(
                text=self.language_dict['export audio formats'][2],
                command=lambda: self.export_pitch_audio_file(mode='ogg')),
            self.parent.get_action(
                text=self.language_dict['export audio formats'][3],
                command=lambda: self.export_pitch_audio_file(mode='other'))
        ])
        export_audio_file_menubar.popup(QtGui.QCursor().pos())

    def export_pitch_audio_file(self, mode='wav'):
        if not self.has_load:
            self.show_msg(self.language_dict["msg"][39])
            return
        if mode == 'other':
            self.parent.ask_other_format(mode=1)
            return
        filename = Dialog(
            caption=self.language_dict['title'][3],
            directory=self.parent.last_path,
            filter=f"{self.language_dict['title'][1]} (*)",
            default_filename=f"{self.language_dict['untitled']}.{mode}",
            mode=2).filename[0]
        if not filename:
            return
        self.parent.update_last_path(filename)
        self.show_msg(self.language_dict["msg"][41])
        try:
            self.new_pitch.export(filename, format=mode)
            self.show_msg(f'{self.language_dict["msg"][24]}{filename}')
        except:
            self.show_msg(
                f'{self.language_dict["error"]}{mode}{self.language_dict["msg"][23]}'
            )

    def pitch_shifter_import_pitch(self):
        file_path = Dialog(
            caption=self.language_dict['title'][0],
            directory=self.parent.last_path,
            filter=f"{self.language_dict['title'][1]} (*)").filename[0]
        if file_path:
            self.parent.update_last_path(file_path)
            self.show_msg(self.language_dict["msg"][42])
            try:
                default_pitch = self.default_pitch_entry.text()
            except:
                default_pitch = 'C5'
            try:
                self.current_pitch = pitch(file_path, default_pitch)
            except:
                self.show_msg(
                    f'{self.language_dict["error"][:-1]}{self.language_dict["msg"][23]}'
                )
                return
            self.import_current_pitch_label.configure(
                text=f'{self.language_dict["pitch shifter"][1]}{file_path}')
            self.show_msg(self.language_dict["msg"][1])
            self.has_load = True
            self.new_pitch = self.current_pitch.sounds

    def pitch_shifter_change_default_pitch(self):
        if self.has_load:
            new_pitch = self.default_pitch_entry.text()
            try:
                self.current_pitch.set_note(new_pitch)
                self.show_msg(f'{self.language_dict["msg"][43]}{new_pitch}')
            except:
                self.show_msg(self.language_dict["msg"][37])

    def pitch_shifter_change_pitch(self):
        if not self.has_load:
            return

        try:
            new_pitch = N(self.pitch_entry.text())
            current_msg = self.language_dict["msg"][44].split('|')
            self.show_msg(f'{current_msg[0]}{new_pitch}{current_msg[1]}')
            self.new_pitch = self.current_pitch + (
                new_pitch.degree - self.current_pitch.note.degree)
            self.show_msg(f'{self.language_dict["msg"][45]}{new_pitch}')
        except Exception as e:
            output(traceback.format_exc())
            self.show_msg(self.language_dict["msg"][40])


class Mixer_window(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.current_font = self.parent.current_font
        self.language_dict = self.parent.language_dict
        self.setStyleSheet(self.parent.get_stylesheet())
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setWindowTitle(self.language_dict['mixer'][0])
        self.setMinimumSize(700, 400)
        self.activateWindow()

        self.import_effect_button = Button(self,
                                           text=self.language_dict['mixer'][1],
                                           command=self.import_effect,
                                           x=20,
                                           y=20)

        self.save_effect_button = Button(self,
                                         text=self.language_dict['mixer'][11],
                                         command=self.save_effect_parameters,
                                         x=170,
                                         y=20)

        self.replace_effect_button = Button(
            self,
            text=self.language_dict['mixer'][12],
            command=self.replace_effect,
            x=320,
            y=20)

        self.change_parameter_value_button = Button(
            self,
            text=self.language_dict['mixer'][3],
            command=self.change_parameter_value,
            x=470,
            y=20)

        self.remove_effect_button = Button(self,
                                           text=self.language_dict['mixer'][5],
                                           command=self.remove_effect,
                                           x=470,
                                           y=200)

        self.check_enable_label = Label(self,
                                        text=self.language_dict['mixer'][6],
                                        x=600,
                                        y=100)
        self.check_enable_button = CheckBox(self,
                                            value=False,
                                            command=self.change_enabled,
                                            x=650,
                                            y=100)

        self.current_channel_window = QtWidgets.QListWidget(self)
        self.current_channel_window.setFont(self.current_font)
        self.current_channel_window.clicked.connect(self.show_current_channel)
        self.current_channel_window.setFixedSize(120, 150)
        self.current_channel_window.move(20, 100)
        self.current_channel_label = Label(
            self, text=self.language_dict['mixer'][10], x=20, y=70)
        self.current_channel_window.addItem('Master')
        self.current_channel_window.addItems(self.parent.channel_names)

        self.current_effect_window = QtWidgets.QListWidget(self)
        self.current_effect_window.setFont(self.current_font)
        self.current_effect_window.clicked.connect(self.show_current_effect)
        self.current_effect_window.setFixedSize(120, 150)
        self.current_effect_window.move(170, 100)
        self.current_effect_label = Label(self,
                                          text=self.language_dict['mixer'][7],
                                          x=170,
                                          y=70)

        self.current_effect_parameters_window = QtWidgets.QListWidget(self)
        self.current_effect_parameters_window.setFont(self.current_font)
        self.current_effect_parameters_window.clicked.connect(
            self.show_current_effect_parameters)
        self.current_effect_parameters_window.setFixedSize(120, 150)
        self.current_effect_parameters_window.move(320, 100)
        self.current_effect_parameters_label = Label(
            self, text=self.language_dict['mixer'][8], x=320, y=70)

        self.current_effect_parameter_entry = LineEdit(self,
                                                       width=100,
                                                       x=470,
                                                       y=100,
                                                       font=self.current_font)
        self.current_effect_parameter_label = Label(
            self, text=self.language_dict['mixer'][9], x=470, y=70)

        self.show()

    def import_effect(self):
        current_ind = self.current_channel_window.currentRow()
        if current_ind < 0:
            return
        filename = Dialog(
            caption=self.language_dict['mixer'][1],
            directory=self.parent.last_path,
            filter=
            f'python (*.py);;Musicpy Daw parameters (*.mdparam);;{self.language_dict["title"][1]} (*)'
        ).filename[0]
        if filename:
            self.parent.update_last_path(filename)
            try:
                if os.path.splitext(filename)[1][1:].lower() == 'mdparam':
                    with open(filename, encoding='utf-8') as f:
                        data = json.load(f)
                    file_path = data['file_path']
                    current_effect = importfile(file_path).Synth()
                    current_effect.file_path = file_path
                    current_effect.instrument_parameters.update(
                        data['python instrument parameters']
                        ['instrument_parameters'])
                    current_effect.effect_parameters.update(
                        data['python instrument parameters']
                        ['effect_parameters'])
                    current_effect.enabled = data[
                        'python instrument parameters']['enabled']
                else:
                    current_effect = importfile(filename).Synth()
                    current_effect.file_path = filename
                self.current_effect_window.addItem(current_effect.name)
                if current_ind == 0:
                    self.parent.master_effects.append(current_effect)
                else:
                    self.parent.channel_effects[current_ind -
                                                1].append(current_effect)
            except:
                self.parent.show_msg(self.language_dict["mixer"][2])
                output(traceback.format_exc())

    def show_current_channel(self):
        current_ind = self.current_channel_window.currentRow()
        if current_ind == 0:
            current_effects = self.parent.master_effects
        else:
            current_effects = self.parent.channel_effects[current_ind - 1]
        self.current_effect_parameters_window.clear()
        self.current_effect_parameter_entry.clear()
        self.check_enable_button.setChecked(False)
        self.current_effect_window.clear()
        self.current_effect_window.addItems([i.name for i in current_effects])

    def show_current_effect(self):
        current_ind = self.current_channel_window.currentRow()
        if current_ind < 0:
            return
        current_effect_ind = self.current_effect_window.currentRow()
        if current_ind == 0:
            current_effects = self.parent.master_effects
        else:
            current_effects = self.parent.channel_effects[current_ind - 1]
        current_effect = current_effects[current_effect_ind]
        self.current_effect_parameters_window.clear()
        self.current_effect_parameters_window.addItems(
            list(current_effect.effect_parameters.keys()))
        self.current_effect_parameter_entry.clear()
        self.check_enable_button.setChecked(current_effect.enabled)

    def show_current_effect_parameters(self):
        current_ind = self.current_channel_window.currentRow()
        if current_ind < 0:
            return
        current_effect_parameter = self.current_effect_parameters_window.currentItem(
        ).text()
        current_effect_ind = self.current_effect_window.currentRow()
        if current_ind == 0:
            current_effects = self.parent.master_effects
        else:
            current_effects = self.parent.channel_effects[current_ind - 1]
        current_effect = current_effects[current_effect_ind]
        current_effect_parameter_value = current_effect.effect_parameters[
            current_effect_parameter]
        self.current_effect_parameter_entry.clear()
        self.current_effect_parameter_entry.setText(
            str(current_effect_parameter_value))

    def change_parameter_value(self):
        current_ind = self.current_channel_window.currentRow()
        if current_ind < 0:
            return
        try:
            current_value = get_value(
                self.current_effect_parameter_entry.text())
        except:
            self.parent.show_msg(self.language_dict["mixer"][2])
            return
        current_effect_ind = self.current_effect_window.currentRow()
        if current_effect_ind >= 0:
            current_parameter_name = self.current_effect_parameters_window.currentItem(
            )
            if current_parameter_name is not None:
                current_effect_parameter = current_parameter_name.text()
                if current_ind == 0:
                    current_effects = self.parent.master_effects
                else:
                    current_effects = self.parent.channel_effects[current_ind -
                                                                  1]
                current_effect = current_effects[current_effect_ind]
                current_effect.effect_parameters[
                    current_effect_parameter] = current_value

    def remove_effect(self):
        current_ind = self.current_channel_window.currentRow()
        if current_ind < 0:
            return
        current_effect_ind = self.current_effect_window.currentRow()
        if current_effect_ind >= 0:
            if current_ind == 0:
                current_effects = self.parent.master_effects
            else:
                current_effects = self.parent.channel_effects[current_ind - 1]
            del current_effects[current_effect_ind]
            self.current_effect_window.takeItem(current_effect_ind)
            self.current_effect_parameters_window.clear()
            self.current_effect_parameter_entry.clear()
            self.check_enable_button.setChecked(False)

    def change_enabled(self):
        current_ind = self.current_channel_window.currentRow()
        if current_ind < 0:
            return
        current_effect_ind = self.current_effect_window.currentRow()
        if current_effect_ind >= 0:
            if current_ind == 0:
                current_effects = self.parent.master_effects
            else:
                current_effects = self.parent.channel_effects[current_ind - 1]
            current_effect = current_effects[current_effect_ind]
            current_effect.enabled = self.check_enable_button.isChecked()

    def save_effect_parameters(self):
        current_ind = self.current_channel_window.currentRow()
        if current_ind < 0:
            return
        current_effect_ind = self.current_effect_window.currentRow()
        if current_effect_ind < 0:
            return
        if current_ind == 0:
            current_effects = self.parent.master_effects
        else:
            current_effects = self.parent.channel_effects[current_ind - 1]
        current_effect = current_effects[current_effect_ind]
        filename = Dialog(
            caption=self.language_dict['file'][8],
            directory=self.parent.last_path,
            filter=
            f"Musicpy Daw Parameters (*.mdparam);; {self.language_dict['title'][1]} (*)",
            default_filename=f"{self.language_dict['untitled']}.mdparam",
            mode=2).filename[0]
        if filename:
            current_effect_name = current_effect.file_path
            parameter_dict = {}
            parameter_dict['file_path'] = current_effect_name
            parameter_dict['type'] = 'effect'
            parameter_dict['python instrument parameters'] = {
                'instrument_parameters': current_effect.instrument_parameters,
                'effect_parameters': current_effect.effect_parameters,
                'enabled': current_effect.enabled
            }
            self.parent.update_last_path(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(parameter_dict,
                          f,
                          indent=4,
                          separators=(',', ': '),
                          ensure_ascii=False)

    def replace_effect(self):
        current_ind = self.current_channel_window.currentRow()
        if current_ind < 0:
            return
        current_effect_ind = self.current_effect_window.currentRow()
        if current_effect_ind < 0:
            return
        if current_ind == 0:
            current_effects = self.parent.master_effects
        else:
            current_effects = self.parent.channel_effects[current_ind - 1]
        filename = Dialog(
            caption=self.language_dict['mixer'][1],
            directory=self.parent.last_path,
            filter=
            f'python (*.py);;Musicpy Daw parameters (*.mdparam);;{self.language_dict["title"][1]} (*)'
        ).filename[0]
        if filename:
            self.parent.update_last_path(filename)
            try:
                if os.path.splitext(filename)[1][1:].lower() == 'mdparam':
                    with open(filename, encoding='utf-8') as f:
                        data = json.load(f)
                    file_path = data['file_path']
                    current_effect = importfile(file_path).Synth()
                    current_effect.file_path = file_path
                    current_effect.instrument_parameters.update(
                        data['python instrument parameters']
                        ['instrument_parameters'])
                    current_effect.effect_parameters.update(
                        data['python instrument parameters']
                        ['effect_parameters'])
                    current_effect.enabled = data[
                        'python instrument parameters']['enabled']
                else:
                    current_effect = importfile(filename).Synth()
                    current_effect.file_path = filename
                self.current_effect_window.currentItem().setText(
                    current_effect.name)
                self.current_effect_parameters_window.clear()
                self.current_effect_parameter_entry.clear()
                self.check_enable_button.setChecked(False)
                current_effects[current_effect_ind] = current_effect
            except:
                self.parent.show_msg(self.language_dict["mixer"][2])
                output(traceback.format_exc())


class Python_instrument_window(QtWidgets.QMainWindow):

    def __init__(self, parent=None, current_ind=0):
        super().__init__()
        self.parent = parent
        self.current_ind = current_ind
        self.current_font = self.parent.current_font
        self.language_dict = self.parent.language_dict
        self.setStyleSheet(self.parent.get_stylesheet())
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setWindowTitle(self.language_dict['python instrument'][0])
        self.setMinimumSize(500, 300)
        self.current_instrument = self.parent.channel_instruments[
            self.current_ind]

        self.current_instrument_parameters_window = QtWidgets.QListWidget(self)
        self.current_instrument_parameters_window.setFont(self.current_font)
        self.current_instrument_parameters_window.clicked.connect(
            self.show_current_instrument_parameters)
        self.current_instrument_parameters_window.setFixedSize(120, 150)
        self.current_instrument_parameters_window.move(20, 100)
        self.current_instrument_parameters_window.addItems(
            list(self.current_instrument.instrument_parameters.keys()))
        self.current_instrument_label = Label(
            self, text=self.language_dict['mixer'][8], x=20, y=70)

        self.current_instrument_parameter_entry = LineEdit(
            self, width=100, x=170, y=100, font=self.current_font)
        self.current_instrument_label = Label(
            self, text=self.language_dict['mixer'][9], x=170, y=70)

        self.change_parameter_value_button = Button(
            self,
            text=self.language_dict['mixer'][3],
            command=self.change_parameter_value,
            x=20,
            y=20)

        self.activateWindow()
        self.show()

    def show_current_instrument_parameters(self):
        current_instrument_parameter = self.current_instrument_parameters_window.currentItem(
        ).text()
        current_instrument_parameter_value = self.current_instrument.instrument_parameters[
            current_instrument_parameter]
        self.current_instrument_parameter_entry.clear()
        self.current_instrument_parameter_entry.setText(
            str(current_instrument_parameter_value))

    def change_parameter_value(self):
        try:
            current_value = get_value(
                self.current_instrument_parameter_entry.text())
        except:
            self.parent.show_msg(self.language_dict["mixer"][2])
            return
        current_parameter_name = self.current_instrument_parameters_window.currentItem(
        )
        if current_parameter_name is not None:
            current_instrument_parameter = current_parameter_name.text()
            self.current_instrument.instrument_parameters[
                current_instrument_parameter] = current_value


def set_font(font, dpi):
    if dpi != 96.0:
        font.setPointSize(int(font.pointSize() * (96.0 / dpi)))
    return font


def open_main_window():
    current_start_window.close()
    global current_daw
    current_file = None
    argv = sys.argv
    if len(argv) > 1:
        current_file = argv[1]
    current_daw = Daw(file=current_file, dpi=dpi)


def play_audio(audio, mode=0):
    if isinstance(audio, (pitch, sound)):
        current_audio = audio.sounds
    else:
        current_audio = audio
    if mode == 0:
        if current_audio.frame_rate != current_settings.frequency:
            current_audio = current_audio.set_frame_rate(
                current_settings.frequency)
        if current_audio.channels == 1:
            current_audio = current_audio.set_channels(2)
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


def load_audiosegments(current_dict, current_sound_path, current_queue=None):
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
                        current_settings.frequency).set_channels(
                            2).set_sample_width(2)
            except:
                with open(current_sound_obj_path, 'rb') as f:
                    current_data = f.read()
                current_sounds[i] = AudioSegment.from_file(
                    BytesIO(current_data),
                    format=current_sound_format).set_frame_rate(
                        current_settings.frequency).set_channels(
                            2).set_sample_width(2)
        else:
            current_sounds[i] = None
    if current_queue:
        current_queue.put(current_sounds)
    return current_sounds


def standardize_note(i):
    if i in database.standard_dict:
        i = database.standard_dict[i]
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


def all_has_audio(sound):
    if isinstance(sound, chord):
        return all(isinstance(i, AudioSegment) for i in sound.notes)
    elif isinstance(sound, piece):
        return all(all_has_audio(i) for i in sound.tracks)


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
                    current_daw.bar_to_real_time(current_note.duration, bpm,
                                                 1), volume[i])
            elif mode == 'triangle':
                temp[i] = triangle(
                    get_freq(current_note),
                    current_daw.bar_to_real_time(current_note.duration, bpm,
                                                 1), volume[i])
            elif mode == 'sawtooth':
                temp[i] = sawtooth(
                    get_freq(current_note),
                    current_daw.bar_to_real_time(current_note.duration, bpm,
                                                 1), volume[i])
            elif mode == 'square':
                temp[i] = square(
                    get_freq(current_note),
                    current_daw.bar_to_real_time(current_note.duration, bpm,
                                                 1), volume[i])
            else:
                temp[i] = mode(
                    get_freq(current_note),
                    current_daw.bar_to_real_time(current_note.duration, bpm,
                                                 1), volume[i])
    return temp


def audio(obj, channel_num=0):
    if isinstance(obj, note):
        obj = chord([obj])
    elif isinstance(obj, track):
        obj = build(obj, bpm=obj.bpm, name=obj.name)
    result = current_daw.export_audio_file(obj,
                                           action='get',
                                           channel_num=channel_num)
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
    if bpm is not None and isinstance(bpm, (int, float)):
        if isinstance(bpm, float) and bpm.is_integer():
            bpm = int(bpm)
        current_daw.change_current_bpm_entry.clear()
        current_daw.change_current_bpm_entry.setText(bpm)
        current_daw.change_current_bpm(1)
    current_daw.play_musicpy_sounds(current_chord,
                                    bpm,
                                    channel,
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
    if bpm is not None and isinstance(bpm, (int, float)):
        if isinstance(bpm, float) and bpm.is_integer():
            bpm = int(bpm)
        current_daw.change_current_bpm_entry.clear()
        current_daw.change_current_bpm_entry.setText(bpm)
        current_daw.change_current_bpm(1)
    if mode == 'mid' or mode == 'midi':
        current_daw.export_midi_file(current_chord, **write_args)
    else:
        current_daw.export_audio_file(obj=current_chord,
                                      mode=mode,
                                      action=action,
                                      channel_num=channel,
                                      length=length,
                                      extra_length=extra_length,
                                      track_lengths=track_lengths,
                                      track_extra_lengths=track_extra_lengths,
                                      export_args=export_args,
                                      soundfont_args=soundfont_args)


def output(*obj):
    result = ' '.join([str(i) for i in obj]) + '\n'
    if current_daw.debug_window is not None and current_daw.debug_window.isVisible(
    ):
        current_daw.debug_window.output_text.insertPlainText(result)
        current_daw.debug_window.activateWindow()
        current_daw.debug_window.raise_()


def get_value(value):
    try:
        result = literal_eval(value)
    except:
        try:
            result = float(fractions.Fraction(value))
        except:
            result = value
    return result


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

if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    dpi = (app.screens()[0]).logicalDotsPerInch()
    current_start_window = Start_window(dpi=dpi)
    app.exec()
