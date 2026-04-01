
class AnswerAgent:
    def run(self, query, context, analysis):
        out = "Diagnóstico energético:\n"
        if context:
            out += "\nDatos:\n- " + "\n- ".join(context)
        if analysis:
            out += "\nInsights:\n- " + "\n- ".join(analysis)
        if not context:
            out += "\nNo hay datos suficientes"
        return out
