
class AlertEngine:
    def check(self, insights):
        alerts=[]
        for i in insights:
            if "riesgo" in i.lower():
                alerts.append("⚠️ Riesgo financiero detectado")
            if "liquidez" in i.lower():
                alerts.append("⚠️ Problema de liquidez")
        return alerts
