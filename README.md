-Installare python 

-Creare l'ambiente virtuale py : #Va creato solo una volta#
  python -m venv .venv 

-Attivare l'ambiente venv python : 
  se usi powershell : .venv\Scripts\Activate.ps1
  se usi cmd : .venv\Scripts\activate


-Se non riesci con i comandi e stai utilizzando vscode : 
  https://code.visualstudio.com/docs/python/environments

- installare i requrements :
  pip install -r .\requirements.txt

- Compila  :
    python manage.py makemigrations
    python manage.py migrate

-Installare docker :
  https://docs.docker.com/desktop/setup/install/windows-install/

-Lanciare il docker compose : 
  docker compose up -d           

-Run server : 
 python manage.py runserver

-Swagger : 
  http://127.0.0.1:8000/api/docs/
