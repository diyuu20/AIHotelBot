Step-by-Step Guide to Run the AI Hotel Bot
This guide provides all the necessary steps to set up the project environment, install dependencies, prepare the required data, and run the Flask application.
Step 1: Prerequisites
    Before you begin, ensure you have the following software installed on your computer:
    Python: Make sure you have Python 3.8 or newer installed. You can download it from python.org.
    Tesseract-OCR: This is a crucial dependency for the document scanning (OCR) part of the project.
    Windows: Download and run the installer from here. During installation, make sure to check the option to add Tesseract to your system's PATH. The default installation path is usually C:\Program Files\Tesseract-OCR\tesseract.exe, which is what the script expects.
    macOS: Use Homebrew: brew install tesseract
    Linux (Ubuntu/Debian): sudo apt-get install tesseract-ocr
Step 2: Create a Virtual Environment
    It is highly recommended to use a virtual environment to keep the project's dependencies isolated.
    Open your terminal or command prompt.
    Navigate to your main project folder (AIHOTELBOT).
    Run the following command to create a virtual environment (we'll call it hotelbot):
        python -m venv hotelbot


Activate the virtual environment:
On Windows:
.\hotelbot\Scripts\activate


On macOS and Linux:
source hotelbot/bin/activate


You will know it's active when you see (hotelbot) at the beginning of your terminal prompt.
Step 3: Install All Required Libraries
With your virtual environment still active, run the following command to install all the necessary Python libraries at once:
pip install -r requirements.txt




Step: Run the Application
You are now ready to start the hotel bot!
In your terminal (with the virtual environment still active), run the main application file:
python app.py


You will see output indicating that the server is running, similar to this:
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://192.168.1.X:5000/ (Press CTRL+C to quit)


To access the bot:
On the same computer: Open a web browser and go to http://127.0.0.1:5000.
On other devices (like a phone or tablet): Make sure the device is connected to the same Wi-Fi network as your computer. Open a web browser and go to the URL shown in your terminal (e.g., http://192.168.1.X:5000).
You should now see the main page with the "Check-In," "Check-Out," and "Book a Room" buttons, and the application will be fully functional.
