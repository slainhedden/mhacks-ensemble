from agent import AgentTeam

def main():
    team = AgentTeam()
    
    goals = [
        "Develop a marketing strategy for a new product",
        "Create a budget for the next fiscal year",
        "Design a new user interface for our mobile app"
    ]
    
    for goal in goals:
        print(f"\nProcessing goal: {goal}")
        results = team.process_goal(goal)
        
        for result in results:
            print(f"Agent: {result['agent_name']} ({result['agent_role']})")
            print(f"Response: {result['response']}")
            print("-" * 50)

if __name__ == "__main__":
    main()