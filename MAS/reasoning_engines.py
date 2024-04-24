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
            return False
            
        return norm_response.response_type == NormativeActionStatus.ALLOWED or norm_response.response_type == NormativeActionStatus.NOT_REGULATED
            
        
class ComplexMoneyDrivenReasoningEngine(NormativeReasoningEngine):

    def inference(self, agent: Agent, norm_response: NormativeResponse):
        if norm_response.response_type == NormativeActionStatus.FORBIDDEN or norm_response.response_type == NormativeActionStatus.INVIOLABLE:
    
            if norm_response.action.name == 'pick_clients':
                return False

            if norm_response.action.name == 'jump_queue':
                will = 1 - math.pow(0.95, agent.num_consecutive_waits)
                return agent.reputation > 0.20 and random.random() < will
            
            if norm_response.action.name == 'resume_work':
                return agent.reputation > 0.20 and agent.get_working_will() > agent.fatigue

        return True
