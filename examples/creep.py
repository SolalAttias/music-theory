from music_theory import Chord, Key

if __name__ == "__main__":
    # Creep
    creep_chords = [Chord.from_chord_notation(notation) for notation in ("G", "B", "C", "Cm")]
    print(f"Analysing Creep, which has chords: {[chord.to_notation() for chord in creep_chords]}")
    key = Key("G")
    print(f"And is in key: {key.key_notation}")
    for chord in creep_chords:
        print(f"{chord.to_notation()}: {key.get_numeral_from_chord(chord)}")

    for chord in creep_chords:
        if key.contains_chord(chord):
            print(f"{chord.to_notation()} is in {key.key_notation} key")
        else:
            print(f"{chord.to_notation()} is not strictly speaking in {key.key_notation} key")
