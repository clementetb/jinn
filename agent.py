import json
import time

import jsonpickle

from asyncio import CancelledError

from loguru import logger
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

from protocol import NEGOTIATION_PROTOCOL, \
    BID_ACCEPT_PERFORMATIVE, BID_REFUSE_PERFORMATIVE, BID_OFFER_PERFORMATIVE, NEGOTIATION_END_PERFORMATIVE, \
    JINN_READY, JINN_DONE, JINN_WAITING, ANALYSIS_PROTOCOL, HISTORIC_PERFORMATIVE, ACCEPTANCE_PERFORMATIVE

from utility_space import UtilitySpace
from bid import Bid
from timeline import Timeline

# from .utils import CUSTOMER_WAITING, CUSTOMER_IN_DEST, TRANSPORT_MOVING_TO_CUSTOMER, CUSTOMER_IN_TRANSPORT, \
#     TRANSPORT_IN_CUSTOMER_PLACE, CUSTOMER_LOCATION, StrategyBehaviour, request_path, status_to_str


class JinnAgent(Agent):

    INSTANCES = 1

    def __init__(self, agentjid, password):
        super().__init__(agentjid, password)

        # Utilidad mínima aceptada por el agente. Inmutable durante una negociación.
        self.ru = float
        # Factor para el cálculo de la utilidad en términos temporales Inmutable durante una negociación.
        self.beta = float
        # Número de ofertas a recordar para negociación con memoria (tit-for-tat). Inmutable durante una negociación.
        self.delta = float

        self.us = UtilitySpace

        self.sentOffers = list()
        self.opponentOffers = list()
        self.offers_indexes = []

        self.timeline = Timeline

        self.last_action = None
        self.last_content = None
        self.analyzer_jid = None

        self.turn = None
        self.session = None

        self.agent_id = JinnAgent.INSTANCES
        JinnAgent.INSTANCES += 1

        # Examples: Conceder, Boulware... or any human-friendly name
        #self.name = 'Name'
        self.strategy = NegotiationBehaviour()

        self.status = None
        self.acceptedBid = Bid

        self.opponent_id = None
        self.opponent_name = str

        self.init_time = None

        self.type_service = "JinnAgent"
        self.running_strategy = False

    # Por qué async?
    async def setup(self):
        try:
            template = Template()
            template.set_metadata("protocol", NEGOTIATION_PROTOCOL)
            negotation_b = self.strategy
            self.add_behaviour(negotation_b, template)
            while not self.has_behaviour(negotation_b):
                logger.warning(
                    "Customer {} could not create NegotiationBehaviour. Retrying...".format(self.agent_id))
                self.add_behaviour(negotation_b, template)
        except Exception as e:
            logger.error("EXCEPTION creating NegotiationBehaviour in Jinn Agent {}: {}".format(
                self.agent_id, e))

    # Not really needed at the moment
    # def run_strategy(self):
    #     """import json
    #     Runs the strategy for the customer agent.
    #     """
    #     if not self.running_strategy:
    #         negotiation_template = Template()
    #         negotiation_template.set_metadata("protocol", NEGOTIATION_PROTOCOL)
    #         self.add_behaviour(self.strategy(), negotiation_template)
    #         self.running_strategy = True

    def set_id(self, agent_id):
        """
        Sets the agent identifier
        Args:
            agent_id (str): The new Agent Id
        """
        self.agent_id = agent_id

    def set_opponent(self, agent_jid, agent_name):
        """
        Sets the agent identifier
        Args:
            agent_id (str): The new Agent Id
        """
        self.opponent_id = agent_jid
        self.opponent_name = agent_name

    @staticmethod
    def set_opponents(a=Agent, b=Agent):
        a.set_opponent(b.jid, b.name)
        b.set_opponent(a.jid, a.name)
        a.status = JINN_READY
        b.status = JINN_WAITING

    def get_utility(self, bid, discounted=False):
        if discounted:
            return self.us.utility_space[bid.index][-1] * pow(self.us.discount, self.timeline.get_time())
        else:
            return self.us.utility_space[bid.index][-1]

    def accept_offer(bid=Bid):
        raise NotImplementedError

    def propose_offer():
        raise NotImplementedError

    def initialize():
        raise NotImplementedError

    def set_analyzer(self, jid):
        self.analyzer_jid = jid


