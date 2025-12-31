# AIGS-Castle-Generation

This project implements a castle builder and combat simulation, as well as two evolutionary algorithms that can generate new castles.

## Installation

We use conda for managing the python environment. We have provided the configuration file ``environment.yml`` for easy installation. We have dubbed our environment "fortify".

1. Open a conda shell
2. Run ``conda env create -f environment.yml`` or ``conda env update -f environment.yml``, if you have already created the environment.
3. Run ``conda activate fortify``.


## Running the simulation

Run the simulation from the ``CastleGenerationSimulation`` folder, to ensure all relative paths work as intended. Use a conda shell and write ``python main.py``.

Through the file ``CastleGenerationSimulation\conf\config.yaml``, the user can specify the ``mode`` to run the simulation in. We support four modes:

- interactive: The combat simulation. Click *space* to start the simulation.
- mapElites: The mapElites runner.
- conventionalEA: The conventional evolutionary algorithm.
- terrainBuilder: A tool for editing terrain maps. Basic heightmaps can be generated with ``HelperScripts/LevelGenerator/main.py``

Each of the modes have their own configuration options as well. They should be fairly intuitive.