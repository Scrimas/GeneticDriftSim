from __future__ import annotations
import numpy as np
import numpy.typing as npt

class GeneticDriftSimulator:
    MAX_SPECIES: int = 20
    population: npt.NDArray[np.int_]
    history: list[npt.NDArray[np.int_]]
    generation: int

    def __init__(self, population_size: int, num_species: int, mutation_rate: float = 0.0) -> None:
        self.population_size: int = population_size
        self.num_species: int = num_species
        self.mutation_rate: float = mutation_rate
        self.reset()

    def reset(self) -> None:
        """Initializes population with equal distribution of species."""
        base_count: int = self.population_size // self.num_species
        remainder: int = self.population_size % self.num_species
        
        population: list[int] = []
        for i in range(self.num_species):
            count: int = base_count + (1 if i < remainder else 0)
            population.extend([i] * count)
        
        self.population = np.array(population)
        np.random.shuffle(self.population)
        
        self.history = [self.get_counts()]
        self.generation = 0

    def get_counts(self) -> npt.NDArray[np.int_]:
        """Returns the count of each possible species in the current population."""
        if self.population_size == 0:
            return np.zeros(self.MAX_SPECIES, dtype=int)
            
        counts: npt.NDArray[np.int_] = np.bincount(self.population, minlength=self.MAX_SPECIES)
        
        return counts[:self.MAX_SPECIES].astype(int)

    def step(self) -> None:
        """Advances the simulation by one generation (Wright-Fisher model)."""
        if self.population_size == 0:
            return

        indices: npt.NDArray[np.int_] = np.random.choice(self.population_size, size=self.population_size, replace=True)
        next_population: npt.NDArray[np.int_] = self.population[indices]

        if self.mutation_rate > 0:
            mutation_mask: npt.NDArray[np.bool_] = np.random.random(self.population_size) < self.mutation_rate
            if np.any(mutation_mask):
                new_species: npt.NDArray[np.int_] = np.random.randint(0, self.MAX_SPECIES, size=np.count_nonzero(mutation_mask))
                next_population[mutation_mask] = new_species

        self.population = next_population
        self.generation += 1
        self.history.append(self.get_counts())

    def get_history_array(self) -> npt.NDArray[np.int_]:
        """Returns history as a 2D numpy array (generations x species)."""
        return np.array(self.history)
