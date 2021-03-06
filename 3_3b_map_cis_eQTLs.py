# Python script to run cis-eQTL mapping
import sys
import pandas as pd
import tensorqtl
from tensorqtl import genotypeio, cis, trans

# Specify root directory for analysis
path = "/home/jm2294/rds/rds-jmmh2-projects/interval_rna_seq/analysis/04_phase2_full_analysis/"

# Specify output path (and prefix if desired). Can be set to any folder if you want it outside the analysis directory
outpath = path + "results/cis_eQTLs/"

# Get analysis chromosome from command line arguments, this in turn comes from SLURM array ID
chr = str(sys.argv[1]) 

# Set up file paths
phenotype_bed_file = path + "phenotypes/INTERVAL_RNAseq_phase1-2_filteredSamplesGenes_TMMNormalised_FPKM_Counts_foranalysis_chr" + chr + ".bed.gz"
covariates_file = path + "covariates/INTERVAL_RNAseq_phase1-2_fullcovariates_foranalysis.txt"
plink_prefix_path = path + "genotypes/INTERVAL_RNAseq_Phase1-2_imputed_b38_biallelic_MAF0.005_chr" + chr

# Read in phenotypes
phenotype_df, phenotype_pos_df = tensorqtl.read_phenotype_bed(phenotype_bed_file)

# Read in covariates and make subset to only ids that are in the phenotype file
covariates_df = pd.read_csv(covariates_file, sep='\t', index_col=0)
covariates_df = covariates_df[phenotype_df.columns].T

# Read in genotypes 
pr = genotypeio.PlinkReader(plink_prefix_path)

# load genotypes and variants into data frames
genotype_df = pd.DataFrame(pr.load_genotypes(), index=pr.bim['snp'], columns=pr.fam['iid'])
variant_df = pr.bim.set_index('snp')[['chrom', 'pos']]

# Cis gene-level mapping
cis_df = cis.map_cis(genotype_df, variant_df, phenotype_df, phenotype_pos_df, covariates_df)
tensorqtl.calculate_qvalues(cis_df, qvalue_lambda=0) # Lambda of 0 is equivalent to BH correction. Prevents crashes for chr 9, 18, 22. 
cis_df.to_csv(outpath + "tensorqtl_cis_MAF0.005_cisPerGene_chr" + chr + ".csv", index=True, index_label = "Phenotype")

# Cis nominal mapping
cisnom_df = cis.map_nominal(genotype_df, variant_df, phenotype_df, phenotype_pos_df, covariates_df, prefix=outpath + "tensorqtl_cis_MAF0.005_cisNominal_chr" + chr)
cisnom_df2 = pd.read_parquet(outpath + "tensorqtl_cis_MAF0.005_cisNominal_chr" + chr + ".cis_qtl_pairs." + chr + ".parquet")
cisnom_df2.to_csv(outpath + "tensorqtl_cis_MAF0.005_cisNominal_chr" + chr + ".csv", index = False)

# Conditional analysis # commented out because it times out
#indep_df = cis.map_independent(genotype_df, variant_df, cis_df, phenotype_df, phenotype_pos_df, covariates_df, nperm=10000)
#indep_df.to_csv(outpath + "tensorqtl_cis_MAF0.005_cisIndependent_chr" + chr + ".csv", index=True, index_label = "Phenotype")

# GxE
#interaction_s = pd.read_csv("/rds/project/jmmh2/rds-jmmh2-projects/interval_rna_seq/analysis/03_tensorqtl/covariates/INTERVAL_RNAseq_phase1_GxE_neutPCT.txt", sep = "\t", index_col=0, squeeze = True).T
#cisGxE_df = cis.map_nominal(genotype_df, variant_df, phenotype_df, phenotype_pos_df, covariates_df, prefix="Test_gxe", interaction_s=interaction_df)
#cis.map_nominal(genotype_df, variant_df, phenotype_df, phenotype_pos_df, covariates_df, prefix="tensorqtl_cis_MAF0.005_cisGxE_chr1",interaction_s=interaction_s, maf_threshold_interaction=0.05,group_s=None, run_eigenmt=True, output_path=outpath)
