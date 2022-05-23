# Dissertation Pedro Carvalho 21/22
Repository that hosts the project developed in the context of my master's thesis in software engineering at FEUP from 2021/22.

## System's Architecture

![System's Architecture](/assets/images/architecture.png "System's Architecture")


## Domain Model

![Domain Model](/assets/images/domainmodel.png "Domain Model")


## Instalation Guideline

To run the application locally you need firstly to install the following requirements.

### Requirements

- Python <= 3.8
- Redis
- Anaconda
- PostgreSQL

### Procedures

After installing on your machine the mentioned requirements you will need to:

- Create a virtual environment with Anaconda
- Create a database and a user with PostgreSQL
- Install all the project dependencies on your virtual environment trough the requirements.txt
- Create a .env file on the project root to have all the local environment variables set:
  - SECRET_KEY=**your-secret-key**
  - DEBUG=True
  - ALLOWED_HOSTS=.localhost, 127.0.0.1
  - ENVIRONMENT=Development
  - DATABASE_URL=postgres://**username**:**password**@localhost:5432/**database-name**
  - REDISTOGO_URL=redis://127.0.0.1:6379/0

### Execution

After installing all the dependencies and seting up the project locally, to execute the application, you will need to run three commands on a terminal after activting your environment with the command **conda activate VIRTUAL_ENVIRONMENT**:

- redis-server
- celery -A CollectDataService worker
- python manage.py runserver

## Deployed Version

If you only wish to consume the API developed and use it's functionalities you can simply make use of the version hosted on Heroku in the url: https://webpagematcher.herokuapp.com/

### Endpoints

Beyond all the CRUD operations developed, these are the endpoints that give access the core functionalities of the application:

- Create a Website: **POST /webSite**
  - { name: NAME }
- Create a Web Page: **POST /webPage**
  - { url: URL; strucutre:STRUCTURE }
- Create Website's Web Pages Identifiers: **POST /webSite/WEBSITE_NAME/webPage/identifiers?method=METHOD_IDENTIFIER&weight=WEIGHT&offset=OFFSET**
- Get Website's Web Pages Identifiers: **GET /webSite/WEBSITE_NAME/webPage/identifiers?method=METHOD_IDENTIFIER**
- Get Website's Common Paths:**GET /webSite/WEBSITE_NAME/webPage/subsequences?method=METHOD_IDENTIFIER&length=LENGTH&support=SUPPORT**
- Create a Domain: **POST /domain**
  - { domain: DOMAIN_NAME }