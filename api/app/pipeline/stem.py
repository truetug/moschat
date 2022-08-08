import Stemmer


class SnowballHandler:
    def __init__(self):
        self.stemmer = Stemmer.Stemmer('russian')

    def process(self, value):
        return self.stemmer.stemWords(value)
