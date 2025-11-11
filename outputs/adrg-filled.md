---
title: "Analysis Data Reviewer’s Guide"
toc: true
toc-depth: 3
number-sections: true
---


<Sponsor Name>

Study CDISCPILOT01

ADRG Template Version ccyy-mm-dd


# Introduction

## Purpose

This document provides context for the analysis datasets and terminology that benefit from additional explanation beyond the Data Definition document (define.xml)for an invididual study.  In addition, this document provides a summary of ADaM conformance findings.  

## Acronyms

| Acronym | Translation |
| --- | --- |
| aCRF | Annotated Case Report Form |
| ADaM | Analysis Dataset Model |
| ADRG | Analysis Data Reviewer’s Guide |
| eCRF | Electronic Case Report Form |
| eDT | Electronic Data Transfer (e.g. central lab data, ECG vendor data, PK data, etc.) |
| IG | Implementation Guide |
| NA | Not Applicable |
| SDTM | Study Data Tabulation Model |
| TAUG | Therapeutic Area User Guide |

# Dataset Standards

| Standard or Dictionary | Versions Used |
| --- | --- |
| SDTM | SDTM Implementation Guide Version 3.1.2 ; SDTM Version 1.2 |
| Medical Events Dictionary | MedDRA version 8.0 |
| Define-XML | Define version 1.0.0 |

## Source Data Used for Analysis Dataset Creation

(insert your text here)

Include the following text if applicable: Please refer to the Legacy Data Conversion Plan and Report Appendix for additional details.

# Protocol Description

# Protocol Description

## ProtocolNumberand Title

Protocol Number: CDISCPILOT01

Protocol Title: Safety and Efficacy of the Xanomeline Transdermal Therapeutic System (TTS) in Patients with Mild to Moderate Alzheimer’s Disease

Protocol Versions:

The protocol was amended 3 times. For the first 2 amendments, changes were made to the ambulatory ECG assessments. Changes to the protocol-specified analyses are described in the statistical analysis plan.


## Protocol Designin Relation to ADaM Concepts

### 1) Protocol Objective

The primary objectives of this study were to determine if there is a statistically significant relationship between the change in both the ADAS-Cog (11) and CIBIC+ scores, and drug dose, and to document the safety profile of the xanomeline TTS.

### 2) Protocol Methodology

This was a prospective, randomized, multi-center, double-blind, placebo-controlled, parallel-group study. Subjects were randomized equally to placebo, xanomeline low dose, or xanomeline high dose. Subjects applied 2 patches daily and were followed for a total of 26 weeks.

### 3) Number of Subjects Planned in Total and by Group

300 subjects total (100 subjects in each of 3 groups)

### 4) Study Design Schema

The study included three treatment groups: placebo, xanomeline low dose (54 mg), and xanomeline high dose (81 mg). The treatment duration was 26 weeks, with assessments at various time points including Weeks 8, 16, and 24 for efficacy and safety evaluations.

# Analysis Considerations Related to Multiple Analysis Datasets

## Core Variables

Core variables are those that are represented across all/most analysis datasets.

| Variable Name | Variable Description |
| --- | --- |
| AGE | Age |
| AGEGR1 | Pooled Age Group 1 |
| ANL01FL | Analysis Flag 01 |
| AVAL | Analysis Value |
| AVISITN | Analysis Visit (N) |
| BASE | Baseline Value |
| BMIBL | Baseline BMI (kg/m^2) |
| CHG | Change from Baseline |
| CNSR | Censor |
| EFFFL | Efficacy Population Flag |
| HEIGHTBL | Baseline Height (cm) |
| ITTFL | Intent-To-Treat Population Flag |
| MMSETOT | MMSE Total |
| PARAM | Parameter |
| PARAMCD | Parameter Code |
| RACE | Race |
| STUDYID | Study Identifier |
| TRT01A | Actual Treatment for Period 01 |
| TRT01P | Planned Treatment for Period 01 |
| TRTP | Planned Treatment |
| TRTPN | Planned Treatment (N) |
| USUBJID | Unique Subject Identifier |
| WEIGHTBL | Baseline Weight (kg) |

## Treatment Variables

- ARM versus TRTxxP
Are the values of ARM equivalent in meaning to values of TRTxxP?
<Yes/No> (insert additional text hereor a mapping tableor a figure)

