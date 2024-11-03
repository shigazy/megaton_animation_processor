## Setting Up the Virtual Environment

To set up the virtual environment, follow these steps:

1. **Create the virtual environment:**

   Open a terminal or command prompt and navigate to your project directory. Then, run the following command to create a virtual environment called `venv_new`:

   ```sh
   python -m venv venv_new
   ```

2. **Activate the virtual environment:**

   - On Windows, run:
     ```sh
     .\venv_new\Scripts\activate
     ```
   - On macOS and Linux, run:
     ```sh
     source venv_new/bin/activate
     ```

3. **Install the required packages:**

   Once the virtual environment is activated, install the necessary packages by running:
   ```sh
   pip install -r requirements.txt
   ```

## Running the Script

To run the script, simply click on `ingest_animation.bat`. This batch file will handle the execution of the script within the virtual environment.

Make sure the virtual environment is activated before running the batch file to ensure all dependencies are correctly loaded.
