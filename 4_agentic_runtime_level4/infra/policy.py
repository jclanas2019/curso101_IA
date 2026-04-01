
class PolicyEngine:
    def allow(self, task):
        blocked = ["rm -rf", "shutdown", "reboot"]
        return not any(b in task for b in blocked)
