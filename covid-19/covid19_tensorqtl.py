#. /etc/profile.d/modules.sh
#module purge
#module load rhel7/default-gpu
#module load miniconda3-4.5.4-gcc-5.4.0-hivczbz 
#module load cuda/9.2
#module load r-3.6.0-gcc-5.4.0-bzuuksv
#
#source activate tensorQTL
#
#python 

import pandas as pd
import tensorqtl
from tensorqtl import genotypeio, cis, trans

dir = "/rds/project/jmmh2/rds-jmmh2-projects/interval_rna_seq/analysis/03_tensorqtl/"
covdir = "/rds/project/jmmh2/rds-jmmh2-projects/interval_rna_seq/covid19/"

phenotype_bed_file =  covdir + "INTERVAL_RNAseq_phase1_filteredSamplesGenes_TMMNormalised_FPKM_Counts_foranalysis_COVID19.bed.gz"
covariates_peer = covdir + "INTERVAL_RNAseq_COVID19_covariates.txt"
outdir = covdir

phenotype_df, phenotype_pos_df = tensorqtl.read_phenotype_bed(phenotype_bed_file)
covariates_peer_df = pd.read_csv(covariates_peer, sep='\t', index_col=0).T  # samples x covariates

interaction_s = pd.read_csv("/rds/project/jmmh2/rds-jmmh2-projects/interval_rna_seq/covid19/INTERVAL_RNAseq_COVID19_neutPCT_GxE.txt", sep = "\t", index_col=0, squeeze = True).T
interaction_s = interaction_s.squeeze()

plink_prefix_path = "/rds/user/jm2294/rds-jmmh2-projects/interval_rna_seq/analysis/03_tensorqtl/genotypes/INTERVAL_b38_autosomes_RNAseqPhase1_biallelic_all_MAF0.005"
pr = genotypeio.PlinkReader(plink_prefix_path)
genotype_df = pd.DataFrame(pr.get_all_genotypes(), index=pr.bim['snp'], columns=pr.fam['iid'])
variant_df = pr.bim.set_index('snp')[['chrom', 'pos']]

#for i in range(1,23):
#  print(i)
#  plink_prefix_path = "/rds/user/jm2294/rds-jmmh2-projects/interval_rna_seq/analysis/03_tensorqtl/genotypes/INTERVAL_b38_autosomes_RNAseqPhase1_biallelic_chr" + str(i) + "_MAF0.005"
#  print(plink_prefix_path)
#  pr = genotypeio.PlinkReader(plink_prefix_path)
#  genotype_df = pd.DataFrame(pr.get_all_genotypes(), index=pr.bim['snp'], columns=pr.fam['iid'])
#  variant_df = pr.bim.set_index('snp')[['chrom', 'pos']]
#  
#  trans_peer_df = trans.map_trans(genotype_df, phenotype_df, covariates_peer_df, return_sparse=True, maf_threshold = 0.005)
#  trans_peer_df.to_csv(outdir + "tensorqtl_trans_MAF0.005_chr" + str(i) + "_age_sex_rin_batch_readDepth_PC10_PEER20_COVID19.csv")
  
# cis
# Cis gene-level mapping
pheno_df_noACE2 = phenotype_df.drop("ENSG00000130234")
phenopos_df_noACE2 = phenotype_pos_df.drop("ENSG00000130234")

pheno_df_noACE2 = pheno_df_noACE2.drop("ENSG00000184012")
phenopos_df_noACE2 = phenopos_df_noACE2.drop("ENSG00000184012")

cis_df = cis.map_cis(genotype_df, variant_df, pheno_df_noACE2, phenopos_df_noACE2, covariates_peer_df)
tensorqtl.calculate_qvalues(cis_df, qvalue_lambda=0)
cis_df.to_csv(outdir + "tensorqtl_cis_MAF0.005_cisPerGene_chr1.csv", index=True, index_label = "Phenotype")

