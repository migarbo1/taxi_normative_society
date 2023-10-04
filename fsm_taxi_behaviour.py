from enum import Enum
import random
from spade.behaviour import FSMBehaviour, State
import asyncio
from domain_and_roles import Role

class DriverState(Enum):
    WAITING = 0
    PICKING_UP = 1
    ON_SERVICE = 2
    JOINING_QUEUE = 3
    RESTING = 4


class DriverFSMBehaviour(FSMBehaviour):
    async def on_start(self) -> None:
        self.current_state = DriverState.WAITING
        print(f"Driver {self.agent.jid.localpart} starting at initial state {self.current_state}")


class Waiting(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] waiting")
        queue_waittime = random.randint(1,2)
        await asyncio.sleep(queue_waittime)
        self.agent.add_worked_hours(queue_waittime)

        print(f"[{self.agent.jid.localpart}] queue: {self.agent.taxi_queue.q}")

        async with self.agent.q_semaphore:
            if self.agent.taxi_queue.is_in_pickup_position(self.agent.jid.localpart):
                # simulate waiting for client
                print(f"[{self.agent.jid.localpart}] looking for clients")
                client_lookup_waittime = random.randint(2, 4)
                await asyncio.sleep(client_lookup_waittime)
                self.agent.add_worked_hours(client_lookup_waittime)
                self.set_next_state(DriverState.PICKING_UP)
            else:
                # TODO: logic for when to jump queue. For now by default is always tried
                done, _, _ = await self.agent.normative.perform("jump_queue")
                if not done:
                    self.set_next_state(DriverState.WAITING)
                

class PickingUp(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] picking up state")
        self.agent.clients_at_sight = random.randint(1,10)
        done, _, _ = await self.agent.normative.perform('pick_clients')
        if not done:
            async with self.agent.q_semaphore:
                self.agent.taxi_queue.remove_from_queue(self.agent.jid.localpart)
            self.set_next_state(DriverState.JOINING_QUEUE)


class OnService(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] on service")
        duration = random.randint(4, 7)
        await asyncio.sleep(duration)
        self.agent.add_worked_hours(duration)
        self.set_next_state(DriverState.JOINING_QUEUE)


class JoiningQueue(State):
    
    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] joining queue")
        duration = random.randint(3, 5)
        await asyncio.sleep(duration)
        self.agent.add_worked_hours(duration)
        self.agent.earned_money += 2 * self.agent.clients_picked

        done, _, _ = await self.agent.normative.perform('resume_work')
        if not done:
            self.agent.role = Role.RESTING_DRIVER
            self.set_next_state(DriverState.RESTING)


class Resting(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] resting")
        done, _, _ = await self.agent.normative.perform('resume_work')
        if not done:
            await asyncio.sleep(1)
            self.agent.rest()
            self.agent.reset_worked_hours()
            self.set_next_state(DriverState.RESTING)
