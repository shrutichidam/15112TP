import random
class AI(object):
    def __init__(self, dictionary, lengthOfWord):
       self.dictionary = dictionary
       self.wordLength = lengthOfWord
       self.lettersGuessed = set()
       self.wordGuessed = "?" * self.wordLength
       self.done = False

    def getSimilarWords(self):
        simWords = []
        for word in self.dictionary:
            if len(word) != self.wordLength:
                continue
            if self.isSimilar(word):
                simWords.append(word)
        return simWords

    def isSimilar(self, word):
        for i in range(len(word)):
            if self.wordGuessed[i] != "?" and self.wordGuessed[i] != word[i]:
                return False
        return True

    def getHighestFrequencies(self, similarWords):
        freq = dict()
        highestCount = None
        highestCountLetter = list()
        for word in similarWords:
            for letter in word:
                if letter not in self.lettersGuessed:
                    if letter not in freq:
                        freq[letter] = 0
                    freq[letter] += 1
                    if highestCount == None or freq[letter] > highestCount:
                        highestCount = freq[letter]
                        highestCountLetter = []
                        highestCountLetter.append(letter)
                    if freq[letter] == highestCount:
                        if letter not in highestCountLetter:
                            highestCountLetter.append(letter)
        return highestCountLetter

    def guessLetter(self):
        similarWords = self.getSimilarWords()
        possibleGuesses = self.getHighestFrequencies(similarWords)
        guess = possibleGuesses.pop(random.randint(0,len(possibleGuesses)-1))
        self.lettersGuessed.add(guess)
        return guess

    #returns True when the wordToGuess is complete
    def isDoneGuessing(self):
        if "?" not in self.wordGuessed:
            return True
        return False




