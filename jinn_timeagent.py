from agent import JinnAgent
from utility_space import UtilitySpace
from bid import Bid
from timeline import Timeline

class TimeAgent(JinnAgent):
    def __init__(self, agentjid, password, name, utility_space=UtilitySpace, timeline=Timeline):
        super().__init__(agentjid, password)
        self.ru = 0.5
        self.beta = .9

        self.agent_id = agentjid

        self.timeline = timeline
        self.us = utility_space

        self.initialize()

    def aspiration(self):
        current_time = self.timeline.get_time()
        return (1.0 - (1.0 - self.ru) * pow(current_time, 1.0 / self.beta))

    def initialize(self):
        return

    def accept_offer(self, bid=Bid):
        accept = False
        aspiration = self.aspiration()

        utility = self.get_utility(bid, discounted=True) 
        print('🔥', self.name, aspiration, bid.index, utility)
        if(utility >= aspiration):
            print('👹', self.name, aspiration, bid.index, utility)
            accept = True

        return accept

    def propose_offer(self):
        aspiration = self.aspiration()

        return self.us.get_random(aspiration, 1)
        
            
