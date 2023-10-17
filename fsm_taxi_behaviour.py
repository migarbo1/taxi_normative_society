from enum import Enum
import random
from spade.behaviour import FSMBehaviour, State
import asyncio
from domain_and_roles import Role
from norms import RESTING_MINS

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
        queue_waittime = 10e-3
        await asyncio.sleep(queue_waittime)
        self.agent.add_worked_time(queue_waittime)

        print(f"[{self.agent.jid.localpart}] queue: {self.agent.taxi_queue.q}")

        async with self.agent.q_semaphore:
            if self.agent.taxi_queue.is_in_pickup_position(self.agent.jid.localpart):
                # simulate waiting for client
                print(f"[{self.agent.jid.localpart}] looking for clients")
                client_lookup_waittime = random.uniform(5e-3, 15e-3)
                await asyncio.sleep(client_lookup_waittime)
                self.agent.add_worked_time(client_lookup_waittime)
                self.set_next_state(DriverState.PICKING_UP)
            else:
                # TODO: logic for when to jump queue. For now by default is always tried
                done, _, _ = await self.agent.normative.perform("jump_queue")
                if not done:
                    self.set_next_state(DriverState.WAITING)
                

class PickingUp(State):

    async def run(self) -> None:
        self.agent.clients_at_sight = random.randint(1,6)
        print(f"[{self.agent.jid.localpart}] picking up state: {self.agent.clients_at_sight} clients")
        if random.random() > self.agent.reputation and self.agent.reputation < 0.60:
            print(f"Clients rejected {self.agent.jid.localpart} due to low reputation: {self.agent.reputation}")
            done = False
        else:
            done, _, _ = await self.agent.normative.perform('pick_clients')
        if not done:
            self.agent.clients_at_sight = 0
            async with self.agent.q_semaphore:
                self.agent.taxi_queue.remove_from_queue(self.agent.jid.localpart)
            self.set_next_state(DriverState.JOINING_QUEUE)


class OnService(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] on service")
        #driving client to destination
        duration = random.uniform(30e-3, 90e-3)
        await asyncio.sleep(duration)
        self.agent.set_trip_duration(duration)
        self.agent.add_worked_time(duration)
        self.set_next_state(DriverState.JOINING_QUEUE)


class JoiningQueue(State):
    
    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] joining queue")
        #returning from destination to queue
        return_duration = self.agent.trip_duration * 0.85
        await asyncio.sleep(return_duration)
        self.agent.add_worked_time(return_duration)
        self.agent.add_income()

        done, _, _ = await self.agent.normative.perform('resume_work')
        if not done:
            self.agent.role = Role.RESTING_DRIVER
            self.set_next_state(DriverState.RESTING)


class Resting(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] resting")
        done, _, _ = await self.agent.normative.perform('resume_work')
        if not done:
            upper_bound = 15e-3
            lower_bound = min(RESTING_MINS-self.agent.current_rest_time, 5e-3)
            rest_time = random.uniform(lower_bound, upper_bound)
            await asyncio.sleep(rest_time)
            self.agent.rest(rest_time)
            self.agent.reset_worked_time()
            self.set_next_state(DriverState.RESTING)
