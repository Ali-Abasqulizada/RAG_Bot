# Retrieval-Augmented Generation (RAG) Project

RAG, which stands for Retrieval-Augmented Generation, is an AI framework that combines the strengths of traditional information retrieval systems, such as search and databases, with the capabilities of generative large language models (LLMs).

Follow the instructions below to configure and run the application locally.

## Step 1: Environment Setup

1. Open the project in Visual Studio Code or your preferred code editor.
2. Open a terminal and create a virtual environment by running the following command, which will create a folder named `env`:
   ```bash
   python -m venv env
   ```
3. Activate your virtual environment:
   * Windows: `.\env\Scripts\activate` 
   * Mac/Linux: `source env/bin/activate`
   * *Note: To exit the environment at any time, simply type `deactivate` in the terminal.*
4. Install the required project dependencies: 
   ```bash
   pip install -r requirements.txt
   ```

## Step 2: Environment Variables

Create a file named `.env` in the root directory of your project. This file will store all your secure tokens. The application utilizes the following free services, which you will need to register for to obtain the necessary keys:

* **`GROQ_API_KEY`**: The token for the primary generation model. Go to https://console.groq.com, sign in, navigate to "API keys", and generate a key.
* **`CEREBRAS_API_KEY`**: The token for the secondary fallback model. Go to https://cloud.cerebras.ai, sign in, navigate to "API keys", and generate a key.
* **`ZILLIZ_URI` & `ZILLIZ_TOKEN`**: RAG projects require Vector databases rather than standard relational databases. Standard databases do not understand semantic context (for example, recognizing the relationship between "kitten", "cat", and "tiger"), whereas Vector databases process the actual meaning of words. To avoid the computational overhead of local deployment, this project uses the hosted Milvus database via Zilliz. Go to https://cloud.zilliz.com, create a project, and copy your "Public endpoint" (URI) and token.
* **`HF_TOKEN`**: This token is required to utilize Hugging Face's "BAAI" model, which converts queries into vector embeddings. Go to https://huggingface.co, sign in, navigate to settings, select tokens, and create an access token.
* **`SECRET_KEY`**: Your unique Django security key.

## Step 3: Django Initialization

Run the following commands to prepare the Django backend:

1. Gather all static CSS and JavaScript files into a `staticfiles` directory:
   ```bash
   python manage.py collectstatic
   ```
2. Create the default SQLite database to initialize Django's architecture and resolve terminal warnings:
   ```bash
   python manage.py migrate
   ```

## Step 4: Vector Database Ingestion

Before interacting with the AI, you must populate the vector database with your contextual documents.

1. Create a folder named `media` in the project root directory.
2. Add all of your reference documents into the `media` folder. Ensure all files are in PDF format.
3. Run the ingestion script located in the `api` folder to upload and embed the documents into your Zilliz cloud database:
   ```bash
   python api/create.py
   ```
4. **Verification (Optional but Recommended):**
   * Test the database connection by running: `python api/test_database_conn.py`
   * Test the Hugging Face token connection by running: `python api/test_hf_conn.py`

## Step 5: Launch the Application

Once the database is populated, start the local development server:

```bash
python manage.py runserver
```

Congratulations, your personal RAG application is now running.

Checkout the project: https://web-production-05c50.up.railway.app/