import json
import time
from asyncio import CancelledError

from loguru import logger
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

# from .helpers import random_position
from .protocol import NEGOTIATION_PROTOCOL, \
        BID_ACCEPT_PERFORMATIVE, BID_REFUSE_PERFORMATIVE, BID_OFFER_PERFORMATIVE, NEGOTIATION_END_PERFORMATIVE, \
        JINN_READY_TO_NEGOTIATE, JINN_WAITING_OFFER_RESPONSE, JINN_WAITING_ACCEPTANCE_RESPONSE, JINN_ACCEPTED_OFFER, \
        JINN_READY, JINN_DONE, JINN_WAITING

# from .utils import CUSTOMER_WAITING, CUSTOMER_IN_DEST, TRANSPORT_MOVING_TO_CUSTOMER, CUSTOMER_IN_TRANSPORT, \
#     TRANSPORT_IN_CUSTOMER_PLACE, CUSTOMER_LOCATION, StrategyBehaviour, request_path, status_to_str


class JinnAgent(Agent):
    def __init__(self, agentjid, password):
        super().__init__(agentjid, password)

        # Utilidad mínima aceptada por el agente. Inmutable durante una negociación.
        self.ru = float
        # Factor para el cálculo de la utilidad en términos temporales Inmutable durante una negociación.
        self.beta = float

        # Número de ofertas a recordar para negociación con memoria (tit-for-tat). Inmutable durante una negociación.
        self.delta = float

        self.sentOffers = list()
        self.opponentOffers = list()

        self.timeline = None
        self.turn = None
        self.session = None

        self.agent_id = None
        self.strategy = None

        self.status = JINN_READY
        self.acceptedBid = Bid

        self.opponent = JinnAgent

        self.init_time = None

        self.type_service = "JinnAgent"

    # Por qué async?
    async def setup(self):
        try:
            template = Template()
            template.set_metadata("protocol", NEGOTIATION_PROTOCOL)
            negotation_b = NegotiationBehaviour()
            self.add_behaviour(negotation_b, template)
            while not self.has_behaviour(negotation_b):
                logger.warning("Customer {} could not create NegotiationBehaviour. Retrying...".format(self.agent_id))
                self.add_behaviour(negotation_b, template)
        except Exception as e:
            logger.error("EXCEPTION creating NegotiationBehaviour in Jinn Agent {}: {}".format(self.agent_id, e))


    def run_strategy(self):
        """import json
        Runs the strategy for the customer agent.
        """
        if not self.running_strategy:
            template1 = Template()
            template1.set_metadata("protocol", NEGOTIATION_PROTOCOL)
            template2 = Template()
            template2.set_metadata("protocol", BID_PROTOCOL)
            self.add_behaviour(self.strategy(), template1 | template2)
            self.running_strategy = True


    def set_id(self, agent_id):
        """
        Sets the agent identifier
        Args:
            agent_id (str): The new Agent Id
        """
        self.agent_id = agent_id


    def set_directory(self, directory_id):
        """
        Sets the directory JID address
        Args:
            directory_id (str): the DirectoryAgent jid

        """
        self.directory_id = directory_id


