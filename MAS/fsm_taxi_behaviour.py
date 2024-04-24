from enum import Enum
import random
from spade.behaviour import FSMBehaviour, State
import asyncio
from domain_and_roles import Role
from problem_constants import constants

class DriverState(Enum):
    SETUP = -1
    WAITING = 0
    PICKING_UP = 1
    ON_SERVICE = 2
    JOINING_QUEUE = 3
    RESTING = 4


class DriverFSMBehaviour(FSMBehaviour):
    async def on_start(self) -> None:
        self.current_state = DriverState.SETUP.name
        print(f"Driver {self.agent.jid.localpart} starting at initial state {self.current_state}")

class Setup(State):

    async def run(self) -> None:
        if self.agent.num_agents != self.agent.taxi_queue.len():
            await asyncio.sleep(5e-3)
            self.set_next_state(DriverState.SETUP.name)
        else:
            self.set_next_state(DriverState.WAITING.name)


class Waiting(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] waiting")
        await asyncio.sleep(constants['queue_waittime'])
        self.agent.add_worked_time(constants['queue_waittime'])

        print(f"[{self.agent.jid.localpart}] queue: {self.agent.taxi_queue.q}")

        async with self.agent.q_semaphore:
            if self.agent.taxi_queue.is_in_pickup_position(self.agent.jid.localpart):
                # simulate waiting for client
                print(f"[{self.agent.jid.localpart}] looking for clients")
                client_lookup_waittime = random.uniform(constants['client_waittime_lb'], constants['client_waittime_ub'])
                await asyncio.sleep(client_lookup_waittime)
                self.agent.add_worked_time(client_lookup_waittime)
                self.set_next_state(DriverState.PICKING_UP.name)
            else:
                done, _, _ = await self.agent.normative.perform("jump_queue")
                self.agent.num_consecutive_waits += 1 if not done else 0
                self.set_next_state(DriverState.PICKING_UP.name if done else DriverState.WAITING.name)
                

class PickingUp(State):

    async def run(self) -> None:
        self.agent.clients_at_sight = random.randint(1,6)
        print(f"[{self.agent.jid.localpart}] picking up state: {self.agent.clients_at_sight} clients")
        if random.random() > self.agent.reputation :#and self.agent.reputation < 0.6:
           print(f"Clients rejected {self.agent.jid.localpart} due to low reputation: {self.agent.reputation}")
           self.agent.num_jobs_lost += 1
           done = False
        else:
           done, _, _ = await self.agent.normative.perform('pick_clients')
        if not done:
            self.agent.clients_at_sight = 0
            self.agent.trip_duration = 0
            async with self.agent.q_semaphore:
                self.agent.taxi_queue.remove_from_queue(self.agent.jid.localpart)
            self.set_next_state(DriverState.JOINING_QUEUE.name)


class OnService(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] on service")
        #driving client to destination
        duration = random.uniform(constants['trip_lb'], constants['trip_ub'])
        await asyncio.sleep(duration)
        self.agent.set_trip_duration(duration)
        self.agent.add_worked_time(duration)
        self.set_next_state(DriverState.JOINING_QUEUE.name)


class JoiningQueue(State):
    
    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] joining queue")
        #returning from destination to queue
        return_duration = self.agent.trip_duration * 0.85
        await asyncio.sleep(return_duration)
        self.agent.add_worked_time(return_duration)
        self.agent.add_income()
        self.agent.set_trip_duration(0)

        done, _, _ = await self.agent.normative.perform('resume_work')
        if not done:
            self.agent.role = Role.RESTING_DRIVER
            self.set_next_state(DriverState.RESTING.name)


class Resting(State):

    async def run(self) -> None:
        print(f"[{self.agent.jid.localpart}] resting")
        done, _, _ = await self.agent.normative.perform('resume_work')
        if not done:
            lower_bound = min(constants['min_resting_time']-self.agent.current_rest_time, constants['rest_lb'])
            rest_time = random.uniform(lower_bound, constants['rest_ub'])
            await asyncio.sleep(rest_time)
            self.agent.rest(rest_time)
            self.agent.reset_worked_time()
            self.set_next_state(DriverState.RESTING.name)
