#!/bin/bash

#SBATCH --account=rubin:developers      # Account name
#SBATCH --partition=milano
#
#SBATCH --job-name=baseline5.1
#SBATCH --output=output-%j.txt
#SBATCH --error=output-%j.txt
#
#SBATCH --nodes=1                       # Number of nodes
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=20
#SBATCH --mem-per-cpu=8g
#
#SBATCH --time=2-14:10:00
#SBATCH --chdir=/sdf/data/rubin/shared/fbs_sims/26_scratch/sat_streaks
#SBATCH --mail-user=yoachim@uw.edu
#
##turn on e-mail notification
#SBATCH --mail-type=ALL
#SBATCH --mail-user=yoachim@uw.edu

## Set up the evironment
source ~/anaconda3/etc/profile.d/conda.sh
conda activate rubin13
export OPENBLAS_NUM_THREADS=1

cat sats.sh | parallel -j 20
