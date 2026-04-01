
class AnswerAgent:
    def run(self,q,ctx,insights):
        out="Análisis financiero:\n"
        out+="\nDatos:\n- " + "\n- ".join(ctx)
        out+="\nInsights:\n- " + "\n- ".join(insights)
        return out
