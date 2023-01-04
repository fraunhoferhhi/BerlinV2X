#!/bin/bash
### 			INSTRUCTIONS
### I. CREATE SINGULARITY CONTAINER
# Execute the following bash command:
#   singularity build --fakeroot --force cluster/ubuntu-mi.sif cluster/ubuntu-mi.def
#
### II. ADAPT TO YOUR PREFERRED SLURM OPTIONS
# Change the SBATCH lines below:
# 1. Add your mail user
# 2. Name your job
# 3. Set hardware options
# 4. Set the number of array jobs with --array
# 5. Add any other options of your like

#SBATCH --mail-type=ALL
#SBATCH --mail-user=max.mustermann@hhi.fraunhofer.de
#SBATCH --job-name="mi2log_parquet"
#SBATCH --nodes=1
#SBATCH --partition=gpu
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1
#SBATCH --mem-per-gpu=32GB
#SBATCH --array=0-100


# include the definition of the LOCAL_JOB_DIR which is autoremoved after each job
source "/etc/slurm/local_job_dir.sh"

# Adapt to your data and code paths
DATA_DIR="/data/datapool3/datasets/ai4mobile"
DATA_MNT="/mnt/ai4mobile"

CODE_DIR="/data/cluster/users/${USER}/ai4mobile/berlin"
CODE_MNT="/mnt/project"

#################### DEBUG TIP ####################
# Enter a similar command as below with `singularity shell`
# instead of `singularity run` in the command line
# to debug code before cluster submission
# https://docs.sylabs.io/guides/3.1/user-guide/cli/singularity_shell.html

# Call the right python script and pass the job array index as $SLURM_ARRAY_TASK_ID
singularity run --bind ${DATA_DIR}:${DATA_MNT},${CODE_DIR}:${CODE_MNT} ./cluster/ubuntu-mi.sif mi/reader/run.py  -i $SLURM_ARRAY_TASK_ID