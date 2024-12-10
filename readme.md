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

## Using main.py

To use `main.py`, follow these steps:

1. **Specify a Character Model:**

   You need to select a character model FBX file to be used in the animation processing. You have two options:

   - **Option 1: Use the default Ready Player Me avatar (avatar1):**
     - Place the `avatar1.fbx` file in the `avatar` folder located in the project directory.
     - When prompted to select the character model file, navigate to the `avatar` folder and select `avatar1.fbx`.

   - **Option 2: Use a custom avatar:**
     - Place your custom avatar FBX file in the `avatar` folder located in the project directory.
     - When prompted to select the character model file, navigate to the `avatar` folder and select your custom avatar FBX file.

2. **Run the Script:**

   - Open a terminal or command prompt and navigate to the project directory.
   - Ensure the virtual environment is activated.
   - Run the script by executing:
     ```sh
     python main.py
     ```

3. **Follow the Prompts:**

   - You will be prompted to select the FBX input directory containing the animation files.
   - You will also be prompted to select the output directory where the processed files will be saved.

4. **Processing:**

   - The script will process the animations, generate GIFs, convert them to WebP format, create 8K grids, and run the OpenAI parser to generate metadata.
   - The output files, including the processed animations and metadata, will be saved in the specified output directory.

By following these steps, you can use `main.py` to process animations with your specified character model.
