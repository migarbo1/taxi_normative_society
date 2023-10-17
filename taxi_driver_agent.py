from spade.agent import Agent
from spade_norms.spade_norms import NormativeMixin
from fsm_taxi_behaviour import *


FATIGUE_CONVERSION = 8


class TaxiDriverAgent(NormativeMixin, Agent):

    def __init__(self, queue = [], semaphore = None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.q_semaphore = semaphore
        
        self.earned_money = 0
        self.fatigue = 0
        self.reputation = 0.85

        self.fatigue_ratio = 1
        self.recovery_ratio = 1.6

        self.worked_time = 0
        self.current_rest_time = 0
        self.trip_duration = 0

        self.taxi_capacity = 4
        self.clients_picked = 0
        self.clients_at_sight = 0

        self.taxi_queue = queue
        self.taxi_queue.add_to_end_of_queue(self.jid.localpart)


    async def setup(self) -> None:
        fsmb = DriverFSMBehaviour()

        fsmb.add_state(name=DriverState.WAITING, state=Waiting(), initial=True)
        fsmb.add_state(name=DriverState.PICKING_UP, state=PickingUp())
        fsmb.add_state(name=DriverState.ON_SERVICE, state=OnService())
        fsmb.add_state(name=DriverState.JOINING_QUEUE, state=JoiningQueue())
        fsmb.add_state(name=DriverState.RESTING, state=Resting())

        fsmb.add_transition(source=DriverState.WAITING, dest=DriverState.WAITING)
        fsmb.add_transition(source=DriverState.WAITING, dest=DriverState.PICKING_UP)
        fsmb.add_transition(source=DriverState.PICKING_UP, dest=DriverState.ON_SERVICE)
        fsmb.add_transition(source=DriverState.PICKING_UP, dest=DriverState.JOINING_QUEUE)
        fsmb.add_transition(source=DriverState.ON_SERVICE, dest=DriverState.JOINING_QUEUE)
        fsmb.add_transition(source=DriverState.JOINING_QUEUE, dest=DriverState.WAITING)
        fsmb.add_transition(source=DriverState.JOINING_QUEUE, dest=DriverState.RESTING)
        fsmb.add_transition(source=DriverState.RESTING, dest=DriverState.WAITING)
        fsmb.add_transition(source=DriverState.RESTING, dest=DriverState.RESTING)

        self.add_behaviour(fsmb)


    def set_trip_duration(self, duration):
        self.trip_duration = duration


    def add_worked_time(self, amount):
        self.worked_time += amount
        #TODO
        self.fatigue = self.worked_time * FATIGUE_CONVERSION * self.fatigue_ratio


    def rest(self, amount):
        self.current_rest_time += amount
        # TODO
        self.fatigue = min(0, self.fatigue - self.current_rest_time * self.recovery_ratio)


    def add_income(self):
        applied_tax = 0
        applied_fare = 0
        # Long local trip
        if self.worked_time < 70e-3:
            applied_tax = 2.3
            applied_fare = 0.41
        # Local trip
        if self.worked_time <= 50e-3: 
            applied_tax = 1.15
            applied_fare = 0.36
        # Intercity
        if self.worked_time >= 70e-3:
            applied_tax = 2.3
            applied_fare = 0.28

        self.earned_money += (applied_tax + self.worked_time * 1000 * applied_fare)


    def reset_worked_time(self):
        self.worked_time = 0


    def reset_rest_time(self):
        self.current_rest_time = 0


    def increase_reputation(self, amount):
        self.reputation = min(1, self.reputation + amount)


    def decrease_reputation(self, amount):
        self.reputation = max(0, self.reputation - amount)