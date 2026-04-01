
class Planner:
    def plan(self, query):
        q = query.lower()
        steps = ["retrieval"]

        if "energ" in q or "consumo" in q:
            steps.append("energy")

        steps.append("answer")
        return steps
