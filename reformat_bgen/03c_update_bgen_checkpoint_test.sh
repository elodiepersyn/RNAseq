#!/bin/bash
#SBATCH -J checkpoint_test_update_bgen
#SBATCH -A PETERS-SL3-CPU
#SBATCH --output=/home/jm2294/rds/rds-jmmh2-projects/interval_rna_seq/GENETIC_DATA/b37_b38_liftover/logs/checkpoint_test_update_bgen_%A_%a.log
#SBATCH --time=00:01:00
#SBATCH -p skylake-himem
#SBATCH --mem 20G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jm2294@medschl.cam.ac.uk

. /etc/profile.d/modules.sh
module purge
module load rhel7/default-peta4
module load dmtcp/2.6.0-intel-17.0.4
module load qctool
ulimit -s 8192

RESTARTSCRIPT="dmtcp_restart_script.sh"
export DMTCP_QUIET=2

runcmd='
qctool -g /home/jm2294/rds/rds-jmmh2-pre_qc_data/interval/affy_ukbiobank_array/raw_data/genetics/imputed/impute_22_interval.bgen -s /home/jm2294/rds/rds-jmmh2-pre_qc_data/interval/affy_ukbiobank_array/raw_data/genetics/imputed/interval.samples -incl-samples /home/jm2294/rds/rds-jmmh2-projects/interval_rna_seq/analysis/00_testing/results/test_run/batch1_ids.txt -map-id-data /home/jm2294/rds/rds-jmmh2-projects/interval_rna_seq/GENETIC_DATA/b37_b38_liftover/INTERVAL_chr22_b37_to_b38_map.txt -og /home/jm2294/rds/rds-jmmh2-projects/interval_rna_seq/GENETIC_DATA/b37_b38_liftover/b38_bgen/impute_22_interval_b38_checkpointtest_small_comparisonfile.bgen'
tint=60

echo "Start coordinator"
date
eval "dmtcp_coordinator --daemon --coord-logfile dmtcp_log.txt --exit-after-ckpt --exit-on-last -i "$tint" --port-file cport.txt -p 0"
sleep 2
cport=$(<cport.txt)
echo "$cport"

if [ -f "$RESTARTSCRIPT" ]
then
    echo "Resume the application"
    CMD="dmtcp_restart -p "$cport" -i "$tint" ckpt*.dmtcp"
    echo $CMD
    eval $CMD
else
    echo "Start the application"
    CMD="dmtcp_launch --rm --infiniband --no-gzip -h localhost -p "$cport" "$runcmd
    echo $CMD
    eval $CMD
fi

echo "Stopped program execution"
date
sleep 2
dmtcp_command -h $DMTCP_COORD_HOST -p $DMTCP_COORD_PORT --quit