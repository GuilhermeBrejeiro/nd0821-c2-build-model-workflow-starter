#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)


    artifact_local_path = run.use_artifact(args.input_artifact).file()

    df = pd.read_csv(artifact_local_path)

    #Drop outliers
    logger.info("Drop outliers")
    idx = df["price"].between(args.min_price, args.max_price)
    df = df[idx].copy()

    idx = df["longitude"].between(-74.25, -73.50) & df["latitude"].between(40.5, 41.2)
    df = df[idx].copy()

    #Convert last review to datetime
    logger.info("convert last review to datetime")
    df["last_review"] = pd.to_datetime(df["last_review"])

    filename = "clean_sample.csv"
    df.to_csv(filename, index=False)

    artifact = wandb.Artifact(
        name = args.output_artifact,
        type = args.output_type,
        description=args.output_description,
    )

    artifact.add_file(filename)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(filename)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="The input artifact to be cleaned",
        required=True,
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="A cleaned output artifact",
        required=True,
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="The type of artifact",
        required=True,
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="A description about the output gerenated",
        required=True,
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="The minimum price threshold",
        required=True,
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="The maximum price threshold",
        required=True,
    )


    args = parser.parse_args()

    go(args)