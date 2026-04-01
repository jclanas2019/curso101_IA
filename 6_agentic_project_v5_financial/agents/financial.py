
class FinancialAgent:
    def run(self,ctx):
        insights=[]
        for c in ctx:
            if "decrec" in c: insights.append("Riesgo de ingresos")
            if "costos" in c: insights.append("Estructura de costos ineficiente")
            if "flujo" in c: insights.append("Problema de liquidez")
        return insights
