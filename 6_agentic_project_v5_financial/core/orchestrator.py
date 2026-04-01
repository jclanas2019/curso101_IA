
class Orchestrator:
    def __init__(self, registry, planner, memory, tracer, alerts):
        self.registry=registry; self.planner=planner
        self.memory=memory; self.tracer=tracer; self.alerts=alerts

    def run(self, q):
        self.memory.add("user", q)
        plan=self.planner.plan(q)
        self.tracer.log("plan", plan)

        ctx=[]; insights=[]; result=None

        for step in plan:
            agent=self.registry.get(step)
            if step=="retrieval":
                ctx=agent.run(q); self.tracer.log("retrieval",ctx)
            elif step=="financial":
                insights=agent.run(ctx); self.tracer.log("financial",insights)
            elif step=="answer":
                result=agent.run(q,ctx,insights); self.tracer.log("answer",result)

        alerts=self.alerts.check(insights)
        self.memory.add("assistant", result)
        return result, alerts
