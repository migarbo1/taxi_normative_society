import threading
from spade.agent import Agent
from spade_norms.spade_norms import NormativeMixin
from fsm_taxi_behaviour import *
from problem_constants import *
import asyncio
import math


FATIGUE_CONVERSION = 8


class TaxiDriverAgent(NormativeMixin, Agent):

    def __init__(self, queue = [], semaphore = None, num_agents=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.q_semaphore = semaphore
        self.num_agents = num_agents
        
        self.earned_money = 0
        self.fatigue = 0
        self.reputation = 0.85

        self.total_time = 0
        self.worked_time = 0
        self.current_rest_time = 0
        self.trip_duration = 0

        self.taxi_capacity = 4
        self.clients_picked = 0
        self.clients_at_sight = 0
        self.sucessful_pickup_count = 0

        self.num_consecutive_waits = 0
        
        self.num_jobs_lost = 0

        self.taxi_queue = queue
        


    async def setup(self) -> None:
        fsmb = DriverFSMBehaviour()

        fsmb.add_state(name=DriverState.SETUP.name, state=Setup(), initial=True)
        fsmb.add_state(name=DriverState.WAITING.name, state=Waiting())
        fsmb.add_state(name=DriverState.PICKING_UP.name, state=PickingUp())
        fsmb.add_state(name=DriverState.ON_SERVICE.name, state=OnService())
        fsmb.add_state(name=DriverState.JOINING_QUEUE.name, state=JoiningQueue())
        fsmb.add_state(name=DriverState.RESTING.name, state=Resting())

        fsmb.add_transition(source=DriverState.SETUP.name, dest=DriverState.SETUP.name)
        fsmb.add_transition(source=DriverState.SETUP.name, dest=DriverState.WAITING.name)
        fsmb.add_transition(source=DriverState.WAITING.name, dest=DriverState.WAITING.name)
        fsmb.add_transition(source=DriverState.WAITING.name, dest=DriverState.PICKING_UP.name)
        fsmb.add_transition(source=DriverState.PICKING_UP.name, dest=DriverState.ON_SERVICE.name)
        fsmb.add_transition(source=DriverState.PICKING_UP.name, dest=DriverState.JOINING_QUEUE.name)
        fsmb.add_transition(source=DriverState.ON_SERVICE.name, dest=DriverState.JOINING_QUEUE.name)
        fsmb.add_transition(source=DriverState.JOINING_QUEUE.name, dest=DriverState.WAITING.name)
        fsmb.add_transition(source=DriverState.JOINING_QUEUE.name, dest=DriverState.RESTING.name)
        fsmb.add_transition(source=DriverState.RESTING.name, dest=DriverState.WAITING.name)
        fsmb.add_transition(source=DriverState.RESTING.name, dest=DriverState.RESTING.name)

        self.add_behaviour(fsmb)


    def join_queue_first_time(self):
        self.taxi_queue.add_to_end_of_queue(self.jid.localpart)


    def set_trip_duration(self, duration):
        self.trip_duration = duration


    def add_worked_time(self, amount):
        self.total_time += amount
        self.worked_time += amount
        self.accumulate_fatigue(amount)


    def add_income(self):
        applied_tax = 0
        applied_fare = 0
        if self.trip_duration > 0:
            # Long local trip
            if self.trip_duration < constants['long_local_trip_time']:
                applied_tax = 2.3
                applied_fare = constants['long_local_trip_fare']
            # Local trip
            if self.trip_duration <= constants['short_local_trip_time']: 
                applied_tax = 1.15
                applied_fare = constants['short_local_trip_fare']
            # Intercity
            if self.trip_duration >= constants['intercity_trip_time']:
                applied_tax = 2.3
                applied_fare = constants['intercity_trip_fare']

            self.earned_money += (applied_tax + self.trip_duration * 1000 * applied_fare)


    def reset_worked_time(self):
        self.worked_time = 0


    def reset_rest_time(self):
        self.current_rest_time = 0


    def increase_reputation(self, amount):
        self.reputation = min(1, self.reputation + amount)


    def decrease_reputation(self, amount):
        self.reputation = max(0, self.reputation - amount)


    def get_working_will(self):
        money_per_time = compute_expected_money_per_job()/compute_expected_time_per_job()
        if self.total_time == 0:
            return 1
        
        return 1 - self.earned_money/(self.total_time*1000*money_per_time)


    def rest(self, amount):
        self.total_time += amount
        self.current_rest_time += amount
        self.fatigue -= (amount/constants['min_resting_time'])*0.65
        self.fatigue = max(0, self.fatigue)


    def accumulate_fatigue(self, amount):
        
        actual_fatigue = amount/(12*60*1e-3)
        self.fatigue += actual_fatigue
        self.fatigue = min(1, self.fatigue)
