# Preprocessing of MobileInsight

## Overview

MobileInsight saves the captured information from
LTE messages in _.mi2log_ format.
The internal structure is that of a nested JSON object.

We provide all the captured messages for all devices
in the tabular format parquet.
We use the  function
[pandas.DataFrame.explode](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.explode.html)
to transform the original nested structure into a table.

The underlying nested structure is not preserved.
For a reference of the structure of all messages,
check [mobile_insight_structure.json](mobile_insight_structure.json).

## Installation

The directory [mi/cluster](./cluster) contains
files to create a container and submit MobileInsight jobs
in an HPC environment with
[Singularity](https://docs.sylabs.io/guides/3.5/user-guide/introduction.html) +
[Slurm](https://slurm.schedmd.com/documentation.html).
The files [requirements.txt](cluster/requirements.txt)
and [ubuntu-mi.def](cluster/ubuntu-mi.def) can be
reused for a Unix installation.

## Pipeline

1. [mi_parser_init_berlin.py](reader/mi_parser_init_berlin.py):
This extracts the messages from the mi2log files into
pickled dataframes with minimal processing.
2. [pkl_to_parquet.py](pkl_to_parquet.py):
Conversion to parquet after exploding the pickled dataframe.
3. [merge_mi.py](merge_mi.py): Merging per device.
