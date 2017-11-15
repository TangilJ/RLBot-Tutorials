class Agent:
    def __init__(self, name, team, index):
        self.index = index

    def get_output_vector(self, values):
        return [1, 0, 0, 0, 0, False, False, False]
