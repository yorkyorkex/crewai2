#!/usr/bin/env python
import sys
import warnings
import argparse
from datetime import datetime
from dotenv import load_dotenv

from travel_planner2.crew import TravelPlanner2

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Load environment variables
load_dotenv()

def run():
    """
    Run the crew with travel planning inputs.
    """
    # Default inputs for testing
    inputs = {
        'destination': 'Tokyo, Japan',
        'duration': 3
    }

    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='Travel Planner CLI')
        parser.add_argument('--destination', '-d', type=str, help='Travel destination')
        parser.add_argument('--duration', '-t', type=int, help='Trip duration in days')
        parser.add_argument('--preferences', '-p', type=str, help='Travel preferences')

        args, unknown = parser.parse_known_args()

        if args.destination:
            inputs['destination'] = args.destination
        if args.duration:
            inputs['duration'] = args.duration
        if args.preferences:
            inputs['preferences'] = args.preferences

    try:
        print(f"🌍 Planning a {inputs['duration']}-day trip to {inputs['destination']}...")
        result = TravelPlanner2().crew().kickoff(inputs=inputs)
        print("\n✅ Travel plan completed! Check the 'travel_guide.md' file for your itinerary.")
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def run_api():
    """
    Run the FastAPI server.
    """
    import uvicorn
    from travel_planner2.api import app

    print("🚀 Starting Travel Planner API server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🌐 API Interface: http://localhost:8000")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "destination": "Paris, France",
        "duration": 5
    }
    try:
        TravelPlanner2().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        TravelPlanner2().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "destination": "London, UK",
        "duration": 4
    }

    try:
        TravelPlanner2().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def main():
    """
    Main entry point with mode selection.
    """
    if len(sys.argv) > 1 and sys.argv[1] == 'api':
        run_api()
    else:
        run()

if __name__ == "__main__":
    main()
