import random

class FantasyNameGenerator:
    """
    Generates fantasy universe names by combining syllables following specific phonetic patterns.
    """

    def __init__(self):
        # Define syllable categories to create structured names
        # Onsets: consonant or consonant clusters that can start a syllable
        self.onsets = [
            "",  # Allow syllables that start with a vowel sound
            "b", "br", "bl", "c", "cr", "cl", "d", "dr", "f", "fr",
            "fl", "g", "gr", "gl", "h", "j", "k", "kr", "kl", "l", 
            "m", "n", "p", "pr", "pl", "qu", "r", "s", "st", "str", 
            "sl", "t", "tr", "v", "w", "z", "zh", "sh", "ch"
        ]

        # Vowels or vowel combinations (nuclei of syllables)
        self.vowels = [
            "a", "e", "i", "o", "u", "ae", "ai", "au", "ea", "ee", "ei",
            "io", "oa", "oe", "oo", "ou", "ua", "ue", "ui"
        ]

        # Codas: consonant or consonant clusters that can end syllables
        self.codas = [
            "",  # Allow open syllables (ending in vowel)
            "b", "d", "g", "k", "l", "m", "n", "r", "s", "t", "th",
            "nd", "st", "nt", "rk", "rd", "sh", "ss", "zz", "ck"
        ]

        # Patterns for the structure of syllables
        # Each pattern is a tuple of (onset, vowel, coda)
        self.syllable_patterns = [
            (True, True, True),   # onset + vowel + coda
            (True, True, False),  # onset + vowel
            (False, True, True),  # vowel + coda
            (False, True, False), # vowel only
        ]

        # Name length in syllables: fantasy names usually have 2-4 syllables
        self.min_syllables = 2
        self.max_syllables = 4

    def generate_syllable(self) -> str:
        """
        Generate a single syllable based on a randomly chosen pattern.
        
        Returns:
            A syllable string
        """
        pattern = random.choice(self.syllable_patterns)
        onset = random.choice(self.onsets) if pattern[0] else ""
        vowel = random.choice(self.vowels) if pattern[1] else ""
        coda = random.choice(self.codas) if pattern[2] else ""

        syllable = onset + vowel + coda
        return syllable

    def generate_name(self) -> str:
        """
        Generate a fantasy name composed of multiple syllables combined with rules
        about smooth transitions and allowed combinations to make names feel coherent.

        Returns:
            A string representing a generated fantasy name.
        """
        syllable_count = random.randint(self.min_syllables, self.max_syllables)
        name_syllables = []

        for i in range(syllable_count):
            # Generate a syllable
            syll = self.generate_syllable()

            # Improve cohesion:
            # Avoid starting syllable with same onset as last coda to prevent repetition
            if i > 0:
                prev_coda_last_char = name_syllables[-1][-1] if name_syllables[-1] else ""
                onset_first_char = syll[0] if syll else ""
                # If onset starts with same letter as previous coda ends, regenerate to avoid repetition
                trials = 0
                while onset_first_char == prev_coda_last_char and trials < 5:
                    syll = self.generate_syllable()
                    onset_first_char = syll[0] if syll else ""
                    trials += 1

            name_syllables.append(syll)

        # Capitalize first letter to make it resemble a proper name
        name = "".join(name_syllables).capitalize()
        return name

if __name__ == "__main__":
    generator = FantasyNameGenerator()
    # Generate and print 10 example fantasy names
    for _ in range(10):
        print(generator.generate_name())

