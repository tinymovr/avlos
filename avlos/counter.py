class Counter:
    def __init__(self, starting=0):
        self.count = starting

    def next(self):
        cnt = self.count
        self.count += 1
        return cnt

    def count(self):
        return self.count


counter = None


def make_counter():
    global counter
    counter = Counter()


def get_counter():
    return counter