- ACTARM versus TRTxxA
If TRTxxA is used, then are the values of ACTARM equivalent in meaning to values of TRTxxA?
<Yes/No> (insert additional text hereor a mapping tableor a figure)

- Use of ADaM Treatment Variables in Analysis
Are both planned and actual treatment variables used in analysis?
<Yes/No> (insert additional texthereor a mapping tableor a figure)

- Use of ADaMTreatment Grouping Variables in Analysis
Are both planned and actual treatment grouping variables used in analysis?
<Yes/No> (insert additional text here or a mapping tableor a figure)

## Subject Issues that Require Special Analysis Rules

(insert your text hereor indicate that there were no subject issues to be documented)

## Use of Visit Windowing, Unscheduled Visits, and Record Selection

- Was windowing used in one or more analysis datasets?
<Yes/No> (insert additional texthere)

- Were unscheduled visits used in any analyses?
<Yes/No> (insert additional texthere)

- Additional Content of Interest
<SeeADRG Completion Guidelines foradditional content of interest, and includetext here or remove this text >.

## Imputation/Derivation Methods

- If date imputation was performed, were there rules that were used in multiple analysis datasets?
<Yes/No> (insert additional texthere)

- Additional Content of Interest
<SeeADRG Completion Guidelines foradditional content of interest, and includetext here or remove this text >.

# Analysis Data Creation and Processing Issues

## Split Datasets

(insert your textortablehereor indicate there are no split datasets)

## Data Dependencies

| dataset name | depend on the following datasets |
| --- | --- |
| ADADAS |  |
| ADAE | ADSL |
| ADLBC | ADSL |
| ADSL |  |
| ADTTE | ADAE, ADSL |

## Intermediate Datasets

(insert your text hereor indicate there are no intermediate datasets)

# Analysis Dataset Descriptions

## Overview

- Are data for screen failures, including data for run-in screening (for example, SDTM values of ARMCD=’SCRNFAIL’, or ‘NOTASSGN’) included in ADaM datasets?
<Yes/No> <insert additional text here>

- Are data taken from an ongoing study?
<Yes/No> <insert additional text here>
- Do the analysis datasets support all protocol-and statistical analysis plan-specified objectives?
<Yes/No>(insert additional text here)
- Include all objectives listed in the protocol or SAP which are not supported in the analysis datasets and the reason for their absence.

Additional Content of Interest

( SeeADRG Completion Guidelines foradditional content of interest, and includetext here or remove this text).

## Analysis Datasets

| Dataset
Dataset Label | Class | Efficacy | Safety | Baseline or other subject characteristics | PK/PD | Primary Objective | Structure |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Subject Level Analysis Dataset | ADSL |  |  | X |  |  | One observation per subject |
|  |  |  |  |  |  |  |  |

### 5.2.1ADSL – Subject Level Analysis Dataset

(insert your text here)

(insert date imputation rules if applicable)

### 5.2.xDataset – Dataset Label

(A new section is required for each dataset that is hyperlinked in the inventory table.  This section should be copied to create a new section for each dataset.  The text in the section header above must be edited to match the dataset name and label.

**Note that the header numbering in this section is NOT automatic.  The header number for each dataset must be manually edited.**)

# Data Conformance Summary

## Conformance Inputs

Specify the software name and version for the analysis datasets

(Text here)

Specify the version of the validation rules (i.e. CDISC, FDA) for the analysis datasets

(Text here)

Specify the software name and version for the define.xml

(Text here)

Specify the version of the validation rules (i.e. CDISC, FDA) for the define.xml

(Text here)

Provide any additionalcompliance evaluation information:

(Text here)

## Issues Summary

(insert your text here and/or use following table)

| Dataset | Diagnostic Message | Severity | Count | Explanation |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

# Submission of Programs

All programs for analysis datasets and primary and secondary efficacy resultsaresubmitted.   They were all createdon a <text here> platformusing<version>.The internal reference date used to create dates in ADaM datasets is<date>.

## ADaM Programs

| Program Name | Output | Macro Used |
| --- | --- | --- |
|  |  |  |

## Analysis Output Programs

