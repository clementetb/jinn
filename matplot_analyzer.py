from agent import AnalyzerAgent
from bidding import UtilitySpace
import matplotlib.pyplot as plt
from threading import Lock
import _thread
import numpy as np
from helpers import is_pareto_efficient


class MatplotAgent(AnalyzerAgent):
    def __init__(self, jid, password, agent_a_name, agent_a_us, agent_b_name, agent_b_us):
        super().__init__(jid, password)
        self.agent_a_name = agent_a_name
        self.agent_b_name = agent_b_name

        self.utility_a = agent_a_us.utility_space[:-1]
        self.utility_b = agent_b_us.utility_space[:-1]
        self.lock = Lock()
        self.offers_a = []
        self.offers_b = []

        self.pareto_points = self.calculate_pareto_frontier()

        self.agreement = None

        _thread.start_new_thread(self.paint_loop, ())

    def calculate_pareto_frontier(self):
        points = np.vstack([self.utility_a[:,-1], self.utility_b[:,-1]]).transpose()

        pareto_points = is_pareto_efficient(points, return_mask=True)

        px = points[:, 0]
        py = np.ma.masked_array(points[:, 1], mask=~pareto_points)

        pareto_points = np.ma.masked_array(points, mask=np.vstack(
            [~pareto_points, ~pareto_points]).transpose()).compressed().reshape(-1, 2)

        pareto_sorted = []
        for i in range(pareto_points.shape[0]):
            pareto_sorted.append((pareto_points[i, 0], pareto_points[i, 1]))

        pareto_sorted = sorted(pareto_sorted, key=lambda x: x[0])
        pareto_sorted = np.array(pareto_sorted)

        return pareto_sorted

    def get_utilities(self, utility_space, indexes):
        return utility_space[indexes, -1]

    def paint_loop(self):
        plt.ion()
        while True:
            self.lock.acquire()
            proposals_a_x = self.get_utilities(self.utility_a, self.offers_a)
            proposals_a_y = self.get_utilities(self.utility_b, self.offers_a)
            proposals_b_x = self.get_utilities(self.utility_a, self.offers_b)
            proposals_b_y = self.get_utilities(self.utility_b, self.offers_b)
            self.lock.release()

            plt.clf()
            plt.axis([-.1, 1.1, -.1, 1.1])
            plt.plot(self.utility_a, self.utility_b, 'ro', ms=1)
            plt.plot(proposals_a_x, proposals_a_y, '-bs')
            plt.plot(proposals_b_x, proposals_b_y, '-gs')
            plt.plot(self.pareto_points[:, 0], self.pareto_points[:, 1], '-m^')

            if self.agreement is not None:
                plt.plot(self.agreement[0],
                         self.agreement[1], '-rs', ms=10)
                
            plt.pause(.5)

    def on_acceptance(self, bid):
        self.agreement = [self.utility_a[bid, -1], self.utility_b[bid, -1]]

    def on_proposal(self, name, bid_index):
        self.lock.acquire()
        if name == self.agent_a_name:
            self.offers_a.append(bid_index)
        if name == self.agent_b_name:
            self.offers_b.append(bid_index)

        self.lock.release()
