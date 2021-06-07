from musicpy import *
import random

'''
def write_jpop(scale_type, length, melody_ins=1, chord_ins=1, bpm=80):
    if 'minor' in scale_type.mode:
        scale_type = scale_type.relative_key()
    choose_chord_progressions_list = ['6451', '3456', '4536', '14561451']
    choose_chord_progressions = random.choice(choose_chord_progressions_list)
    choose_chords = scale_type % (choose_chord_progressions, 1 / 8, 1 / 8, 4)
    chord_num = len(choose_chords)
    length_count = 0
    chord_ind = 0
    melody_notes_list = [random.choice(choose_chords[0].notes).up(octave)]
    melody_intervals = [random.choice([1 / 8, 1 / 16])]
    melody = chord(melody_notes_list, interval=melody_intervals)
    chords_part = None
    while length_count < length:
        current_chord = choose_chords[chord_ind]
        chord_ind += 1
        if chord_ind >= chord_num:
            chord_ind = 0
        if chords_part is None:
            chords_part = current_chord
        else:
            chords_part |= current_chord
        length_count = chords_part.bars()
        while melody.bars() < length_count:
            current_melody = random.choice(current_chord.notes).up(octave)
            current_melody.duration = random.choice([1 / 8, 1 / 16])
            melody.notes.append(current_melody)
            melody.interval.append(copy(current_melody.duration))

    result = piece([melody, chords_part], [melody_ins, chord_ins],
                   bpm, [0, 0],
                   track_names=['melody', 'chords'])
    return result


#a = read("G:/fl studio files/aaa/mp3和midi文件/midi文件/Pianoteq 6 (64-bit).mid", mode='all', to_piece=True, get_off_drums=True)
#a.clear_pitch_bend(value=0)
#play(a.merge()[1], a.tempo)
#play(a.merge()[1], a.tempo)
#b = read("G:/fl studio files/aaa/mp3和midi文件/midi文件/2021.1.28.mid", mode='all', to_piece=True, get_off_drums=False)
#play(a + b)
#a.normalize_tempo()
#play(a)

#a = read("G:/fl studio files/aaa/mp3和midi文件/midi文件/命运交响曲原版.mid", mode='all', to_piece=True, get_off_drums=False)
#play(a.cut(98))
#a = read("G:/fl studio files/aaa/mp3和midi文件/others/东方全曲midi/touhoumidi/pic051_东方靈異伝/th1_14.mid", get_off_drums=False, mode='all', to_piece=True, split_channels=True)
#q = a.merge()[1].cut(1, 41)
#print(q.detect_scale())

#a = read("temp.mid", mode='all', to_piece=True, get_off_drums=False)
#a.normalize_tempo()
#play(a)

#bpm, q, start_time = a
#q.normalize_tempo(bpm, start_time=start_time)
#play(q, bpm, start_time=start_time, deinterleave=False)
#q = a.tracks[0]
#for each in tempo_changes: each.start_time -= 0.625
#q += tempo_changes
#q.normalize_tempo(a.tempo, start_time=a.start_times[0])
#play(q, a.tempo, start_time=a.start_times[0])

#bpm, a, start_time = new_midi_file
#a.normalize_tempo(154, start_time=start_time)
#play(a, 154, deinterleave=False)
#q += new_midi_file.get_tempo_changes()
#w = q.normalize_tempo(new_midi_file.tempo, start_time=new_midi_file.start_times[7], return_tempo_changes=True)
#play(q, new_midi_file.tempo)
#os.chdir("G:/fl studio files/aaa/mp3和midi文件/midi文件/")
#a = read('2018.9.17欢快阳光小道.mid', mode='all', to_piece=True, get_off_drums=False)
#play(a)
#b = track(C('Cmaj7'), 47, 150, name='123')
#new_midi_file = read("G:/fl studio files/aaa/mp3和midi文件/midi文件/prelude in C major.mid", mode='all', to_piece=True, get_off_drums=False)
#q = new_midi_file.tracks[0]
#w = q.pitch_inversion().retrograde().pitch_inversion()
#a = read("Someone_like_You.mscz.mid", mode='all', to_piece=True, get_off_drums=False)
#w = a.merge()[1]
#print(chord_analysis(w, mode='bars start'))
'''
#(P([(drum('0,1,2,1,0,0,2,1,{4},!1/16;1/16')).notes, chord('B1,F#2')%(1/16,1/16)%4 | chord('G1,D2')%(1/16,1/16)%4 | chord('A1,E2')%(1/16,1/16)%4 | chord('D2,A2')%(1/16,1/16)%4],[1,34],80,[0,0],channels=[9,1])).play()
q = read("G:/fl studio files/aaa/mp3和midi文件/midi文件/星雨.mid", mode="all", get_off_drums=False, merge=True)[1]