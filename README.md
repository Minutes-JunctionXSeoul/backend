# Junction-django

1. pip install -r requirements.txt
2. python manage.py migrate
3. python manage.py runserver

## Setup

You need to store the key and endpoints for Azure configuration in the shell variable before running server.
```
export NER_KEY={Your Azure Text Analysis Key}
export NER_ENDPOINT={Your Azure Text Analysis Endpoint}
```
