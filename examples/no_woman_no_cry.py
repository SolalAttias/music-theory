from music_theory import Chord, find_keys

if __name__ == "__main__":
    # No Woman No Cry
    nwnc_chords = [Chord.from_chord_notation(notation) for notation in ("C", "G", "Am", "F")]
    print(
        "Analysing No Woman No Cry, which has chords: "
        f"{[chord.to_notation() for chord in nwnc_chords]}"
    )
    keys = find_keys(nwnc_chords)
    print(f"These are the possible keys {[key.key_notation for key in keys]}")
    # Should be C key
    key = keys[0]
    print(f"Selected the key {key.key_notation}")
    # I-V-vi-IV classic pop song chord progression
    for chord in nwnc_chords:
        print(f"{chord.to_notation()}: {key.get_numeral_from_chord(chord)}")
