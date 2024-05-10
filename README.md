# Horizon marketplace

## Installation

Follow these steps to set up the Horizon marketplace project on your local machine.

### Prerequisites

- [Python](https://www.python.org/) (version 3.6 or higher)
- [pip](https://pip.pypa.io/en/stable/)
- [Virtualenv](https://virtualenv.pypa.io/en/stable/)
- [PostgreSQL](https://www.postgresql.org/) (installed and running)

### Steps

1. **Clone the Repository:**

   ```bash
   git clone [https://github.com/shilpacvenugopal/horizon.git]
   cd horizon
   ```

2. **Create a Virtual Environment:**

   ```bash
   virtualenv venv
   ```

3. **Activate the Virtual Environment:**

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Database:**

   - Create .env file
    ```bash
   touch .env
   ```
   - copy content in .env_example file and make neccessary changes
   - Here used database url for connection with database can also use:
    ```bash
           DATABASES = {
          'default': {
              'ENGINE': 'django.db.backends.postgresql',
              'NAME': os.getenv('NAME')  
              'USER': os.getenv('USER')
              'PASSWORD':os.getenv('PASSWORD')
              'HOST': os.getenv('HOST')
              'PORT':os.getenv('PORT')
          }
         }
      ```

     Then add this part in setting.py and also add this details in the .env file also.
     
7. **Run Migrations:**

   ```bash
   python manage.py migrate
   ```

8. **Create Superuser (Admin User):**

   ```bash
   python manage.py createsuperuser
   ```

   Follow the prompts to create an admin user.

9. **Run the Development Server:**

   ```bash
   python manage.py runserver
   ```

   The project will be accessible at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).


10. **Access the Dashboard Interface:**

    - Visit [http://127.0.0.1:8000/dashboard/register/](http://127.0.0.1:8000/dashboard/register/)


## Technology Stack

- **Backend:** Python – Django
- **Frontend:** Django Templates
- **Database:** PostgreSQL

