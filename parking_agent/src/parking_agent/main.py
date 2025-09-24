#!/usr/bin/env python
import sys
import warnings
import argparse
from datetime import datetime
from dotenv import load_dotenv

from parking_agent.crew import ParkingAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Load environment variables
load_dotenv()

def run():
    """
    Run the crew with parking search inputs.
    """
    # Default inputs for testing (Melbourne CBD area)
    inputs = {
        'latitude': -37.8136,
        'longitude': 144.9631,
        'radius': 500
    }

    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='Melbourne Parking Finder CLI')
        parser.add_argument('--latitude', '-lat', type=float, help='User latitude')
        parser.add_argument('--longitude', '-lon', type=float, help='User longitude')
        parser.add_argument('--radius', '-r', type=int, help='Search radius in meters')

        args, unknown = parser.parse_known_args()

        if args.latitude:
            inputs['latitude'] = args.latitude
        if args.longitude:
            inputs['longitude'] = args.longitude
        if args.radius:
            inputs['radius'] = args.radius

    try:
        print(f"Searching for parking spots within {inputs['radius']}m of ({inputs['latitude']}, {inputs['longitude']})...")
        result = ParkingAgent().crew().kickoff(inputs=inputs)
        print("\nParking search completed!")
        print(result)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def run_api():
    """
    Run the FastAPI server.
    """
    import uvicorn
    from parking_agent.api import app

    print("Starting Melbourne Parking Agent API server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Parking Finder Interface: http://localhost:8000")

    uvicorn.run("parking_agent.api:app", host="0.0.0.0", port=8000, reload=True)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'latitude': -37.8136,
        'longitude': 144.9631,
        'radius': 500
    }
    try:
        ParkingAgent().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ParkingAgent().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'latitude': -37.8136,
        'longitude': 144.9631,
        'radius': 500
    }

    try:
        ParkingAgent().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

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
