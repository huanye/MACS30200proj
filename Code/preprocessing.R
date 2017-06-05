outpatients=NULL
for (i in 1:5){
fname=paste("DE1_0_2008_to_2010_Outpatient_Claims_Sample_",toString(i),'.csv',sep='')
data =read.csv(fname,header=T)
data = data[data$CLM_PMT_AMT>0,]
data$length = data[1,5]-data[1,4]+1
data$AVE_CLM_PMT = data$CLM_PMT_AMT/data$length
fname1=paste("DE1_0_2010_Beneficiary_Summary_File_Sample_",toString(i),'.csv',sep='')
fname2=paste("DE1_0_2009_Beneficiary_Summary_File_Sample_",toString(i),'.csv',sep='')
fname3=paste("DE1_0_2008_Beneficiary_Summary_File_Sample_",toString(i),'.csv',sep='')
bene2010 = read.csv(fname1,header = T)
bene2009 = read.csv(fname2,header = T)
bene2008 = read.csv(fname3,header = T)
bene = rbind(bene2008,bene2009,bene2010)
data_new = merge(data,bene,by = 'DESYNPUF_ID')
data_new$birth_year = data_new$BENE_BIRTH_DT%/%10000
outpatient = data_new[,c('AT_PHYSN_NPI','ICD9_DGNS_CD_1','HCPCS_CD_1','birth_year','BENE_SEX_IDENT_CD','AVE_CLM_PMT')]
outpatient = unique(outpatient)
row.names(outpatient)=NULL
outpatient = outpatient[complete.cases(outpatient),]
outpatients=rbind(outpatients,outpatient)
}
write.table(outpatients, file = "outpatient.csv",row.names=FALSE, col.names=FALSE, sep=",")