| r_file | outputs | filters | variables |
| --- | --- | --- | --- |
| tlf-demographic.r | tlf-demographic-pilot5.out | ADSL.STUDYID == 'CDISCPILOT01'; ADSL.ITTFL == 'Y' | ADSL.AGE; ADSL.AGEGR1; ADSL.RACE; ADSL.HEIGHTBL; ADSL.WEIGHTBL; ADSL.BMIBL; ADSL.MMSETOT |
| tlf-efficacy.r | tlf-efficacy-pilot5.rtf | ADSL.ITTFL == 'Y'; ADLB.TRTPN %in% c(0, 81); ADLB.PARAMCD == 'GLUC'; ADLB.!is.na(AVISITN); ADLB1.AVISITN == 20; ADLB1.!is.na(CHG); ADLB1.!is.na(BASE); ADLB1.AVISITN == 0 | ADSL.STUDYID; ADSL.USUBJID; ADLB.BASE; ADLB.TRTPN; ADLB.PARAMCD; ADLB.AVISITN; ADLB.CHG; ADLB.AVAL |
| tlf-kmplot.r | pdf/tlf-kmplot-pilot5.pdf | ADSL.SAFFL == 'Y'; ADSL.STUDYID == 'CDISCPILOT01'; ADTEE.PARAMCD == 'TTDE'; ADTEE.STUDYID == 'CDISCPILOT01' | ADSL.STUDYID; ADSL.USUBJID; ADSL.TRT01A; ADTEE.AVAL; ADTEE.CNSR; ADTEE.PARAM; ADTEE.PARAMCD |
| tlf-primary.r | tlf-primary-pilot5.rtf | ADAS.EFFFL == 'Y'; ADAS.ITTFL == 'Y'; ADAS.PARAMCD == 'ACTOT'; ADAS.ANL01FL == 'Y'; ADSL.EFFFL == 'Y'; ADSL.ITTFL == 'Y' | ADAS.EFFFL; ADAS.ITTFL; ADAS.PARAMCD; ADAS.ANL01FL; ADAS.AVAL; ADAS.AVISITN; ADAS.CHG; ADSL.TRTP; ADSL.TRT01P |

## Open source R packages

