
class Planner:
    def plan(self, q):
        steps=["retrieval"]
        if "balance" in q.lower() or "financ" in q.lower():
            steps.append("financial")
        steps.append("answer")
        return steps
