class FileTool:
    def run(self, path: str):
        try:
            with open(path.strip(), "r") as f:
                return f.read()
        except Exception as e:
            return str(e)
