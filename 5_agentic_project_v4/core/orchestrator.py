
class Orchestrator:
    def __init__(self, registry, planner, memory, tracer):
        self.registry = registry
        self.planner = planner
        self.memory = memory
        self.tracer = tracer

    def run(self, query):
        self.memory.add("user", query)
        plan = self.planner.plan(query)
        self.tracer.log("plan", plan)

        context, analysis, result = [], [], None

        for step in plan:
            agent = self.registry.get(step)

            if step == "retrieval":
                context = agent.run(query)
                self.tracer.log("retrieval", context)

            elif step == "energy":
                analysis = agent.run(context)
                self.tracer.log("energy_analysis", analysis)

            elif step == "answer":
                result = agent.run(query, context, analysis)
                self.tracer.log("answer", result)

        self.memory.add("assistant", result)
        return result