# Cis nominal mapping
cisnom_df = cis.map_nominal(genotype_df, variant_df, pheno_df_noACE2, phenopos_df_noACE2, covariates_peer_df, prefix= covdir + "tensorqtl_cis_MAF0.005_cisNominal_covid19")

# Conditional analysis
indep_df = cis.map_independent(genotype_df, variant_df, cis_df, pheno_df_noACE2, phenopos_df_noACE2, covariates_peer_df)
indep_df.to_csv(covdir + "tensorqtl_cis_MAF0.005_cisIndependent_covid19.csv", index=True, index_label = "Phenotype")

# GxE
cisGxE_df = cis.map_nominal(genotype_df, variant_df, pheno_df_noACE2, phenopos_df_noACE2, covariates_peer_df, prefix= covdir + "Test_gxe", interaction_s=interaction_s)
cis.map_nominal(genotype_df, variant_df, pheno_df_noACE2, phenopos_df_noACE2, covariates_peer_df, prefix="tensorqtl_cis_MAF0.005_cisGxE_covid19",interaction_s=interaction_s, maf_threshold_interaction=0.005,group_s=None, run_eigenmt=True, output_dir=covdir)

for i in [8,9,21]:
  df = pd.read_parquet(covdir + "tensorqtl_cis_MAF0.005_cisGxE_covid19.cis_qtl_pairs." + str(i) + ".parquet")
  df.to_csv(covdir + "tensorqtl_cis_MAF0.005_cisGxE_covid19.cis_qtl_pairs." + str(i) + ".csv", index=False)

# trans
trans_peer_df = trans.map_trans(genotype_df, pheno_df_noACE2, covariates_peer_df, return_sparse=True, maf_threshold = 0.005)
trans_peer_df.to_csv(outdir + "tensorqtl_trans_MAF0.005_all_age_sex_rin_batch_readDepth_PC10_PEER20_COVID19.csv")

#################################################################
# chrX
import pandas as pd
import tensorqtl
from tensorqtl import genotypeio, cis, trans

covdir = "/rds/project/jmmh2/rds-jmmh2-projects/interval_rna_seq/covid19"

phenotype_file =  covdir + "/phenotypes/INTERVAL_RNAseq_phase1-2_UNfilteredSamplesGenes_TMMNormalised_FPKM_Counts_foranalysis_COVID19.bed.gz"
covariates_file = covdir + "/covariates/INTERVAL_RNAseq_COVID19_covariates.txt"

phenotype_file_ace2 =  covdir + "/phenotypes/INTERVAL_RNAseq_phase1-2_UNfilteredSamplesGenes_TMMNormalised_FPKM_Counts_foranalysis_ACE2_no_zeros.bed.gz"
covariates_file_ace2 = covdir + "/covariates/INTERVAL_RNAseq_COVID19_covariates_ACE2_no_zeros.txt"

outdir = covdir + "/results"

phenotype_df, phenotype_pos_df = tensorqtl.read_phenotype_bed(phenotype_file)
ace2_phenotype_df, ace2_phenotype_pos_df = tensorqtl.read_phenotype_bed(phenotype_file_ace2)

# drop all phenotypes but ACE2
phenotype_df = phenotype_df.drop(phenotype_df.index[[0,1,2]])
phenotype_pos_df = phenotype_pos_df.drop(phenotype_pos_df.index[[0,1,2]])

covariates_df = pd.read_csv(covariates_file, sep='\t', index_col=0).T  # samples x covariates
ace2_covariates_df = pd.read_csv(covariates_file_ace2, sep='\t', index_col=0).T  # samples x covariates

# Read genotypes
plink_prefix_path = "/rds/project/jmmh2/rds-jmmh2-projects/interval_rna_seq/covid19/genotypes/merged_cleaned_chrx_RNAseq_phase1-2"
pr = genotypeio.PlinkReader(plink_prefix_path)
genotype_df = pd.DataFrame(pr.get_all_genotypes(), index=pr.bim['snp'], columns=pr.fam['iid'])
variant_df = pr.bim.set_index('snp')[['chrom', 'pos']]

