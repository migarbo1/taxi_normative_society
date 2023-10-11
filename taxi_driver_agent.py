from spade.agent import Agent
from spade_norms.spade_norms import NormativeMixin
from fsm_taxi_behaviour import *


HOUR_CONVERSION = 5
FATIGUE_CONVERSION = 8


class TaxiDriverAgent(NormativeMixin, Agent):

    def __init__(self, queue = [], semaphore = None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.q_semaphore = semaphore
        
        self.earned_money = 0
        self.fatigue = 0
        self.reputation = 85

        self.fatigue_ratio = 1
        self.recovery_ratio = 1.6

        self.worked_hours = 0
        self.current_rest_time = 0

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


    def add_worked_hours(self, amount):
        self.worked_hours += float(amount) / HOUR_CONVERSION
        self.fatigue = self.worked_hours * FATIGUE_CONVERSION * self.fatigue_ratio


    def rest(self):
        self.current_rest_time += 10
        self.fatigue = min(0, self.fatigue - self.current_rest_time * self.recovery_ratio)


    def reset_worked_hours(self):
        self.worked_hours = 0


    def reset_rest_time(self):
        self.current_rest_time = 0