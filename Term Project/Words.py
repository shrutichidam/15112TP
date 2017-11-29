class Words(object):
    def __init__(self):
        self.words = self.initializeDictionary()

    #still have to add a lot more words to each set, maybe find a better way to do this 
    def initializeDictionary(self):
        easyWords =["cat", "dog", "home", "jazz", "buzz", "fuzz", "quiz", "mat", "rat", "desk", "all", "pool", "ant"]
        mediumWords = ["llama", "house", "photo"]
        hardWords = ["caterpillar", "programming", "vivacious"]
        return {1: easyWords, 2: mediumWords, 3: hardWords}
