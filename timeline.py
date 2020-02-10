import time

class Timeline():

    def __init__(self, total, has_deadline=True):
        self.start = time.time()
        self.total = total
        self.has_deadline = has_deadline

    # Absolute
    def get_time_absolute(self):
        return time.time() - self.start

    # Normalized
    def get_time(self):
        return min(self.get_time_absolute() / self.total, 1.0)

    # Over
    def over_deadline(self):
        return (time.time() - (self.total + self.start)) >= 0


