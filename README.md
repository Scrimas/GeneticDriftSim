# Genetic Drift Simulator

A Python-based simulation of genetic drift based on the Wright-Fisher model. This tool allows users to visualize how allele frequencies (represented as "species") change over time due to random sampling in a finite population.

## Features

- **Population Grid**: A visual representation of the population where each colored square represents an individual of a specific species.
- **Real-time Graphing**: Line graph showing the population count of each species over generations.
- **Configurable Parameters**:
  - Population Size
  - Number of Species (up to 20)
  - Mutation Rate (0.0 to 1.0)
- **Control Modes**:
  - **Start/Pause**: Run the simulation continuously at a configurable speed.
  - **Step**: Advance the simulation by exactly one generation.
  - **Run N Gens**: Advance the simulation by a set number of generations at once.
  - **Reset**: Re-initialize the population with equal distribution.

## Requirements

- Python 3.x
- NumPy
- Matplotlib

## Installation

If you don't have the dependencies installed, you can install them via pip:

```bash
pip install numpy matplotlib
```

## Usage

Run the simulator using the entry point:

```bash
python main.py
```

## How it Works

The simulation uses the **Wright-Fisher model**:
1. **Sampling**: The next generation is created by sampling $N$ times from the current generation with replacement. This simulates random reproduction.
2. **Mutation**: If a mutation rate is set, each new individual has a chance to mutate into any of the available species (chosen uniformly).
3. **Drift**: Over many generations, random sampling typically leads to the loss of genetic diversity (fixation of one species), unless mutations are frequent enough to maintain it.
