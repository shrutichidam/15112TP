#englishWords.txt file adapted from https://github.com/first20hours/google-10000-english

class Words(object):
    def __init__(self):
        self.words = self.initializeDictionary()

    #creates dictionary of English words, where key is the difficulty level, value is a list of words 
    def initializeDictionary(self):
        easyWords = []
        mediumWords = []
        hardWords = []
        file = open("englishWords.txt", "r")
        listWords = file.read().split("\n")
        for word in listWords:
            if len(word) < 5:
                easyWords.append(word)
            elif len(word) < 7:
                mediumWords.append(word)
            else:
                hardWords.append(word)
        return {1: easyWords, 2: mediumWords, 3: hardWords}