| Package | Version | Description |
| --- | --- | --- |
| admiral | 1.3.0 | This R package provides tools for creating and managing Clinical Data Interchange Standards Consortium (CDISC) compliant Analysis Data Model (ADaM) datasets, which are essential for regulatory submissions to the FDA. |
| admiraldev | 1.3.1 | The package provides utility functions for checking data, variables, and conditions in 'admiral' and its extensions, as well as helper tools for maintaining documentation and testing. |
| assertthat | 0.2.1 | This package serves as an enhanced version of stopifnot(), allowing developers to easily declare and verify pre and post conditions for their code, while generating user-friendly error messages to improve understanding of any issues that arise. |
| backports | 1.5.0 | This package re-implements functions introduced or modified since R version 3.0.0, allowing use of newer features in older R installations through conditionally exported backports. |
| base64enc | 0.1-3 | This package offers flexible tools for handling base64 encoding, surpassing the capabilities of the outdated base64 package. |
| bit | 4.6.0 | This package offers efficient classes and methods for manipulating boolean and skewed boolean vectors, performing fast boolean operations, sorting integers, and executing set operations, along with foundational tools for range indexing and data compression. |
| bit64 | 4.6.0-1 | The 'bit64' package in R provides a way to handle 64-bit signed integers for precise numeric operations and database key management, while ensuring compatibility with various data structures and mathematical functions. |
| brew | 1.0-10 | The package provides a templating framework that allows users to combine text with R code for generating reports, using a syntax similar to that of PHP and other templating languages. |
| broom | 1.0.8 | The Broom package in R summarizes and organizes statistical model outputs into tidy data frames, facilitating easy reporting, plotting, and comparison of model results through its functions tidy(), glance(), and augment(). |
| cachem | 1.1.0 | This package provides key-value stores that automatically manage memory by pruning entries based on either total size limits or the age of the oldest object, ensuring efficient caching. |
| callr | 3.7.6 | This package enables users to execute computations in an isolated R process, ensuring that the current R session remains unaffected. |
| cellranger | 1.1.0 | This package provides helper functions for working with spreadsheets, specifically focusing on the "A1:D10" style of cell range specification. |
| checkmate | 2.3.2 | This package provides efficient argument checking and validation through a combination of R and C code to minimize execution time overhead. |
| cli | 3.6.5 | This package provides a collection of tools for creating visually appealing command line interfaces using semantic elements and customizable themes, along with support for various lower-level CLI components and ANSI color styles. |
| clipr | 0.8.0 | This package provides simple utility functions for reading from and writing to the clipboard across Windows, OS X, and X11 systems. |
| commonmark | 2.0.0 | This package utilizes the 'cmark' implementation to convert CommonMark markdown text into various formats such as HTML, LaTeX, and groff man, while also providing access to the markdown parse tree in XML format and supporting optional GFM extensions like tables and strikethrough. |
| cowplot | 1.2.0 | This package enhances the creation of publication-quality figures using 'ggplot2' by providing themes, alignment, arrangement functions, and tools for annotating plots and integrating images, originally developed for internal use in the Wilke lab. |
| cpp11 | 0.5.2 | The 'cpp11' package provides a safe and modern C++11 interface for interacting with R's C API, ensuring compliance with R's function semantics and support for ALTREP vectors. |
| crayon | 1.5.3 | The crayon package provides colored terminal output using ANSI color codes, allowing for customizable styles and easy integration with terminals and tools like Emacs ESS, but is now superseded by the cli package for new projects. |
| curl | 6.4.0 | This package provides bindings to 'libcurl' for making fully configurable HTTP/FTP requests, allowing responses to be processed in various ways, including in memory and on disk. |
| datasetjson | 0.3.0 | This package facilitates the reading, construction, and writing of CDISC Dataset JSON files, including validation against the Dataset JSON schema. |
| desc | 1.4.3 | This package provides tools for reading, writing, creating, and manipulating DESCRIPTION files, primarily designed for packages that interact with other R packages. |
| diffdf | 1.1.1 | This package offers functions for comparing two data frames, enabling users to identify and analyze differences between them while providing tools to troubleshoot discrepancies. |
| digest | 0.6.37 | This R package provides functions for creating hash digests of arbitrary objects using various algorithms, allowing for easy comparison of objects and the generation of hash-based message authentication codes, but is not intended for cryptographic purposes. |
| dplyr | 1.1.4 | This package offers a fast and reliable solution for manipulating data frame-like objects, enabling seamless operations on data both in memory and out of memory. |
| emmeans | 1.11.2 | The package provides tools for obtaining estimated marginal means (EMMs) and computing contrasts, trends, and comparisons for various linear, generalized linear, and mixed models, along with visualization options. |
| estimability | 1.5.1 | This package offers tools for assessing the estimability of linear functions of regression coefficients and includes methods for correctly handling non-estimable cases. |
| evaluate | 1.0.4 | This package provides tools for parsing and evaluating R commands, facilitating the recreation of command line behavior within R scripts. |
| fansi | 1.0.6 | This package provides R functions for string manipulation that effectively handle ANSI text formatting control sequences. |
| farver | 2.1.2 | The 'farver' package facilitates efficient and rapid conversion between various color spaces, enhancing performance compared to R's base color conversion functions. |
| fastmap | 1.2.0 | The package provides a fast implementation of data structures, including a key-value store, stack, and queue, while efficiently managing memory to prevent leaks associated with R's global symbol table. |
| forcats | 1.0.0 | This package provides tools for reordering and modifying factor levels in R, including methods for moving levels to the front, ordering by appearance, reversing, shuffling, collapsing rare levels, anonymizing, and manual recoding. |
| formatters | 0.5.11 | This package offers a framework for generating ASCII representations of complex tables and includes various formatters for converting values into display-friendly strings. |
| fs | 1.6.6 | This package provides a cross-platform interface for file system operations, leveraging the capabilities of the 'libuv' C library for efficient asynchronous I/O. |
| generics | 0.1.4 | The generics package in R provides a set of commonly used S3 generics to minimize package dependencies and conflicts. |
| ggplot2 | 3.5.2 | `ggplot2` is a data visualization package in R that allows users to create complex and customizable graphics using a declarative syntax based on the principles of "The Grammar of Graphics." |
| ggsurvfit | 1.1.0 | This R package simplifies the creation of publication-ready time-to-event (survival) endpoint figures by providing modular functions that integrate seamlessly with ggplot2 for customization and enhancement. |
| glue | 1.8.0 | This R package enables the use of interpreted string literals that facilitate multi-line string formatting, similar to features found in Python and Julia. |
| gtable | 0.3.6 | The 'gtable' package provides tools for creating, manipulating, and combining grid-based graphical objects ('grobs') to facilitate the construction of complex visual compositions in R. |
| haven | 2.5.5 | The package allows users to import foreign statistical formats into R using the ReadStat C library. |
| highr | 0.11 | This package provides syntax highlighting for R source code in LaTeX and HTML, with additional support for other programming languages through the highlight package. |
| hms | 1.1.3 | This package provides an S3 class for the storage and formatting of time-of-day values using the 'difftime' class as a basis. |
| htmltools | 0.5.8.1 | This package provides tools for generating and outputting HTML content efficiently. |
| huxtable | 5.6.0 | This package creates customizable styled tables for data presentation, allowing users to export to various formats such as HTML, LaTeX, and Excel, while also offering features for manipulating table aesthetics and generating regression tables. |
| isoband | 0.2.7 | This package provides a fast C++ implementation for generating contour lines and polygons from regularly spaced elevation data grids. |
| janitor | 2.2.1 | The janitor package in R simplifies data cleaning and formatting by providing user-friendly functions for formatting data frame column names, generating frequency tables and crosstabs, and exploring duplicate records, while adhering to the principles of the tidyverse. |
| jsonlite | 2.0.0 | The 'jsonlite' package in R provides efficient tools for parsing and generating JSON data, optimized for statistical applications and web interactions, while offering features for streaming, validating, and formatting JSON. |
| jsonvalidate | 1.5.0 | This package validates JSON data against specified JSON schemas using the Node.js libraries 'is-my-json-valid' or 'ajv', supporting drafts 04, 06, and 07 of the JSON schema standard. |
| knitr | 1.50 | This package facilitates dynamic report generation in R by utilizing Literate Programming techniques. |
| labeling | 0.4.3 | This package offers various functions for implementing different algorithms to label axes effectively in visualizations. |
| lattice | 0.22-7 | Lattice is a high-level data visualization system in R that provides a powerful and flexible framework for creating multi-dimensional plots, inspired by Trellis graphics, to effectively visualize complex datasets. |
| lifecycle | 1.0.4 | This package facilitates the management of exported functions throughout their life cycle by providing shared conventions, documentation badges, and user-friendly deprecation warnings. |
| lubridate | 1.9.4 | The 'lubridate' package in R provides user-friendly functions for parsing, manipulating, and performing algebraic operations on date-time objects and time spans. |
| magrittr | 2.0.3 | This package introduces a forward-pipe operator, %>%, that facilitates chaining commands by forwarding values or expression results into subsequent function calls, with flexible support for various right-hand side expressions. |
| MASS | 7.3-65 | This package provides functions and datasets designed to support the teachings of Venables and Ripley's "Modern Applied Statistics with S" (4th edition, 2002). |
| Matrix | 1.7-3 | This package provides a comprehensive hierarchy of sparse and dense matrix classes, supporting various matrix types and offering efficient methods for matrix operations by leveraging optimized libraries such as 'BLAS', 'LAPACK', and 'SuiteSparse'. |
| memoise | 2.0.1 | This package provides functionality to cache the results of a function, allowing for faster retrieval of previously computed values when the function is called with the same arguments. |
| metacore | 0.2.0 | This package creates an immutable container for metadata, enhancing programming activities and improving the functionality of other packages within the clinical programming workflow. |
| metatools | 0.1.6 | The package utilizes metadata information from 'metacore' objects to verify and construct metadata-related columns. |
| mgcv | 1.9-3 | This package implements generalized additive (mixed) models with various smoothing parameter estimation techniques, supporting advanced Bayesian inference and a range of smoothers and distributions beyond the exponential family. |
| mvtnorm | 1.3-3 | This package provides tools for computing multivariate normal and t probabilities, quantiles, random deviates, densities, and log-likelihoods for multivariate Gaussian models and Gaussian copulas, along with functions for handling interval-censored and exact data, including score functions and methods for managing lower triangular matrices. |
| nlme | 3.1-168 | This package allows users to fit and compare Gaussian linear and nonlinear mixed-effects models for analyzing complex data structures. |
| numDeriv | 2016.8-1.1 | This package provides methods for accurately calculating first and second order numerical derivatives using techniques such as Richardson's extrapolation and complex step derivatives, along with a simpler and faster finite difference method for real scalar and vector valued functions. |
| patchwork | 1.3.1 | The 'patchwork' package enhances 'ggplot2' by enabling the composition of multiple plots using mathematical operators, facilitating the creation of complex visualizations. |
| pharmaRTF | 0.1.4 | The package provides an enhanced RTF wrapper for generating high-quality RTF documents with customizable features, including multiple levels of titles and footnotes, landscape orientation, and detailed margin control, specifically tailored for creating regulatory submission reports using existing R table packages like 'Huxtable' or 'GT'. |
| pillar | 1.11.0 | This package offers 'pillar' and 'colonnade' generics that facilitate the formatting of data columns with a wide array of colors compatible with modern terminal displays. |
| pkgbuild | 1.4.8 | This package provides essential functions for building R packages, including locating necessary compilers across different platforms and configuring the PATH to enable R's access to these tools. |
| pkgconfig | 2.0.3 | This package allows for the configuration of options that are specific to individual packages, ensuring that changes apply only to the designated package without affecting others. |
| pkgload | 1.4.0 | The package facilitates the simulation of installing and attaching R packages, streamlining the development and iteration process within the 'devtools' framework. |
| prettyunits | 1.2.0 | This package provides human-readable formatting for various quantities, including time intervals, byte sizes, p-values, and colors, allowing for clearer data presentation. |
| processx | 3.8.6 | The 'processx' package in R provides tools to manage and interact with system processes in the background, allowing users to check their status, wait for completion, retrieve exit statuses, and read their output and errors through non-blocking connections. |
| progress | 1.2.3 | This package offers customizable progress bars for R, displaying features such as percentage, elapsed time, and estimated completion time, and is compatible with various environments including terminal, Emacs ESS, RStudio, Windows Rgui, and macOS R.app, along with a C++ API that works with or without Rcpp. |
| ps | 1.9.1 | This package allows users to list, query, and manipulate all system processes across Windows, Linux, and macOS platforms. |
| purrr | 1.1.0 | This R package provides a comprehensive and reliable set of tools for functional programming, enabling users to efficiently implement functional paradigms in their R projects. |
| r2rtf | 1.1.4 | This package facilitates the creation of polished, production-ready Rich Text Format (RTF) tables and figures with versatile formatting options. |
| R6 | 2.6.1 | The package provides a way to create lightweight reference classes in R, which support public and private members, inheritance, and do not rely on the S4 system. |
| RColorBrewer | 1.1-3 | This package offers color schemes for maps and other graphics, inspired by the designs of Cynthia Brewer as detailed on colorbrewer2.org. |
| Rcpp | 1.1.0 | The 'Rcpp' package facilitates seamless integration between R and C++ by providing R functions and C++ classes that allow for efficient data type interchange and the utilization of third-party libraries. |
| readr | 2.1.5 | The 'readr' package provides a fast and user-friendly solution for reading rectangular data formats such as CSV and TSV, while offering flexible parsing capabilities and handling unexpected data variations gracefully. |
| readxl | 1.4.5 | This R package enables the import of Excel files (both '.xls' and '.xlsx' formats) into R, utilizing embedded libraries to ensure cross-platform compatibility without external dependencies. |
| rematch | 2.0.0 | This package provides a simplified interface to the 'regexpr' function, enabling users to easily extract matches and captured groups from a regular expression applied to character vectors. |
| renv | 1.1.4 | The 'renv' package in R enables users to create and manage isolated project-specific libraries, track dependencies with a lockfile, and restore library states for enhanced project portability and reproducibility. |
| rlang | 1.1.6 | This package provides tools for manipulating base types and core R features, including the condition system and tidy evaluation, while integrating essential components of the Tidyverse. |
| roxygen2 | 7.3.2 | The `roxygen2` package facilitates the generation of R documentation, 'NAMESPACE' files, and collation fields directly from specially formatted comments in the code, streamlining the documentation process and ensuring it remains current with code changes. |
| rprojroot | 2.1.0 | This package provides robust and flexible methods for constructing file paths relative to a project's root directory, which is identified by specific criteria such as the presence of a designated file. |
| rtables | 0.6.13 | The 'rtables' package in R facilitates the creation of complex, multi-level reporting tables by providing a hierarchical framework for organizing and summarizing data, while supporting advanced tabulation features and a user-friendly pipeable interface. |
| scales | 1.4.0 | The package provides tools for mapping data to graphical aesthetics while automating the determination of breaks and labels for axes and legends. |
| snakecase | 0.11.1 | This package provides a versatile and user-friendly tool for parsing and converting strings into various case formats, such as snake_case and camelCase. |
| stringi | 1.8.7 | The 'stringi' package provides a comprehensive suite of tools for string manipulation and processing, including pattern searching, random string generation, case mapping, sorting, and Unicode normalization, all optimized for performance and portability across different locales and platforms. |
| stringr | 1.5.1 | This package provides a user-friendly interface with consistent functionality for string manipulation, leveraging the capabilities of the 'stringi' package while effectively handling missing values and zero-length vectors. |
| survival | 3.8-3 | This R package provides essential survival analysis functions, including the management of Surv objects, Kaplan-Meier and Aalen-Johansen curve calculations, Cox models, and parametric accelerated failure time models. |
| tibble | 3.3.0 | This package offers a 'tbl_df' class, known as a 'tibble', which enhances data frame usability with stricter validation and improved formatting features. |
| tidyr | 1.3.1 | `tidyr` is an R package designed to help create tidy data by providing tools for reshaping datasets, handling nested data structures, and managing missing values effectively. |
| tidyselect | 1.2.1 | This package provides a backend for creating select-like functions within your own R packages, ensuring consistency with the selection interfaces of the 'tidyverse'. |
| timechange | 0.3.0 | This package provides efficient routines for manipulating date-time objects while handling time zones, daylight saving times, and various date-time component modifications. |
| Tplyr | 1.2.1 | This package streamlines data manipulation processes to facilitate the creation of clinical summaries with a focus on traceability. |
| tzdb | 0.5.0 | This package offers an updated copy of the IANA Time Zone Database along with a C++ interface for the 'date' library, facilitating easy handling of dates, date-times, and time zone manipulations in R. |
| utf8 | 1.2.6 | This package facilitates the processing, validation, normalization, encoding, formatting, and display of 'UTF-8' encoded international text (Unicode). |
| V8 | 6.0.4 | The R package provides an interface to the V8 JavaScript engine, allowing users to execute JavaScript and WebAssembly code within R. |
| vctrs | 0.6.5 | This package introduces new concepts of prototype and size for enabling consistent type coercion and size recycling, while also addressing type- and size-stability to enhance the analysis of function interfaces. |
| viridisLite | 0.4.2 | The 'viridisLite' package provides color maps that enhance graph readability for individuals with color blindness and ensures perceptual uniformity, along with 'ggplot2' bindings for discrete and continuous color scales. |
| vroom | 1.6.5 | The 'vroom' package in R is designed for fast reading and writing of data files, such as CSV and TSV, by utilizing a quick indexing step and lazy value loading, along with parallel formatting for efficient asynchronous writing. |
| withr | 3.0.2 | This package provides a collection of functions that allow users to execute code with a modified global state in a safe and temporary manner. |
| xfun | 0.52 | This package provides a collection of miscellaneous functions that assist in facilitating various tasks commonly encountered in other packages maintained by Yihui Xie. |
| xml2 | 1.3.8 | This package provides bindings to 'libxml2' for XML data manipulation using a user-friendly interface based on 'XPath' expressions, along with support for XML schema validation. |
| xportr | 0.4.3 | This package provides tools for creating CDISC-compliant datasets and verifying their compliance with CDISC standards. |
| yaml | 2.3.10 | This R package implements the 'libyaml' YAML 1.1 parser and emitter, providing tools for reading and writing YAML data. |
| yyjsonr | 0.1.21 | This R package provides a fast JSON parser, generator, and validator that converts JSON, NDJSON, and GeoJSON data to and from R objects, supporting standard data types and structures. |

# Appendix

(insert text here or remove this section)

| Legacy Data Conversion Plan and Report Appendix |
| --- |

# Purpose

The purpose of this appendix is to document thetraceability ofkeyoutput analysis results with ADaM when the analysis results were generated using a legacy process.

Because of transformations required during ADaM conversion, some of the terms, categories and data formats used in the tabulation data have been translated into CDISC standard formats in the ADaM data.  This appendix identifies differences between the legacyanalysisand ADaM data, and explains how ADaM represents the equivalent data.

# Conversion Data Flow

The legacy data was converted to SDTM/ADaMas described in the following data flow diagram.

**Rationale:**

(Text here)

# Converted Data Summary

## Issues Encountered and Resolved

- (Text and/or table here)
- (Text and/or table here)
# Traceability Data Flow

The legacy data traceability from collection to submission is described in the following data flow diagram.

# Outstanding Issues

- (Text and/or table here)
- (Text and/or table here)
