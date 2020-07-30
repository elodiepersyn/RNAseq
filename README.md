# INTERVAL RNA-seq eQTL analysis

## Scripts
This is a repository of scripts used in the analysis of the RNA seq data from the INTERVAL cohort. Current generation scripts are stored in the root folder, with the [initial Limix pipeline](01_limix_pipeline) and the [tensorQTL phase I analysis](02_tensorqtl_phase_1) scripts stored in subfolders for reference purposes.

Where possible, I've tried to name files in a way that makes it obvious what order they have to be run in.

Unless otherwise specified, all file paths are given relative to `/rds/project/jmmh2/rds-jmmh2-projects/interval_rna_seq/`.

## Data

### Phenotype

#### Raw data
RNA-seq data is downloaded from the Sanger HGI service Globus server. This is accessed from https://app.globus.org/file-manager and requires an endpoint to be set up on CSD3 to transfer files. The commands required to configure this are stored in [globus_config_for_csd3.txt](globus_config_for_csd3.txt).

Initial Phase I data is stored in `/rds/project/jmmh2/rds-jmmh2-pre_qc_data/interval/rna_seq/raw_data/globus` in subfolders by batch. Within each subfolder, `.cram` files are stored tar files in the `data` folders and processed gene counts are stored in the `results-study5591-*` folders.

Phase I was recalled together with batches 9-12 of Phase II to bring INTERVAL into closer alignment with the BioAid and GAINS studies. This latest data release is stored on the globus server, with some files downloaded to `globus_phase2_recalled`. Not all files have been copied,  as many of these files are symlinks on the Sanger side and are ignored by the globus sync functions. This is something that needs to be worked out with Guillaume Noell.

#### Reformatted data
Gene counts from globus have been filtered and TMM-normalised by Artika Nath - a version of the script used for this is stored [here](artika_TMM_normalisation.R) but she will have the most up-to-date version. The file used as input for phenotype generation is the same one used for peer and is consequently stored in `analysis/04_phase2_full_analysis/peer_factors/peer_InputFiles/GeneExpr_PEER_TmmInvRankNormalised_swapsSwapped_mismatchRemoved.csv`. Phenotype input files for TensorQTL are stored in `analysis/04_phase2_full_analysis/phenotypes` and are generated with [this script](3_1_make_tensorQTL_input_phase2.R).

#### Annotation
Genomic positions of genes are obtained from Ensembl. Annotation files are stored in `analysis/04_phase2_full_analysis/annotation_file`, with the raw BioMart output stored in `19_9_5_mart_export.txt` and the reformatted annotation file in `Feature_Annotation_Ensembl_gene_ids_autosomesPlusChrX_b38.txt`. This is a throwback to the Limix pipeline where annotation was supplied as a separate file, but this information is now stored within the TensorQTL .bed input. However, the phenotype generation scriptes still require the annotation file to be in the Limix format. The script to reformat this is stored [here](3_0_make_annotation_file_autosomes_plus_x.R).

### Covariates
Scripts for covariate handing are stored in [their own subfolder](covariates). The master file containing all covariates is `analysis/04_phase2_full_analysis/covariates/processed/INTERVAL_RNA_batch1-12_master_covariates_release_2020_07_01.csv`. The analysis ready covariate file is stored in `analysis/04_phase2_full_analysis/covariates`.

### PEER factors
PEER factors were also generated by Artika. The scripts for doing this are duplicated [here](covariates/PEER). 20 factors were generated as more than this contribute little to explaining variance in the RNA-seq data. Biological covariates explicitly adjusted for are detailed in `analysis/04_phase2_full_analysis/peer_factors/peer_InputFiles/Covariates_for_PEER_mismatchRemoved.csv`. Additional technical covariates are included in the regression model in TensorQTL. The rationale behind this was to explicitly correct for those covariates where there might be an interest in partitioning variance, e.g. the cell count traits. 

