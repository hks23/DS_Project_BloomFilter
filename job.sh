#!/bin/bash

#SBATCH --job-name=bloom_filter_benchmark
#SBATCH --output=bloom_output_%j.txt
#SBATCH --error=bloom_error_%j.txt
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --partition=batch

echo "Started: $(date)"
echo "Node: $(hostname)"
echo "Working directory: $(pwd)"

module load Miniconda3
conda activate bloom

cd $SLURM_SUBMIT_DIR

python benchmark.py

echo "Finished: $(date)"