class NegotiationBehaviour(CyclicBehaviour):
    """
    """

    async def on_start(self):
        """
        Initializes the logger and timers. Call to parent method if overloaded.
        """
        logger.debug("Strategy {} started in customer {}".format(
            type(self).__name__, self.agent.name))
        self.agent.init_time = time.time()
        #logger.debug("Customer {} started NegotiationBehaviour.".format(self.agent.name))

    async def on_end(self):
        print("Behaviour finished with exit code {}.".format(self.exit_code))
        # self.agent.stop()

    async def offer(self, bid=Bid, content=None):
        """
        """
        if content is None or len(content) == 0:
            content = {
                "jinn_id": str(self.agent.agent_id),
                "jinn_name": str(self.agent.name),
                "opponent_id": str(self.agent.opponent_id),
                "opponent_name": str(self.agent.opponent_name),
                "bid": jsonpickle.encode(bid),
                "bid_index": str(bid.index),
                "bid_id": str(bid.id)
            }

        msg = Message()
        msg.to = str(self.agent.opponent_id)
        msg.set_metadata("protocol", NEGOTIATION_PROTOCOL)
        msg.set_metadata("performative", BID_OFFER_PERFORMATIVE)
        msg.body = json.dumps(content)

        self.agent.last_action = BID_OFFER_PERFORMATIVE
        self.agent.last_content = content

        await self.send(msg)

        analysis_msg = Message()
        analysis_msg.to = str(self.agent.analyzer_jid)
        analysis_msg.set_metadata("protocol", ANALYSIS_PROTOCOL)
        analysis_msg.set_metadata("performative", HISTORIC_PERFORMATIVE)

        analysis_msg.body = str(bid.index)
        
        await self.send(analysis_msg)

        logger.info("Agent {} sent bid {} to agent {}.".format(
            self.agent.name, str(content['bid_id']), self.agent.opponent_name))

    async def accept(self, bid=Bid, content=None):
        """
        """

        if content is None or len(content) == 0:
            content = {
                "jinn_id": str(self.agent.agent_id),
                "jinn_name": str(self.agent.name),
                "opponent_id": str(self.agent.opponent_id),
                "opponent_name": str(self.agent.opponent_name),
                "bid": jsonpickle.encode(bid),
                "bid_index": str(bid.index),
                "bid_id": str(bid.id)
            }

        # for fleetmanager in self.agent.fleetmanagers.keys():  # Send a message to all FleetManagers
        msg = Message()
        msg.to = str(self.agent.opponent_id)
        msg.set_metadata("protocol", NEGOTIATION_PROTOCOL)
        msg.set_metadata("performative", BID_ACCEPT_PERFORMATIVE)
        msg.body = json.dumps(content)

        self.agent.last_action = BID_ACCEPT_PERFORMATIVE
        self.agent.last_content = content

        await self.send(msg)

        analysis_msg = Message()
        analysis_msg.to = str(self.agent.analyzer_jid)
        analysis_msg.set_metadata("protocol", ANALYSIS_PROTOCOL)
        analysis_msg.set_metadata("performative", ACCEPTANCE_PERFORMATIVE)

        analysis_msg.body = str(bid.index)
        
        await self.send(analysis_msg)

        logger.info("Jinn {} accepted bid {} from {}.".format(
            self.agent.name, str(content['bid_id']), self.agent.opponent_name))

    async def refuse(self, bid=Bid, content=None):
        """
        """
        reply = Message()
        reply.to = str(self.agent.opponent_id)
        reply.set_metadata("protocol", NEGOTIATION_PROTOCOL)
        reply.set_metadata("performative", BID_REFUSE_PERFORMATIVE)

        if content is None or len(content) == 0:
            content = {
                "jinn_id": str(self.agent.agent_id),
                "jinn_name": str(self.agent.name),
                "opponent_id": str(self.agent.opponent_id),
                "opponent_name": str(self.agent.opponent_name),
                "bid": jsonpickle.encode(bid),
                "bid_index": str(bid.index),
                "bid_id": str(bid.id)
            }

        self.agent.last_action = BID_REFUSE_PERFORMATIVE
        self.agent.last_content = content

        reply.body = json.dumps(content)
        await self.send(reply)

        print('content', content['bid_id'])
        logger.info("Jinn {} refused bid {} from {}.".format(
            self.agent.name, content['bid_id'], self.agent.opponent_name))

    async def run(self):
        if self.agent.timeline.has_deadline and self.agent.timeline.over_deadline():
            print('⏰ TIME FINISHED')
            self.agent.status = JINN_DONE
            await self.agent.stop()

        if self.agent.status == JINN_READY:
            offer = self.agent.propose_offer()
            if offer is not None:
                print('🐮 OFFER', offer.index)
                self.agent.sentOffers = self.agent.sentOffers + [offer]
                # self.agent.offers_indexes.append(int(offer.index))
                self.agent.status == JINN_WAITING
                await self.offer(offer)
            else:
                # print('🔥 SLEEP')

                # time.sleep(1)
                pass

        msg = await self.receive(timeout=1)

        if msg:
            content = json.loads(msg.body)
            performative = msg.get_metadata("performative")
            sender = msg.sender  # Always the opponent?

            # Imprime el tipo de performativa
            logger.debug("It's a {}".format(performative))

            if performative == BID_OFFER_PERFORMATIVE:
                # Se calcula la distancia del taxi que envía la propuesta
                #bid = jsonpickle.decode(content['bid'])
                print('🐮', (content['bid_index']))
                bid = self.agent.us.get_by_index(int(content['bid_index']))

                # Accummulate on offers
                self.agent.opponentOffers = self.agent.opponentOffers + [bid]

                logger.info(
                    "Bid {} offer from Jinn {} received".format(bid.id, sender))

                # The offer is accepted according to `accept_offer` implementation.
                if self.agent.accept_offer(bid):
                    logger.info("🎉 Jinn {} accepted offer {} from {}".format(
                        self.agent.name, bid.id, content['jinn_name']))
                    try:
                        await self.accept(bid)
                        self.agent.status = JINN_DONE
                        self.agent.acceptedBid = bid
                        await self.agent.stop()
                    except Exception as e:
                        self.agent.status = JINN_READY
                        self.agent.acceptedBid = None
                # The offer is not accepted
                else:
                    logger.info("Jinn {} refused offer {} from {}".format(
                        self.agent.name, bid.id, content['jinn_name']))
                    self.agent.status = JINN_READY
                    await self.refuse(bid, content)

            # Bid is accepted, Jinn finishes
            elif performative == BID_REFUSE_PERFORMATIVE:
                #self.agent.acceptedBid = msg.bid
                self.agent.status = JINN_READY

            # Bid is accepted, Jinn finishes
            elif performative == BID_ACCEPT_PERFORMATIVE:
                #self.agent.acceptedBid = msg.bid
                self.agent.status = JINN_DONE
                await self.agent.stop()

        elif self.agent.status == JINN_WAITING:
            if self.agent.last_action == BID_OFFER_PERFORMATIVE:
                offer = self.agent.sentOffers[-1]
                await self.offer(offer, content=self.agent.last_content)
            if self.agent.last_action == BID_REFUSE_PERFORMATIVE:
                await self.refuse(content=self.agent.last_content)
            if self.agent.last_action == BID_ACCEPT_PERFORMATIVE:
                await self.accept(content=self.agent.last_content)


class AnalyzerAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)

    async def setup(self):
        self.add_behaviour(AnalyzerBehavior())

    def on_proposal(self, name, bid):
        raise NotImplementedError

    def on_acceptance(self, bid):
        raise NotImplementedError


class AnalyzerBehavior(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=1)
        if msg:
            protocol = msg.get_metadata("protocol")
            if protocol is ANALYSIS_PROTOCOL:
                performative = msg.get_metadata("performative")
                
                if performative is HISTORIC_PERFORMATIVE:
                    bid_index = int(msg.body)
                    self.agent.on_proposal(str(msg.sender), bid_index)

                elif performative is ACCEPTANCE_PERFORMATIVE:
                    bid_index = int(msg.body)
                    self.agent.on_acceptance(bid_index)