# Cis gene-level mapping
cis_df = cis.map_cis(genotype_df, variant_df, phenotype_df, phenotype_pos_df, covariates_df)
cis_no0_df = cis.map_cis(genotype_df, variant_df, ace2_phenotype_df, ace2_phenotype_pos_df, ace2_covariates_df)
tensorqtl.calculate_qvalues(cis_df, qvalue_lambda=0)
cis_df.to_csv(outdir + "tensorqtl_cis_MAF0.005_cisPerGene_chr1.csv", index=True, index_label = "Phenotype")

# Cis nominal mapping
cisnom_df = cis.map_nominal(genotype_df, variant_df, pheno_df_noACE2, phenopos_df_noACE2, covariates_peer_df, prefix= covdir + "tensorqtl_cis_MAF0.005_cisNominal_covid19")

# Conditional analysis
indep_df = cis.map_independent(genotype_df, variant_df, cis_df, pheno_df_noACE2, phenopos_df_noACE2, covariates_peer_df)
indep_df.to_csv(covdir + "tensorqtl_cis_MAF0.005_cisIndependent_covid19.csv", index=True, index_label = "Phenotype")

# GxE
cisGxE_df = cis.map_nominal(genotype_df, variant_df, pheno_df_noACE2, phenopos_df_noACE2, covariates_peer_df, prefix= covdir + "Test_gxe", interaction_s=interaction_s)
cis.map_nominal(genotype_df, variant_df, pheno_df_noACE2, phenopos_df_noACE2, covariates_peer_df, prefix="tensorqtl_cis_MAF0.005_cisGxE_covid19",interaction_s=interaction_s, maf_threshold_interaction=0.005,group_s=None, run_eigenmt=True, output_dir=covdir)

for i in [8,9,21]:
  df = pd.read_parquet(covdir + "tensorqtl_cis_MAF0.005_cisGxE_covid19.cis_qtl_pairs." + str(i) + ".parquet")
  df.to_csv(covdir + "tensorqtl_cis_MAF0.005_cisGxE_covid19.cis_qtl_pairs." + str(i) + ".csv", index=False)

# trans
trans_df = trans.map_trans(genotype_df, phenotype_ace2_df, covtest, return_sparse=True, maf_threshold = 0.005)
trans_peer_df.to_csv(outdir + "tensorqtl_trans_MAF0.005_all_age_sex_rin_batch_readDepth_PC10_PEER20_COVID19.csv")


trans_peer_df = trans.map_trans(genotype_df, phenotype_df, covariates_peer_df, return_sparse=True, maf_threshold = 0.005, pval_threshold = 0.05)
trans_peer_df.to_csv(outdir + "results/tensorqtl_trans_MAF0.005_chrx_age_sex_rin_batch_readDepth_PC10_PEER20_COVID19_phase1.csv")
p = phenotype_df.drop(phenotype_df.index[[0,1,2]])
p_pos = phenotype_pos_df.drop(phenotype_pos_df.index[[0,1,2]])
cis_df = cis.map_cis(genotype_df, variant_df, p, p_pos, covariates_peer_df)
tensorqtl.calculate_qvalues(cis_df, qvalue_lambda=0)
cis_df.to_csv(outdir + "results/tensorqtl_cis_MAF0.005_cisPerGene_chr1.csv", index=True, index_label = "Phenotype")
cisnom_df = cis.map_nominal(genotype_df, variant_df, p, p_pos, covariates_peer_df, prefix= covdir + "results/tensorqtl_cis_MAF0.005_cisNominal_ACE2_phase1")
cisnom_df = pd.read_parquet(covdir + "results/tensorqtl_cis_MAF0.005_cisNominal_ACE2_phase1.cis_qtl_pairs.23.parquet")
cisnom_df.to_csv(covdir + "results/tensorqtl_cis_MAF0.005_cisNominal_ACE2_phase1.cis_qtl_pairs.23.csv", index=False)
