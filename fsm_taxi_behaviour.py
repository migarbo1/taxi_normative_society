from enum import Enum
import random
from spade.behaviour import FSMBehaviour, State
import asyncio
import queue_utils as qu


class DriverState(Enum):
    WAITING = 0
    PICKING_UP = 1
    ON_SERVICE = 2
    AT_DESTINATION = 3
    RESTING = 4


class DriverFSMBehaviour(FSMBehaviour):
    async def on_start(self) -> None:
        self.current_state = DriverState.WAITING
        print(f"Driver {self.agent.jid.localpart} starting at initial state {self.current_state}")


class Waiting(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] waiting")
        await asyncio.sleep(random.randint(1,2))

        print(f"[{self.agent.jid.localpart}] queue: {self.agent.taxi_queue.q}")

        async with self.agent.q_semaphore:
            if self.agent.taxi_queue.is_in_pickup_position(self.agent.jid.localpart):
                # simulate waiting for client
                print(f"[{self.agent.jid.localpart}] looking for clients")
                await asyncio.sleep(random.randint(2, 4))
                #TODO: dynamic client num
                #TODO: max capacity
                self.set_next_state(DriverState.PICKING_UP)
            else:
                if True: #TODO: jumping condition
                    await self.agent.normative.perform("jump_queue", self.agent)
                else:
                    self.set_next_state(DriverState.WAITING)
                self.set_next_state(DriverState.WAITING)


class PickingUp(State):

    async def run(self) -> None:
        async with self.agent.q_semaphore:
            print(f"[{self.agent.jid.localpart}] picking up")
            self.agent.taxi_queue.remove_from_queue(self.agent.jid.localpart)
            self.set_next_state(DriverState.ON_SERVICE)


class OnService(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] on service")
        duration = random.randint(4, 7)
        await asyncio.sleep(duration)
        self.agent.worked_hours += duration
        self.set_next_state(DriverState.AT_DESTINATION)


class AtDestination(State):
    
    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] at destination")
        duration = random.randint(3, 5)
        await asyncio.sleep(duration)
        self.agent.worked_hours += duration
        self.agent.earned_money += 5 #TODO: price depending on client number
        
        #TODO: replace with working hours Norm
        if self.agent.worked_hours >= 30:
            self.set_next_state(DriverState.RESTING)
        else:
            async with self.agent.q_semaphore:
                self.agent.taxi_queue.add_to_end_of_queue(self.agent.jid.localpart)
                self.set_next_state(DriverState.WAITING)


class Resting(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] resting")
        await asyncio.sleep(3)
        async with self.agent.q_semaphore:
            self.agent.taxi_queue.add_to_end_of_queue(self.agent.jid.localpart)
            self.set_next_state(DriverState.WAITING)
