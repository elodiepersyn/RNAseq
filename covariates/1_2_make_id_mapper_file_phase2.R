# Reformat covariates for LIMIX pipeline
library(dplyr)
library(data.table)
setwd("C:/Users/Jonathan/Documents/INTERVAL_covars")

#dat <- fread("data_release_20190815/INTERVALdata_15AUG2019.csv", data.table = F)
ids <- fread("omicsMap.csv", data.table = F)
ids3 <- fread("omicsMap_P3.csv", data.table = F)
ids[which(ids == "", arr.ind = T)] <- NA
ids3[which(ids3 == "", arr.ind = T)] <- NA
allids <- full_join(ids, ids3)
#dat2 <- full_join(allids, dat)

# Read in ids from RNA seq data
rna_seq_ids <- fread("INTERVAL_RNA_technical_covariates_batch1-12_20200402.csv", data.table = F) %>%
  select(RNA_id = INT_ID, Batch)

# filter to just RNA id columns and rows with an RNA id
RNAcols <- grep("RNA", names(allids))
rnaids <- allids %>% 
  select(identifier, all_of(RNAcols), attendanceDate_p3) %>%
  mutate(RNAseq_gwasQC_24m = as.character(RNAseq_gwasQC_24m),
         RNAseq_gwasQC_48m = as.character(RNAseq_gwasQC_48m),
         RNAseq_gwasQC_p3 = as.character(RNAseq_gwasQC_p3))

RNArows <- rowSums(is.na(select(rnaids, -identifier, -attendanceDate_p3))) != ncol(select(rnaids, -identifier, -attendanceDate_p3)) # list rows with at least one non-NA RNA id
rnaids <- rnaids %>% 
  filter(RNArows)

# Make single column for RNA identifier
RNA_any <- NA
for (i in 1:nrow(rnaids)) {
  idsb <- as.character(select(rnaids, -identifier, -attendanceDate_p3)[i,])
  RNA_any[i] <- paste(unique(na.exclude(idsb)), collapse = ",")
}
rnaids$RNA_any <- RNA_any

#
rnaidsPhase <- rnaids %>% select(identifier, RNAseq_RAW_24m, RNAseq_RAW_48m, RNAseq_RAW_p3, RNA_any,attendanceDate_p3) 
rnaidsPhase$RNAphase <- ifelse(!is.na(rnaidsPhase$RNAseq_RAW_24m), 
                     "24m",
                     ifelse(!is.na(rnaidsPhase$RNAseq_RAW_48m), 
                            "48m",
                            ifelse(!is.na(rnaidsPhase$RNAseq_RAW_p3), 
                                   "p3",
                                   "none")))

# Output mapper file
rna_id_mapper <- rnaidsPhase %>%
  select(identifier, RNA_id = RNA_any, phase = RNAphase, attendanceDate_p3) %>% 
  filter(!is.na(identifier))

rna_id_mapper <- full_join(rna_id_mapper, rna_seq_ids) #%>%
#  filter(!is.na(batch)) # Remove this filter to allow unnumbered batch 5 ids through for now
write.csv(rna_id_mapper, "rna_id_mapper.csv", quote = F, row.names = F)