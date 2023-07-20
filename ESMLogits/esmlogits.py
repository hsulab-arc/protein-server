import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from Bio import pairwise2, SeqIO
from scipy import stats as ss
import subprocess
import os
import argparse

from predict_esm import predict_esm

def download_from_bucket(bucket_name):
    """
    Downloads a blob from the bucket to a local file named input.fasta
    """
    try:
        process = subprocess.run(['gsutil', 'cp', f'gs://{bucket_name}/input.fasta', "input.fasta"], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error occurred while downloading file from GCS: {e}')
        exit(1, e)

def write_to_bucket(bucket_name, file_name):
    try:
        process = subprocess.run(['gsutil', 'cp', f'logits/{file_name}', f'gs://{bucket_name}/{file_name}'], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error occurred while downloading file from GCS: {e}')
        
        
def process_fasta(file):
    records = list(SeqIO.parse(file, "fasta"))
    sequences = {}
    try:
        sequences = {record.id: str(record.translate().seq) for record in records}
    except Exception as e:
        print(f'Error occurred while processing fasta file: {e}')
        print('You may have uploaded an amino acid FASTA file instead of a DNA FASTA file.')
    return sequences

model_locations = [
    'esm1v_t33_650M_UR90S_1',
    'esm1v_t33_650M_UR90S_2',
    'esm1v_t33_650M_UR90S_3',
    'esm1v_t33_650M_UR90S_4',
    'esm1v_t33_650M_UR90S_5',
    'esm2_t36_3B_UR50D',
]
def esmlogits(sequences, indexing=1):

    for name, sequence in sequences.items():

        # Using wt-marginals because it's faster, correlates strongly to masked-marginals,
        # and scores are normalized by WT anyways, so masked-marginals are not needed

        WT_marginals = predict_esm(
            sequence=sequence,
            model_locations=model_locations,
            scoring_strategy='wt-marginals',
            offset_idx=indexing,
            verbose=1
        )

        WT_marginals['esm_summed'] = WT_marginals[model_locations].sum(axis=1)
        WT_marginals['position'] = WT_marginals['mutant'].str[1:-1]
        WT_marginals.set_index('mutant', inplace=True)

        # Save the outputs
        print(f'Saving output to logits/{name}.csv')
        WT_marginals.to_csv(f'logits/{name}.csv', index=True)
    
if __name__ == "__main__":
    # Parse Inputs
    parser = argparse.ArgumentParser(description="ESMLogits function")

    parser.add_argument('Bucket', 
                        type=str,
                        help='Input bucket name')

    args = parser.parse_args()

    # Pull input fasta file from bucket
    bucket = args.Bucket
    print(f"I got the following bucket path: {bucket}")

    print("Attempting to pull from the bucket...")
    download_from_bucket(bucket)
    print(f"{os.listdir('.')}")

    print(f"Creating output directory")
    os.makedirs("./logits", exist_ok=True)
    

    # Run ESMLogits
    print("Processing input fastas")
    tokenized_input = process_fasta("input.fasta")

    print("Running ESMLogits.")
    esmlogits(tokenized_input)

    print("Copying outputs to bucket")
    for file in os.listdir("./logits"):
        write_to_bucket(bucket, file)