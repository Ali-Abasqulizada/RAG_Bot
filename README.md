RAG -> Retrieval-Augmented Generation

RAG, which stands for Retrieval-Augmented Generation, is an AI framework that combines 
the strengths of traditional information retrieval systems (such as search and databases) 
with the capabilities of generative large language models (LLMs).

How to run locally...

STEP 1.

Open project on Visual Studio Code (or any other compiler, Ideally which one you are most familiar with)

Then create your virtual environment by using this command `python -m venv env`. This command will create 
folder named "env". Then activate your virtual environment: `.\env\Scripts\activate`. 

Note: if you want to close your environment, just write `deactivate` terminal

In next step, we need to install dependencies aka libraries.

`pip install > requirements.txt`

This command will create file called "reqirements.txt" and all the dependencies will be located there. 

STEP 2.

Create a file called ".env". All the tokens will be located there. Currently this application uses these. These are all free options:

`GROQ_API_KEY` -> Token of first model that we are going to use in our project. Go to https://console.groq.com, sign in then click on "API keys". There you will create your api key. 
`CEREBRAS_API_KEY` -> Token of second model. Go to https://cloud.cerebras.ai, sign in then click on "API keys". There you will create your api key. 
`ZILLIZ_URI`, `ZILLIZ_TOKEN` -> For RAG projects, we have to use Vector databases. Because if we use normal Relational or Non-relational databases and search for kitten in the database with query, it will not return Cat or Tiger on the DB. Because they don't understand the real meaning of words. However, Vector databases understand words. I will not explain how. I suggest you to search a bit if you don't know about that. 

Having Database on local pc, could be expensive. Also if you want to deploy your project on free of charge, this will cause you problem in the future. We could use "docker" but again, in deployment process, it will cause us problem. So we can use Milvus vector database on https://cloud.zilliz.com. Go to that web site, create your project then get your "Public endpoint" and "token". 
`HF_TOKEN` -> This token will be required for "BAAI" model of Hugging Face company. This will help us to convert our query to vectors. In order to get this token you need to go https://huggingface.co site. Sign in and go to settings then tokens, there you will create your access token. 
`SECRET_KEY` -> This will be your django secret key.

STEP 3.

Create static files: `python manage.py migrate`. This will create folder named staticfiles. There will be located your css files. 
Create sqlite database: `python manage.py migrate`, We will not use this in our project, but in order to remove warnigns we must do that.

STEP 4. 

In this step we will create Milvus database on the internet. But before that we need to create folder named "media". Then add you documents (All documents should be PDf) into media folder. 

Then just run "create.py" in "api" folder: `python.exe api/create.py`.

This will create our database on the zilliz. Ideally you should run "test_database_conn.py" file in the same folder to check the connection: `python.exe api/test_database_conn.py`.

Note: Don't forget to check if HF is working or not. Just run "test_hf_conn.py" file: `python.exe api/test_hf_conn.py`.

STEP 5.

Finally, it is time to run: `python.exe manage.py runserver`.

CONGRATULATIONS, now you have a personal RAG project.