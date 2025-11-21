# AIGS-Castle-Generation

## Installation

We use conda for managing the python environment. We have provided the configuration file ``environment.yml`` for easy installation. We have dubbed our environment "fortify".

1. Open a conda shell
2. Run ``conda env create -f environment.yml`` or ``conda env update -f environment.yml``, if you have already created the environment.
3. Run ``conda activate fortify``.

## Ask supervisor

- How do we manage castle growth - limiting how far it can grow? Do not place outside range?
- Starting point - Keep block or predefined?


## TODO for map elite

- Implement Crossover
- Implement removing from end of branch
- Implement random variation between Substitute, add and crossover
- Better initial sampling
- Loading from archive
- Saving during MapElites run
- Visualize Archive


- MaxFitness
- Coverage
- QD-score - Average fitness of everything in archive

- 10x10 archive - can visualize
- 1000 iterations