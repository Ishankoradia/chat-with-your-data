Look at the `.png` in each folder to understand how the bot graph is structured using langGraph

1. **Setup environment**

    Make sure you have a `.env` file with the necessary environment variables. You can copy the sample environment variables from `.env.example` if available.

    ```sh
    cp .env.example .env
    ```

2. **Create and Activate env**

    ```sh
    python -m venv venv
    source venv/bin/activate
    ```

3. **Make sure root level modules are available**

    Run from root
    ```sh
    export PYTHONPATH=$(pwd)
    ```

4. **Execute the program**

    ```sh
    python bot_v3_with_memory_and_sql_generation/chatbot.py
    ```