import time
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


class ManagerAgent(Agent):
    async def setup(self):
        pass


class AlternatingOffersBehavior(CyclicBehaviour):
    async def on_start(self):
        pass

    async def run(self):
        pass

    async def on_end(self):
        pass
