<h1 align="center">
  Genetic Drift Simulator
</h1>

## Overview

**Genetic Drift Simulator** is a Python-based simulation of genetic drift based on the Wright-Fisher model. This tool allows users to visualize how allele frequencies change over time due to random sampling in a finite population.

## Project Status

**Completed / Open to updates:** This repository provides a fully functional GUI for exploring population genetics. It was developed as a visualization tool to illustrate stochastic processes in evolutionary biology, specifically how random sampling error affects allele frequencies in small populations.

## Stochastic Modeling Approach

As a tool designed for educational visualization, this simulator prioritizes clarity and real-time interaction. By using **NumPy** for vectorized sampling and **Matplotlib** for dynamic plotting, it demonstrates how stochastic processes can lead to the fixation or loss of alleles in a population without the need for complex agent-based modeling. Every algorithmic choice was made to ensure the simulation remains responsive even at larger population sizes.

## Requirements & Compatibility

- **Python:** Python 3.8+
- **Libraries:** `numpy`, `matplotlib`, `customtkinter`
- **Operating Systems:** 
    - **Windows 11:** Tested
    - **Linux:** Tested, with some UI issues but works fine
    - **macOS:** Untested but should work fine as the script uses standard cross-platform libraries

## Core Features

- **Real-time Population Grid:** A visual representation of the population where each colored square represents an individual of a specific allele.
- **Dynamic Frequency Graphing:** Line graph showing the population count of each allele over generations, updated in real-time.
- **Interactive Control Suite:** Start, pause, step, or run a specific number of generations to observe drift at your own pace.
- **Stochastic Mutation Engine:** Toggleable mutation rates to observe how new genetic variation interacts with random drift.
- **Automated Fixation Detection:** Option to automatically pause the simulation once a single allele has achieved fixation.

## Architecture

The directory structure is organized to separate the mathematical model from the graphical user interface:

```text
GeneticDriftSim/
├── gui.py              # CustomTkinter-based UI and Matplotlib rendering
├── main.py             # Main entry point and system configuration
└── simulator.py        # Wright-Fisher model logic and NumPy backend
```

## Usage

1. **Clone repository**

```bash
git clone https://github.com/Scrimas/GeneticDriftSim
```

2. **Install Dependencies:** Ensure you have the required libraries installed:

```bash
pip install numpy matplotlib customtkinter
```

3. **Run Simulator:** Execute the main script from the root directory:

```bash
python main.py
```

4. **Interact:** Adjust parameters in the left panel and use the control buttons to start the simulation.

## License

This project is licensed under the MIT License.
