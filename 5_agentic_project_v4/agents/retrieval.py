
class RetrievalAgent:
    def run(self, query):
        data = [
            "Consumo energético alto en horas peak",
            "Sistemas de refrigeración tienen pérdidas",
            "Optimización reduce costos hasta 20%"
        ]
        return [d for d in data if any(w in d.lower() for w in query.lower().split())]
