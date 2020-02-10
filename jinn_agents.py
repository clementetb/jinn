from jinn_timeagent import TimeAgent
from utility_space import UtilitySpace
from bid import Bid
from timeline import Timeline

class ConcederAgent(TimeAgent):
    def __init__(self, agentjid, password, name, utility_space=UtilitySpace, timeline=Timeline):
        super().__init__(agentjid, password, name, utility_space, timeline)
        self.initialize()

    def initialize(self):
        self.beta = 3.0


class BoulwareAgent(TimeAgent):
    def __init__(self, agentjid, password, name, utility_space=UtilitySpace, timeline=Timeline):
        super().__init__(agentjid, password, name, utility_space, timeline)
        self.initialize()

    def initialize(self):
        self.beta = 0.33


class Tit4TatRelativeAgent(TimeAgent):
    def __init__(self, agentjid, password, name, utility_space=UtilitySpace, timeline=Timeline):
        super().__init__(agentjid, password, name, utility_space, timeline)
        self.initialize()

    def initialize(self):
        self.beta = 1.0
        self.ru = 0.5
        self.delta = 3

    def aspiration(self):
        aspiration = 0.0
        current_time = self.timeline.get_time()

        nSentOffers = len(self.sentOffers)
        nReceivedOffers = len(self.opponentOffers)
        if nReceivedOffers > self.delta and nSentOffers > 0:
            rel = self.get_utility(self.sentOffers[-1]) * (1.0 - self.get_utility(self.opponentOffers[nReceivedOffers-self.delta+1])) / (1.0 - self.get_utility(self.opponentOffers[nReceivedOffers-self.delta]))
            aspiration = min(1.0, max(self.ru, rel))
        else:
            aspiration = 0.8

        return aspiration

    def accept_offer(self, bid=Bid):
        accept = False
        aspiration = self.aspiration()

        utility = self.get_utility(bid, discounted=True) 
        print('🔥', self.name, aspiration, bid.index, utility)
        if(utility >= aspiration):
            accept = True

        return accept

    def propose_offer(self):
        aspiration = self.aspiration()

        return self.us.get_random(aspiration, 1)
