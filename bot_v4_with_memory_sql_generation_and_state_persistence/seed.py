"""
This file should be executed before running the bot
This does
    1. Train vanna's RAG model for sql generation on the warehouse
    2. Seed the tables that will save the state of the grpah at every checkpoint
"""

import argparse
from sql_generation.main import setup_training_plan_and_execute
from checkpoint import checkpointer

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run training or setup checkpointer.")
    parser.add_argument(
        "--mode",
        choices=["train", "checkpointer"],
        required=True,
        help="Choose whether to run training or setup checkpointer.",
    )

    args = parser.parse_args()

    if args.mode == "train":
        setup_training_plan_and_execute()
    elif args.mode == "checkpointer":
        checkpointer.setup()