class NegotiationBehaviour(CyclicBehaviour):
    """
    """

    async def on_start(self):
        """
        Initializes the logger and timers. Call to parent method if overloaded.
        """
        logger.debug("Strategy {} started in customer {}".format(type(self).__name__, self.agent.name))
        self.agent.init_time = time.time()
        #logger.debug("Customer {} started NegotiationBehaviour.".format(self.agent.name))

    async def on_end(self):
        print("Behaviour finished with exit code {}.".format(self.exit_code))
        #self.agent.stop()

    async def offer(self, bid=Bid, content=None):
        """
        """
        if content is None or len(content) == 0:
            content = {
                "opponent": str(self.agent.opponent),
                "bid": bid
            }

        msg = Message()
        msg.to = str(self.agent.opponent)
        msg.set_metadata("protocol", NEGOTIATION_PROTOCOL)
        msg.set_metadata("performative", BID_OFFER_PERFORMATIVE)
        msg.body = content
        await self.send(msg)
        logger.info("Customer {} sent bid {} to agent {}.".format(self.agent.name, bid.id, self.agent.opponent))


    async def accept(self, bid=Bid, content=None):
        """
        """

        if content is None or len(content) == 0:
            content = {
                "jinn_id": str(self.agent.jid),
                "bid_id": bid.id,
                "bid": bid
            }

        #for fleetmanager in self.agent.fleetmanagers.keys():  # Send a message to all FleetManagers
        msg = Message()
        msg.to = str(self.agent.opponent)
        msg.set_metadata("protocol", NEGOTIATION_PROTOCOL)
        msg.set_metadata("performative", BID_ACCEPT_PERFORMATIVE)
        msg.body = json.dumps(content)
        await self.send(msg)

        logger.info("Jinn {} accepted bid {} from {}.".format(self.agent.name, bid.id, self.agent.opponent))

    def accept_offer(bid=Bin):
        raise NotImplementedError

    def propose_offer(bid=Bin):
        raise NotImplementedError

    def initialize():
        raise NotImplementedError

    async def refuse(self, bid=Bid, opponent_id=None):
        """
        """
        reply = Message()
        reply.to = str(self.agent.opponent)
        reply.set_metadata("protocol", NEGOTIATION_PROTOCOL)
        reply.set_metadata("performative", BID_REFUSE_PERFORMATIVE)
        content = {
            "jinn_id": str(self.agent.jid),
            "opponent_id": str(self.agent.opponent),
            #"bid": bid,
            "bid_id": bid.id
        }
        reply.body = json.dumps(content)
        await self.send(reply)

        logger.info("Jinn {} refused bid {} from {}.".format(self.agent.name, bid.id, self.agent.opponent))


    async def run(self):

        if self.agent.status == JINN_READY:
            offer = propose_offer()
            await self.offer(offer)
            sentOffers = sentOffers + offer
            self.agent.status == JINN_WAITING

        msg = await self.receive(timeout=1)

        if msg:
            content = json.loads(msg.body)
            performative = msg.get_metadata("performative")
            sender = msg.sender # Always the opponent?

            ## Imprime el tipo de performativa
            logger.debug("It's a {}".format(performative))

            if performative == BID_OFFER_PERFORMATIVE:
                ## Se calcula la distancia del taxi que envía la propuesta
                bid = content.bid
                jinn_id = content.jinn_id

                ## Accummulate on offers
                self.agent.opponentOffers = self.agent.opponentOffers + bid

                logger.info("Bid {} offer from Jinn {} received".format(bid.id, sender))

                ## The offer is accepted according to `accept_offer` implementation.
                if accept_offer(bid):
                    logger.info("Jinn {} accepted offer {} from {}".format(self.agent.name, bid.id, jinn_id))
                    try:
                        await self.accept(bid)
                        self.agent.status = JINN_DONE
                        self.agent.acceptedBid = bid
                        self.agent.stop()
                    except Exception as e:
                        self.agent.status = JINN_READY
                        self.agent.acceptedBid = None
                ## The offer is not accepted
                else:
                    logger.info("Jinn {} refused offer {} from {}".format(self.agent.name, bid.id, jinn_id))
                    await self.refuse(bid, jinn_id)
                    self.agent.status = JINN_READY

            ## Bid is accepted, Jinn finishes
            elif performative == BID_REFUSE_PERFORMATIVE:
                #self.agent.acceptedBid = msg.bid
                self.agent.status = JINN_READY

            ## Bid is accepted, Jinn finishes
            elif performative == BID_ACCEPT_PERFORMATIVE:
                #self.agent.acceptedBid = msg.bid
                self.agent.status = JINN_DONE
                self.agent.stop()

        elif self.agent.status == JINN_WAITING:
            offer = self.agent.sentOffers[-1]
            await self.offer(offer)
