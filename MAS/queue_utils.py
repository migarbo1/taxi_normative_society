class TaxiQueue():
    def __init__(self):
        self.q = []

    def is_in_pickup_position(self, jid):
        return self.get_queue_pos(jid) == 0

    def get_queue_pos(self, jid):
        return self.q.index(jid)

    def remove_from_queue(self, jid):
        pos = self.get_queue_pos(jid)
        return self.q.pop(pos)
    
    def add_to_end_of_queue(self, jid):
        self.q.append(jid)

    def add_to_start_of_queue(self, jid):
        self.q.insert(0, jid)

    def len(self):
        return len(self.q)