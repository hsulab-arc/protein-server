# Protein Engineering Server

Use cases:
1. Input a protein, and get a probability distribution of amino acids at each position (masked prediction).
1a. Following from this, predict most likely variant
2. Input a protein, and get the latent representation of it (representation).
3. Visualize protein, and labeled variant.



Deployment:
1. Alphafold docker container which is called every time you want to generate a prediction.
    This is too big to do locally.
2. 


Progress
- [x] frontend input
- [] test running ESM on GCP instance
- [] packaging ESM into a dockerfile or Google Cloud Function
- [] call ESM from frontend
- [] mock output for frontend
- [] probability distribution viz, protein 3d viz for frontend
- [] (optional) ESM optimization with TorchScript