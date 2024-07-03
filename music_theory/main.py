from enum import Enum
from typing import Generator

ROMAN_NUMERALS = ["i", "ii", "iii", "iv", "v", "vi", "vii"]
NOTES = [
    "C",
    "D♭",
    "D",
    "E♭",
    "E",
    "F",
    "G♭",
    "G",
    "A♭",
    "A",
    "B♭",
    "B",
]
NB_NOTES = len(NOTES)


class MODES(Enum):
    MAJOR = "major"
    MINOR = "minor"


MINOR_THIRD_INTERVAL = 3
MAJOR_THIRD_INTERVAL = 4
PERFECT_FIFTH_INTERVAL = 7

# class MusicTheoryError(BaseException):


class Note:
    def __init__(self, note_index: int) -> None:
        self.note_index = note_index
        self.note_value = NOTES[note_index]

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Note):
            return self.note_index == value.note_index

    def __add__(self, other: int) -> "Note":
        return Note((self.note_index + other) % NB_NOTES)

    def __sub__(self, other: "Note") -> "Note":
        return (self.note_index - other.note_index) % NB_NOTES

    @classmethod
    def from_notation(cls, notation: str) -> "Note":
        return Note(NOTES.index(notation))


def is_minor_third(note1: Note, note2: Note):
    return note2 - note1 == MINOR_THIRD_INTERVAL


def is_major_third(note1: Note, note2: Note):
    return note2 - note1 == MAJOR_THIRD_INTERVAL


def is_perfect_fifth(note1: Note, note2: Note):
    return note2 - note1 == PERFECT_FIFTH_INTERVAL


class Chord:
    def __init__(self, notes: list[Note]) -> None:
        self.notes = notes

    @classmethod
    def from_note_indices(cls, notes) -> "Chord":
        return Chord([Note(note) for note in notes])

    def is_major_triad(self) -> bool:
        if len(self.notes) != 3:
            return False

        # TODO: deal with inversions, in particular identify root?

        return is_major_third(self.notes[0], self.notes[1]) and is_perfect_fifth(
            self.notes[0], self.notes[2]
        )

    def is_minor_triad(self) -> bool:
        if len(self.notes) != 3:
            return False

        # TODO: deal with inversions, in particular identify root?
        return is_minor_third(self.notes[0], self.notes[1]) and is_perfect_fifth(
            self.notes[0], self.notes[2]
        )

    def is_diminished_triad(self) -> bool:
        if len(self.notes) != 3:
            return False

        # TODO: deal with inversions, in particular identify root?
        return is_minor_third(self.notes[0], self.notes[1]) and is_minor_third(
            self.notes[1], self.notes[2]
        )

    def to_notation(self) -> str:
        if self.is_major_triad():
            return self.notes[0].note_value
        if self.is_minor_triad():
            return self.notes[0].note_value + "m"
        if self.is_diminished_triad():
            return self.notes[0].note_value + "°"

    @classmethod
    def from_chord_notation(cls, chord_notation) -> "Chord":
        if chord_notation[-1] == "°":
            root = Note.from_notation(chord_notation[:-1])
            return Chord([root, root + MINOR_THIRD_INTERVAL, root + 2 * MINOR_THIRD_INTERVAL])
        elif chord_notation[-1] == "m":
            root = Note.from_notation(chord_notation[:-1])
            return Chord([root, root + MINOR_THIRD_INTERVAL, root + PERFECT_FIFTH_INTERVAL])
        elif chord_notation in NOTES:
            root = Note.from_notation(chord_notation)
            return Chord([root, root + MAJOR_THIRD_INTERVAL, root + PERFECT_FIFTH_INTERVAL])


def get_root_and_mode_from_key(key: str) -> tuple[Note, MODES]:
    if key[-1] == "m":
        return Note.from_notation(key[:-1]), MODES.MINOR
    else:
        return Note.from_notation(key), MODES.MAJOR


class Key:
    def __init__(self, notation) -> None:
        self.key_notation = notation
        self.root, self.mode = get_root_and_mode_from_key(self.key_notation)
        self.notes = self.get_notes()
        self.nb_notes = len(self.notes)

    def get_notes(self) -> list[Note]:
        if self.mode == MODES.MAJOR:
            notes = [self.root]
            for step in (2, 2, 1, 2, 2, 2):
                notes.append(notes[-1] + step)
            return notes
        if self.mode == MODES.MINOR:
            notes = [self.root]
            for step in (2, 1, 2, 2, 1, 2):
                notes.append(notes[-1] + step)
            return notes

    def contains_chord(self, chord: Chord) -> bool:
        for note in chord.notes:
            if note not in self.notes:
                return False
        return True

    def get_numeral_from_chord(self, chord: Chord) -> str:
        root = chord.notes[0]  # TODO: define root explicitly
        try:
            chord_value = self.notes.index(root)
        except ValueError:
            raise IOError(
                f"Root note of chord {chord.to_notation()} is not in key {self.key_notation}"
            )
        numeral = ROMAN_NUMERALS[chord_value]

        if chord.is_major_triad():
            return numeral.upper()
        elif chord.is_minor_triad():
            return numeral
        elif chord.is_diminished_triad():
            return numeral + "°"

    @classmethod
    def all_keys(cls) -> Generator["Key", None, None]:
        for note in NOTES:
            yield Key(note)
            yield Key(note + "m")

    def all_chords(self) -> Generator[Chord, None, None]:
        for i in range(self.nb_notes):
            yield Chord(
                [
                    self.notes[i],
                    self.notes[(i + 2) % self.nb_notes],
                    self.notes[(i + 4) % self.nb_notes],
                ]
            )


def find_keys(chords: list[Chord]) -> list[Key]:
    keys = []
    for key in Key.all_keys():
        is_key = True
        for chord in chords:
            if not key.contains_chord(chord):
                is_key = False
        if is_key:
            keys.append(key)
    return keys


if __name__ == "__main__":
    # No Woman No Cry
    nwnc_chords = [Chord.from_chord_notation(notation) for notation in ("C", "G", "Am", "F")]
    print(
        "Analysing No Woman No Cry, which has chords: "
        f"{[chord.to_notation() for chord in nwnc_chords]}"
    )
    keys = find_keys(nwnc_chords)
    print(f"These are the possible keys {[key.key_notation for key in keys]}")
    key = keys[0]
    print(f"Selected the key {key.key_notation}")
    for chord in nwnc_chords:
        print(f"{chord.to_notation()}: {key.get_numeral_from_chord(chord)}")

    # Creep
    creep_chords = [Chord.from_chord_notation(notation) for notation in ("G", "B", "C", "Cm")]
    print("Analysing Creep, which has chords: " f"{[chord.to_notation() for chord in nwnc_chords]}")
    key = Key("G")
    print(f"And is in key: {key.key_notation}")
    for chord in creep_chords:
        print(f"{chord.to_notation()}: {key.get_numeral_from_chord(chord)}")

    for chord in creep_chords:
        if key.contains_chord(chord):
            print(f"{chord.to_notation()} is in {key.key_notation} key")
        else:
            print(f"{chord.to_notation()} is not strictly speaking in {key.key_notation} key")

