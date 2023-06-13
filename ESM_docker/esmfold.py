from transformers import AutoTokenizer, EsmForProteinFolding
from accelerate import cpu_offload
from transformers.models.esm.openfold_utils.protein import to_pdb, Protein as OFProtein
from transformers.models.esm.openfold_utils.feats import atom14_to_atom37
from Bio import SeqIO
import torch
from time import time
import sys
import subprocess
import os
import numpy as np

def download_from_bucket(bucket_name):
    """
    Downloads a blob from the bucket to a local file named input.fasta
    """
    try:
        process = subprocess.run(['gsutil', 'cp', f'gs://{bucket_name}/input.fasta', "input.fasta"], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error occurred while downloading file from GCS: {e}')

def write_to_bucket(bucket_name, file_name):
    try:
        process = subprocess.run(['gsutil', 'cp', file_name, f'gs://{bucket_name}/{file_name}'], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error occurred while downloading file from GCS: {e}')
        
        
def process_fasta(file):
    tokenizer = AutoTokenizer.from_pretrained("facebook/esmfold_v1")
    records = list(SeqIO.parse(file, "fasta"))
    sequence = str(records[0].seq)
    
    tokenized_input = tokenizer([sequence], return_tensors="pt", add_special_tokens=False)['input_ids']
    tokenized_input = tokenized_input.to(device)
    return tokenized_input
        
def convert_outputs_to_pdb(outputs):
    final_atom_positions = atom14_to_atom37(outputs["positions"][-1], outputs)
    outputs = {k: v.to("cpu").numpy() for k, v in outputs.items()}
    final_atom_positions = final_atom_positions.cpu().numpy()
    final_atom_mask = outputs["atom37_atom_exists"]
    pdbs = []
    for i in range(outputs["aatype"].shape[0]):
        aa = outputs["aatype"][i]
        pred_pos = final_atom_positions[i]
        mask = final_atom_mask[i]
        resid = outputs["residue_index"][i] + 1
        pred = OFProtein(
            aatype=aa,
            atom_positions=pred_pos,
            atom_mask=mask,
            residue_index=resid,
            b_factors=outputs["plddt"][i],
            chain_index=outputs["chain_index"][i] if "chain_index" in outputs else None,
        )
        pdbs.append(to_pdb(pred))
    return pdbs

def esmfold(tokenized_input):
    # Loading and prepping model
    model = EsmForProteinFolding.from_pretrained("facebook/esmfold_v1", low_cpu_mem_usage=True)
    model = model.cuda()
    
    # Speedups and optim
    # Uncomment to switch the stem to float16
    model.esm = model.esm.half()
    torch.backends.cuda.matmul.allow_tf32 = True
    # Uncomment this line if your GPU memory is 16GB or less, or if you're folding longer (over 600 or so) sequences
    model.trunk.set_chunk_size(64)
    cpu_offload(model)
    
    # Run and benchmark time for esmfold
    start_time = time()
    with torch.no_grad():
        output = model(tokenized_input, num_recycles=10)
    process_time = time() - start_time
    print(f"Took {process_time} seconds")
    return output
    
def save_output(output):
    pdb = convert_outputs_to_pdb(output)
    with open("output.pdb", "w") as f:
        f.write("".join(pdb))
    
if __name__ == "__main__":
    bucket = sys.argv[1]
    print(f"I got the following bucket path: {bucket}")
    print("Attempting to pull from the bucket...")
    # Pulling fasta files from bucket
    try:
        download_from_bucket(bucket)
        print(f"{os.listdir('.')}")
    except Exception as e:
        sys.exit("Error downloading from bucket: {e}")
    
    # Tokenizing input and running ESMfold
    try:
        device = torch.cuda.current_device()
        print("Tokenizing the input")
        tokenized_input = process_fasta("input.fasta")
        print("Running ESMFold.")
        output = esmfold(tokenized_input)
        print("Saving outputs to pdb")
    except Exception as e:
        sys.exit("Error running ESMFold: {e}")


    # Saving output
    try:
        save_output(output)
        print("Copying outputs to bucket")
        write_to_bucket(bucket, "output.pdb")
    except Exception as e:
        sys.exit("Error saving outputs to bucket: {e}")