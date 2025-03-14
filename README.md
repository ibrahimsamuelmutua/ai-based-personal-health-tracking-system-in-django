# installation
  1. Create a virtual environment
   - python -m venv virtual
 
  2. Activate the virtual environment
   - source virtual/Scripts/activate
 
  3. Install the project's dependencies
   - pip install -r requirements.txt
  
  4. Apply migrations
   - python manage.py migrate
  
  5. Start the Development Server
    - python manage.py runserver
  
  6. Access the Application
    -Once the server is running, open the following URL in your browser: http://127.0.0.1:8000/ 
