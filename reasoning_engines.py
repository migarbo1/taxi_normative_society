from spade.agent import Agent
from spade_norms.engines.reasoning_engine import NormativeReasoningEngine
from spade_norms.norms.normative_response import NormativeResponse 
from spade_norms.norms.norm_enums import NormativeActionStatus

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
            
        
