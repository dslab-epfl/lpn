from collections import deque

class Place:
    def __init__(self, id: str):
        self.id = id
        self.tokens = deque()
        self.tokens_init = deque()
        self.type_annotations = []
        self.mode = 0
        self.shadow = None

place = Place("example")
print("shadow" in place.__dict__)  # This should print True

