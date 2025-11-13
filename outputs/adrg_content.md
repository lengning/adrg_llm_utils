# ADRG Content Extraction Results

## Adsl Description

Subject-Level Analysis Dataset. one record per subject. Screen Failures are excluded.

## Date Imputation Rules

**Date Imputation Rules:**

- **Algorithm to derive ADAE.ASTDT**: AE.AESTDTC, converted to a numeric SAS date. Some events with partial dates are imputed in a conservative manner. If the day component is missing, a value of '01' is used. If both the month and day are missing no imputation is performed as these dates clearly indicate a start prior to the beginning of treatment. There are no events with completely missing start dates.

- **Algorithm to derive ADAE.ASTDTF**: ASTDTF='D' if the day value within the character date is imputed. Note that only day values needed to be imputed for this study.

## Source Data Description

Analysis datasets were derived from SDTM domains collected via electronic Case Report Forms (eCRF) and electronic Data Transfer (eDT) sources as documented in define.xml.

## Split Datasets

There are no split datasets in this submission.

## Intermediate Datasets

There are no intermediate datasets. All datasets created during processing are included in the final submission.

