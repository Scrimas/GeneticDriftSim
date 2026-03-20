import numpy as np

class GeneticDriftSimulator:
    MAX_SPECIES = 20

    def __init__(self, population_size, num_species, mutation_rate=0.0):
        self.population_size = population_size
        self.num_species = num_species
        self.mutation_rate = mutation_rate
        self.reset()

    def reset(self):
        """Initializes population with equal distribution of species."""
        base_count = self.population_size // self.num_species
        remainder = self.population_size % self.num_species
        
        population = []
        for i in range(self.num_species):
            count = base_count + (1 if i < remainder else 0)
            population.extend([i] * count)
        
        self.population = np.array(population)
        np.random.shuffle(self.population)
        
        self.history = [self.get_counts()]
        self.generation = 0

    def get_counts(self):
        """Returns the count of each possible species in the current population."""
        counts = np.zeros(self.MAX_SPECIES, dtype=int)
        unique, counts_found = np.unique(self.population, return_counts=True)
        for u, c in zip(unique, counts_found):
            if u < self.MAX_SPECIES:
                counts[u] = c
        return counts

    def step(self):
        """Advances the simulation by one generation (Wright-Fisher model)."""
        if self.population_size == 0:
            return

        indices = np.random.choice(self.population_size, size=self.population_size, replace=True)
        next_population = self.population[indices]

        if self.mutation_rate > 0:
            mutation_mask = np.random.random(self.population_size) < self.mutation_rate
            if np.any(mutation_mask):
                new_species = np.random.randint(0, self.MAX_SPECIES, size=np.count_nonzero(mutation_mask))
                next_population[mutation_mask] = new_species

        self.population = next_population
        self.generation += 1
        self.history.append(self.get_counts())

    def get_history_array(self):
        """Returns history as a 2D numpy array (generations x species)."""
        return np.array(self.history)
