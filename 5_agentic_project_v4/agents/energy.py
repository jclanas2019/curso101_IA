
class EnergyAgent:
    def run(self, context):
        insights = []
        for c in context:
            if "alto" in c:
                insights.append("Detectado sobreconsumo")
            if "pérdidas" in c:
                insights.append("Ineficiencia en sistema térmico")
        return insights
