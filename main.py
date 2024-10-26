import argparse
import subprocess
import logging
from pathlib import Path
import os

def run_script(script_name):
    """Run a Python script using os.system."""
    logging.info(f"Running scripts/{script_name}...")
    try:
        command = f"python -u {script_name}"
        result = os.system(command)
        
        if result != 0:
            raise subprocess.CalledProcessError(result, script_name)
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running {script_name}: {e}")
        raise

def ensure_directories_exist():
    """Ensure all necessary directories exist."""
    directories = [
        'data/raw',
        'data/processed',
        'data/results',
        'src/utils',
        'src/models',
        'src/config',
        'scripts'
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Run the AI bias assessment project pipeline.")
    parser.add_argument('--skip-input-generation', action='store_true', help="Skip input generation step")
    parser.add_argument('--skip-response-generation', action='store_true', help="Skip response generation step")
    args = parser.parse_args()

    ensure_directories_exist()

    if not args.skip_input_generation:
        run_script('scripts/generate_inputs.py')
    else:
        logging.info("Skipping input generation step.")

    if not args.skip_response_generation:
        run_script('scripts/generate_responses.py')
    else:
        logging.info("Skipping response generation step.")

    run_script('scripts/analyze_results.py')

    logging.info("Project pipeline completed successfully.")

if __name__ == "__main__":
    main()