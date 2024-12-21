import subprocess
import sys

# Fetch the fraction value from command-line arguments
fraction = sys.argv[1]

def execute_script(script_path, arg=None):
    try:
        if arg is not None:
            subprocess.run(["python", script_path, arg], check=True)
        else:
            subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_path}: {e}")
    except FileNotFoundError:
        print(f"Python interpreter not found. Make sure Python is installed correctly.")

if __name__ == "__main__":
    scripts = [
        f"Stage1_GetScopusID.py",
        f"Stage2_GetScivalData.py",
        f"Stage3_Merge.py",
        f"Stage4_Combine.py"
    ]

    print("Begin Pipeline Execution")

    for i, script in enumerate(scripts):
        print(f"Executing script: {script}")
        # Pass the argument for Script1 only
        if i == 0:
            if fraction is not None:
                execute_script(script, fraction)  # Pass the desired argument for Script1
            else:
                execute_script(script,1)
        else:
            execute_script(script)
        print(f"Script execution completed: {script}")

    print("Pipeline Executed Successfully - All 4 Stages")
