from enum import Enum
from typing import Generator

ROMAN_NUMERALS = ["i", "ii", "iii", "iv", "v", "vi", "vii"]
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
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

    def __repr__(self) -> str:
        return self.to_notation()

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
            raise IOError(f"Root note of chord {chord} is not in key {self.key_notation}")
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

    def __repr__(self) -> str:
        return self.key_notation


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
    is_not_empty = True
    print("First write the chords of the song you with to analyse.")
    print("Please type one chord per line (don't use flats! just sharps!)")
    print("When done, just press Enter.")
    chords = []
    while True:
        chord_input = input()
        if chord_input == "":
            break
        else:
            chords.append(Chord.from_chord_notation(chord_input))
    key_input = input("Type the key of your song. If you don't know just press Enter: ")

    if key_input == "":
        keys = find_keys(chords)

        if keys == []:
            print("There are no keys completely consistent with the chords you put in.")
            exit()

        print(f"These are the possible keys {[key for key in keys]}")
        key_input = input("Which one do you want to use? ")
        if key_input == "":
            key_input = str(keys[0])
            print(f"As you did not input a key, using the first one, {key_input}")
    key = Key(key_input)

    print(f"Here is the roman numeral analysis of your song in the key of {key}")
    for chord in chords:
        print(f"{chord}: {key.get_numeral_from_chord(chord)}")

    if any(not key.contains_chord(chord) for chord in chords):
        print(
            f"Not all chords are strictly contained in key {key}: "
            f"{[chord for chord in chords if not key.contains_chord(chord)]}"
        )
        print(f"The chords in the key are {list(key.all_chords())}")
