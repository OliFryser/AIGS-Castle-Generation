# AIGS-Castle-Generation

## Installation

We use conda for managing the python environment. We have provided the configuration file ``environment.yml`` for easy installation. We have dubbed our environment "fortify".

1. Open a conda shell
2. Run ``conda env create -f environment.yml`` or ``conda env update -f environment.yml``, if you have already created the environment.
3. Run ``conda activate fortify``.

## TODO

1. Build pathfinding graph on start and share between units. They will have the costs precalculated.
2. Seperate castle map and terrain map
3. Sever access in pathfinding graph where there is castle buildings
