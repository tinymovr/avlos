class Counter:
    """
    A plain counter class with the ability
    to return the current and next index with
    auto-increment
    """

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
    """
    Create a new counter and assign it to the
    global reference
    """
    global counter
    counter = Counter()


def get_counter():
    """
    Get the global counter
    """
    return counter


def delete_counter():
    """
    Delete the global counter
    """
    global counter
    counter = None