The Sysmex traits included as covariates were all the traits used in the [Astle et al Cell GWAS](https://pubmed.ncbi.nlm.nih.gov/27863252/) minus the cell counts that were also represented as a percentage (eg Lymphocyte percentage was retained while Lymphocyte count was not. This was because the former was used to derive the latter).

### Genotype
TensorQTL takes plink genotype format as input. This does mean imputed genotypes are hard-called, but I consider the trade off in speed to be worth it. 

The scripts in the [genotypes](genotypes) subfolder describe the filters applied. Genetic PCs are calculated using [this script](genotypes/1_7_plink_get_PCs.sh) which is based on Ben's code from the SomaLogic analysis.

ChrX files were created as part of the [COVID-19 subproject](covid-19). The files `INTERVAL_chrX_merged_cleaned_RNAseq_phase1-2_b38_rsids_deduplicated_MAF0.005.*` were copied to `analysis/04_phase2_full_analysis/genotypes` and renamed `INTERVAL_RNAseq_Phase1-2_imputed_b38_biallelic_MAF0.005_chr23.*`


## Pipeline
Initial cis-eQTL mapping was performed using the [Limix Pipeline](01_limix_pipeline). Experimental trans-eQTL mapping trialed in Limix, but this was switched to TensorQTL, which has been used for all subsequent analyses.

Current-generation scripts are named with `3_#` prefix, for the third iteration of the analysis pipeline. 
Scripts are as follows:
* [3_0_make_annotation_file_autosomes_plus_x.R](3_0_make_annotation_file_autosomes_plus_x.R): Converts BioMart annotation file into the right format for the next step.
* [3_1_make_tensorQTL_input_phase2.R](3_1_make_tensorQTL_input_phase2.R): Output phenotype `.bed` files for use in TensorQTL.
* [3_2_index_bed.sh](3_2_index_bed.sh): Compress and index `.bed` files from previous step.
* [3_3a_map_cis_eQTLs_submissions_script.sh](3_3a_map_cis_eQTLs_submissions_script.sh) and [3_3b_map_cis_eQTLs.py](3_3b_map_cis_eQTLs.py): The python script that runs the cis-eQTL mapping in TensorQTL, and the shell script for submission to CSD3.
* [3_4a_map_trans_eQTLs_submissions_script.sh](3_4a_map_trans_eQTLs_submissions_script.sh) and [3_4b_map_trans_eQTLs.py](3_4b_map_trans_eQTLs.py): The corresponding scripts for submitting trans-eQTL mapping. 

Note: As of 29/7/2020 the trans scripts are untested, but I have historically had errors with trans mapping detailed [here](https://github.com/broadinstitute/tensorqtl/issues/13). These were mitigated for the COVID-19 analysis by expanding the window size to encompass all SNPs in one go, but this may not be possible for genome-wide analysis.

## Files
All files on CSD3 are currently located in the project folder, `/rds/project/jmmh2/rds-jmmh2-projects/interval_rna_seq/` (i.e. not in the GWASqc folder, since they're not yet finalised).
***
**The most up-to-date analysis files are located in `analysis/04_phase2_full_analysis`. It's unlikely anything outside this will be hugely relevant.
***

Where possible, file names are intuitive, but folder contents are broadly as follows:
* **analysis**: files for the main eQTL mapping analysis
	* **00_testing**: Early tests of the Limix pipeline, mostly around getting things working
	* **01_cis_eqtl_mapping**: Limix pipeline cis-eQTL mapping in phase I samples. Some of the subfolders here were originally under the root folder, but have been moved. This will have broken some file paths.
		* **GENETIC_DATA**: (moved from root) genotype data, lifted over from b37 to b38.
		* **genetic_PCs**: (moved from root) genetic PCs for use as covariates
		* **results**: Subfolders for results by covariates included, these were used for pipeline configuration
			* **...5GenesPerChunk**: final complete cis-eQTL results from Limix (switiching to CSD3 meant a 12 hour limit on jobs, necessitating diving the task into 5-gene chunks).
	* **02_trans_eqtl_mapping**: preliminary tests of LIMIX trans-eQTL mapping. Abandoned.
	* **03_tensorqtl**: Initially testing for tensorQTL, evolved into full phase I results.
		* **results**: eQTLs mapped using TensorQTL from the command line
			* **python_module_method**: eQTLs mapped using TensorQTL as a module loaded within python. This worked more consistently. Files are named by covariates adjusted for. 'cis' refers to the output from `map_cis`, which gives the lead SNP for each genetic feature. 'cis_nominal' is the output from `map_nominal` which outputs a p-value for every SNP-phenotype pair, but does not correct for multiple testing. Applying the `pval_nominal_threshold` from cis to the pvalues from cis_nominal allows identification of eSNPs within a significant eGene.
	* **04_phase2_full_analysis**: Folder for latest results using recalled phase I & II samples together for a total of ~4k
		* **phenotypes**, **covariates**, **genotypes**: input files for TensorQTL. Analysis-ready files are in the root folder, with raw files in **raw** and files generated during processing in **processed**.
		* **results**: cis and trans eQTLs stored in separate folders. Format is as above. Parquet files can be read into python with `pd.read_parquet()`
		* **side_projects**: data from related analyses done on an ad hoc basis.
	* **05_sv_analysis**: structural variant data for INTERVAL. This was indended for testing in TensorQTL but I ran out of time. Eugene Gardener has expresssed an interest in doing the analysis itself.
* **covid-19**: the short-term ACE2 analysis done for Adam Butterworth. Quick and dirty. Associated scripts are in the [covid19](covid-19) folder 
* **cram_files**: limited number of CRAM files for sample swap testing.
* **eQTLgen**: Downloaded eQTL results from eQTLgen for positive control tests
* **globus_phase2**: Initial download of phase II data from globus
* **globus_phase2_recalled**: Most up-to-date download of phase I and II data from globus. **NOTE: This is not all the data. A lot remains omn the Sanger system due to file sizes.**
* **hipsci_pipeline**: Marc Jan Bonder's Limix pipeline
* **matrix_eQTL**: Artika's Phase I matrix eQTL results for comparison purposes
* **mediation**: Tests of mediation analysis code
* **RNAseq**: Backup of orignal project folder from cardio cluster
* **scripts**: Analysis scripts, synced to this repository
* **vep**: Downloaded files from Enseml Variant Effect Predictor. Never quite got this working, sadly. 

Note: No cleanup of files has been done. It is my view that once a finalised set of TensorQTL eQTLs results is available, there is no reason to retain the old results, but I leave this decsion to whoever takes over the project. 