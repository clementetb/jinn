import numpy as np
import matplotlib.pyplot as plt

import sys
import logging
import time
from loguru import logger

from genius_template_importer import import_template
from bidding import generate_bids
from helpers import is_pareto_efficient

from bid import Bid
from utility_space import UtilitySpace
from timeline import Timeline
from agent import JinnAgent
from matplot_analyzer import MatplotAgent

from jinn_timeagent import TimeAgent
from jinn_agents import ConcederAgent, BoulwareAgent, Tit4TatRelativeAgent

NEGOTIATION_TIME = 60

if __name__ == "__main__":
    template1 = import_template("templates/Camera/camera_buyer_utility.xml")
    template2 = import_template("templates/Camera/camera_seller_utility.xml")

    us_buyer = UtilitySpace(template1)
    us_seller = UtilitySpace(template2)

    tl = Timeline(NEGOTIATION_TIME)

    
    tab = TimeAgent('ta_buyer@localhost', 'aaa', 'TA Buyer', us_buyer, tl)
    #tas = TimeAgent('ta_seller@gtirouter.dsic.upv.es', 'aaa', 'TA Seller', us_seller, tl)
    #tas = ConcederAgent('ta_seller@gtirouter.dsic.upv.es', 'aaa', 'TA Seller', us_seller, tl)
    #tas = BoulwareAgent('ta_seller@gtirouter.dsic.upv.es', 'aaa', 'TA Seller', us_seller, tl)
    tas = Tit4TatRelativeAgent('ta_seller@localhost', 'aaa', 'TA Seller', us_seller, tl)


    analyzer_agent = MatplotAgent('analyzer@localhost', 'secret',
                                  'ta_buyer@localhost', us_buyer, 'ta_seller@localhost', us_seller)
    analyzer_agent.start()
#     tab = TimeAgent('ta_buyer@localhost', 'aaa', 'TA Buyer', us_buyer, tl)
#     tas = TimeAgent('ta_seller@localhost', 'aaa', 'TA Seller', us_seller, tl)

    tab.set_analyzer('analyzer@localhost')
    tas.set_analyzer('analyzer@localhost')


    JinnAgent.set_opponents(tab, tas)

    time.sleep(1)
    futureb = tab.start()
    futures = tas.start()

    futureb.result()
    futures.result()

    verbose = 0

    if verbose > 0:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO")
