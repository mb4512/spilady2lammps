# spilady2lammps

Script for converting a SPILADY ascii file to a LAMMPS data file. The script also produces an example LAMMPS input file compatible with eam/fs potentials.

## Getting Started

git clone https://github.com/mb4512/spilady2lammps.git

### Prerequisites

This project was only written and tested with Python 3.9.1

Required libraries:
```
numpy (tested with 1.19.5)
```

## Running the code 

The script is run in serial mode using
```
python convert.py spilady.ascii path_to_eam_potential
```

The LAMMPS data and input files are saved in the `output` directory. Some example spilady ascii files are found in the `examples` sdirectory. An example eam/fs potential compatible with the `316SS.ascii` file can be downloaded from the NIST repository running the `getpot.sh` script.


