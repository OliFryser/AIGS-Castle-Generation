# AIGS-Castle-Generation

## Installation

We use conda for managing the python environment. We have provided the configuration file ``environment.yml`` for easy installation. We have dubbed our environment "fortify".

1. Open a conda shell
2. Run ``conda env create -f environment.yml`` or ``conda env update -f environment.yml``, if you have already created the environment.
3. Run ``conda activate fortify``.

## TODO for map elite

### TODO Oliver
- Implement crossover and removing ✅
- Implement random variation between variations ✅
- Implement better initial sampling with different mutation weights ✅
- Plotting of MaxFitness, coverage and QD-score ✅
- Plotting of archive ✅
- Restrict agent to "buildable area" ✅

- Loading from archive
- Saving during MapElites run

### TODO Jakob
- Better performance for pathfinding
- Better AI FSM
- Implement Archer unit
- Profiling of simulation


## Supervision

- Hard max for block behavior to limit infinite growth
- Removing block behavior may converge to just infinite growth
- Adding more enemy units per tower - essentially scaling defense vs. attacking units
  
- Baseline algorithm: Traditional EA - Do you have a good reference for this?

Multi objective mapelite
Multi emitter Map elite
