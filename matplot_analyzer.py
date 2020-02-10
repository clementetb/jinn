from agent import AnalyzerAgent
from bidding import UtilitySpace
import matplotlib
# matplotlib.rcParams['backend'] = "QT4Agg"
import matplotlib.pyplot as plt

import threading
import _thread

def create():
    plt.ion()
    plt.axis([-50,50,0,10000])
    while True:
        # plt.show()
        plt.pause(0.0001)

class MatplotAgent(AnalyzerAgent):
    def __init__(self, jid, password, agent_a_name, agent_a_us: UtilitySpace, agent_b_name, agent_b_us: UtilitySpace):
        super().__init__(jid, password)
        self.agent_a_name = agent_a_name
        self.agent_b_name = agent_b_name

        self.utility_a = agent_a_us.get_utility()
        self.utility_b = agent_b_us.get_utility()

        self.proposals_a_x = []
        self.proposals_a_y = []
        self.proposals_b_x = []
        self.proposals_b_y = []

        _thread.start_new_thread(self.paint_loop, ())

    def paint_loop(self):

        plt.ion()
        while True:
            plt.clf()
            plt.axis([-.1, 1.1, -.1, 1.1])
            plt.plot(self.utility_a, self.utility_b, 'ro', ms=1)
            plt.plot(self.proposals_a_x, self.proposals_a_y, '-bs')
            plt.plot(self.proposals_b_x, self.proposals_b_y, '-gs')
            plt.pause(.5)


    def on_proposal(self, name, bid):
        print(name)
        print(name)
        print(name)
        if str(name) == self.agent_a_name:
            self.proposals_a_x.append(self.utility_a[bid.index][-1])
            self.proposals_a_y.append(self.utility_b[bid.index][-1])
        elif str(name) == self.agent_b_name:
            self.proposals_b_x.append(self.utility_a[bid.index][-1])
            self.proposals_b_y.append(self.utility_b[bid.index][-1])
