# DaliLite.v5

Standalone program for protein structural alignment and database search,
as described in:

> Holm L (2019) Benchmarking fold detection by DaliLite v.5.
> *Bioinformatics* 35, 5326-5327.
> https://doi.org/10.1093/bioinformatics/btz536

The underlying structural comparison algorithm is described in:

> Holm L, Sander C (1993) Protein structure comparison by alignment of
> distance matrices. *J. Mol. Biol.* 233, 123-138.

## Contents

| Path | Description |
|------|-------------|
| `bin/` | Compiled executables and Makefile |
| `src/` | Source code |
| `DAT/` | Data files required at runtime |
| `toy_PDB/` | Small PDB files for testing |
| `test.csh` | Test script |
| `test_output/` | Expected output for comparison |
| `MANUAL.html` | Full user manual |
| `LICENCE` | Licence |

## Installation

    cd DaliLite.v5/bin
    make                  # ignore warnings

For MPI parallel execution (requires OpenMPI — check `OPENMPI_PATH` in `Makefile`):

    make parallel

Tested on Red Hat Linux with gcc 4.8.5 and OpenMPI 1.10.7.

## Test

    cd DaliLite.v5
    ./test.csh
    # compare output to ./test_output/

The test script assumes `blastp` and `makeblastdb` are on your `PATH`.
If not, download BLAST+ from:
https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/

For MPI: set `NP=2` in `test.csh` and rerun.

## Usage

Import a PDB structure into the local database:

    bin/import.pl

Run structural alignment or database search:

    bin/dali.pl [-h]

The `-h` flag prints full usage information. See `MANUAL.html` for details.

## Citation

If you use DaliLite in your work, please cite:

Holm L (2019) Benchmarking fold detection by DaliLite v.5.
*Bioinformatics* 35, 5326-5327.
https://doi.org/10.1093/bioinformatics/btz536
