class Words(object):
    def __init__(self):
        self.words = self.initializeDictionary()

    #creates dictionary of English words, where key is the difficulty level, value is a list of words 
    #words dictionary not complete yet
    def initializeDictionary(self):
        easyWords =["cat", "dog", "home", "jazz", "buzz", "fuzz", "quiz", "mat", "rat", "desk", "all", "pool", "ant"]
        mediumWords = ["llama", "house", "photo", "jolly"]
        hardWords = ["caterpillar", "programming", "vivacious", "textbook", "pumpkin", "holiday", "mesmerize"]
        return {1: easyWords, 2: mediumWords, 3: hardWords}
