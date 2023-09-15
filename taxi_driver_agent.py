from spade.agent import Agent
from spade_norms.spade_norms import NormativeMixin
from fsm_taxi_behaviour import *

class TaxiDriverAgent(NormativeMixin, Agent):

    def __init__(self, queue = [], semaphore = None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.q_semaphore = semaphore
        self.clients_picked = 0
        self.worked_hours = 0
        self.current_rest_time = 0
        self.earned_money = 0
        self.fatigue = 0
        self.reputation = 50
        self.taxi_capacity = 5

        self.taxi_queue = queue
        self.taxi_queue.add_to_end_of_queue(self.jid.localpart)

    async def setup(self) -> None:
        fsmb = DriverFSMBehaviour()

        fsmb.add_state(name=DriverState.WAITING, state=Waiting(), initial=True)
        fsmb.add_state(name=DriverState.PICKING_UP, state=PickingUp())
        fsmb.add_state(name=DriverState.ON_SERVICE, state=OnService())
        fsmb.add_state(name=DriverState.AT_DESTINATION, state=AtDestination())
        fsmb.add_state(name=DriverState.RESTING, state=Resting())

        fsmb.add_transition(source=DriverState.WAITING, dest=DriverState.WAITING)
        fsmb.add_transition(source=DriverState.WAITING, dest=DriverState.PICKING_UP)
        fsmb.add_transition(source=DriverState.PICKING_UP, dest=DriverState.ON_SERVICE)
        fsmb.add_transition(source=DriverState.ON_SERVICE, dest=DriverState.AT_DESTINATION)
        fsmb.add_transition(source=DriverState.AT_DESTINATION, dest=DriverState.WAITING)
        fsmb.add_transition(source=DriverState.AT_DESTINATION, dest=DriverState.RESTING)
        fsmb.add_transition(source=DriverState.RESTING, dest=DriverState.WAITING)
        fsmb.add_transition(source=DriverState.RESTING, dest=DriverState.RESTING)

        self.add_behaviour(fsmb)
