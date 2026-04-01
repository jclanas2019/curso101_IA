from core.query_engine import QueryEngine

if __name__ == "__main__":
    engine = QueryEngine()
    while True:
        user_input = input(">> ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = engine.run(user_input)
        print(response)
