from spade.agent import Agent
from spade_norms.engines.reasoning_engine import NormativeReasoningEngine
from spade_norms.norms.normative_response import NormativeResponse 
from spade_norms.norms.norm_enums import NormativeActionStatus
from problem_constants import *
import random
import math

class MoneyDrivenReasoningEngine(NormativeReasoningEngine):

    def inference(self, agent: Agent, norm_response: NormativeResponse):
        if norm_response.action.name == 'jump_queue':
            if agent.earned_money < 15 and agent.worked_time >= 6:
                return True
            
        if norm_response.action.name == 'resume_work':
            if agent.earned_money < 25 and agent.fatigue < 75:
                return True
            
        if norm_response.action.name == 'pick_clients':
            if agent.earned_money < 8 and agent.worked_time >= 12:
                return True
            
        return norm_response.response_type == NormativeActionStatus.ALLOWED or norm_response.response_type == NormativeActionStatus.NOT_REGULATED
            
        
class ComplexMoneyDrivenReasoningEngine(NormativeReasoningEngine):

    def inference(self, agent: Agent, norm_response: NormativeResponse):
        if norm_response.response_type == NormativeActionStatus.FORBIDDEN or norm_response.response_type == NormativeActionStatus.INVIOLABLE:
    
            if norm_response.action.name == 'pick_clients':
                return random.random() < (math.pow(math.e, agent.total_time/1000) / math.pow(math.e, constants['simulation_time'])) * (1 - agent.earned_money/get_max_possible_money())

            if norm_response.action.name == 'jump_queue':
                print(f'[{agent.jid.localpart}] jumping queue willingness:', (1 - math.pow(math.e, (agent.sucessful_pickup_count * compute_expected_time_per_job())) / math.pow(math.e, agent.total_time/1000)))
                return random.random() < (1 - math.pow(math.e, (agent.sucessful_pickup_count * compute_expected_time_per_job())/1000) / math.pow(math.e, agent.total_time/1000))
            
            if norm_response.action.name == 'resume_work':
                print(f'[{agent.jid.localpart}] deciding if returning to work')
                print(f'[{agent.jid.localpart}] working will:', agent.get_working_will())
                print(f'[{agent.jid.localpart}] Fatigue:', agent.fatigue)
                return agent.get_working_will() > agent.fatigue

        return True
