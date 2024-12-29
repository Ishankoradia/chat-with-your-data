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
    python bot_v4_with_memory_sql_generation_and_state_persistence/seed.py --mode train
    python bot_v4_with_memory_sql_generation_and_state_persistence/seed.py --mode checkpointer
    python bot_v4_with_memory_sql_generation_and_state_persistence/chatbot.py
    ```