import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
import numpy as np
from simulator import GeneticDriftSimulator

class DriftGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Genetic Drift Simulator")
        self.root.geometry("1100x900")

        self.sim = None
        self.is_running = False
        self.after_id = None
        
        self.pop_size_var = tk.IntVar(value=400)
        self.num_species_var = tk.IntVar(value=10)
        
        self.pop_size_var.trace_add("write", self.on_param_change)
        self.num_species_var.trace_add("write", self.on_param_change)

        self.mutation_enabled_var = tk.BooleanVar(value=False)
        self.mutation_rate_var = tk.DoubleVar(value=0.01)
        self.speed_var = tk.IntVar(value=100)
        self.delay_label_var = tk.StringVar(value="100 ms")
        self.speed_var.trace_add("write", lambda *args: self.delay_label_var.set(f"{self.speed_var.get()} ms"))
        
        self.num_gens_to_run = tk.IntVar(value=50)
        self.gen_count_var = tk.StringVar(value="Gen: 0")
        self.stop_on_fixation_var = tk.BooleanVar(value=True)

        self.mutation_rate_var.trace_add("write", self.update_sim_mutation_rate)
        self.mutation_enabled_var.trace_add("write", self.update_sim_mutation_rate)

        self.setup_ui()
        self.reset_sim()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        control_frame = ttk.Frame(self.root, padding="15")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        plot_frame = ttk.Frame(self.root, padding="10")
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure(".", font=("Segoe UI", 11))

        ttk.Label(control_frame, text="Population Size:").pack(pady=5)
        ttk.Entry(control_frame, textvariable=self.pop_size_var).pack(pady=5)

        ttk.Label(control_frame, text="Initial Species (max 20):").pack(pady=5)
        ttk.Entry(control_frame, textvariable=self.num_species_var).pack(pady=5)

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        mutation_frame = ttk.LabelFrame(control_frame, text="Mutation", padding="5")
        mutation_frame.pack(fill='x', pady=5)
        
        self.mut_check = ttk.Checkbutton(mutation_frame, text="Enable Mutation", variable=self.mutation_enabled_var, command=self.on_mutation_toggle)
        self.mut_check.pack(pady=5)

        ttk.Label(mutation_frame, text="Mutation Rate:").pack(pady=2)
        self.mut_entry = ttk.Entry(mutation_frame, textvariable=self.mutation_rate_var)
        self.mut_entry.pack(pady=2)
        
        self.on_mutation_toggle()

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        delay_frame = ttk.Frame(control_frame)
        delay_frame.pack(fill='x', pady=5)
        ttk.Label(delay_frame, text="Delay (ms):").pack(side=tk.LEFT)
        
        self.delay_entry = ttk.Entry(delay_frame, textvariable=self.speed_var, width=8)
        self.delay_entry.pack(side=tk.RIGHT)
        
        ttk.Scale(control_frame, from_=1, to=1000, variable=self.speed_var).pack(fill='x', pady=5)

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Checkbutton(control_frame, text="Stop on Fixation", variable=self.stop_on_fixation_var).pack(pady=5)

        ttk.Button(control_frame, text="Start/Pause", command=self.toggle_run).pack(pady=5, fill=tk.X)
        ttk.Button(control_frame, text="Step", command=self.step_sim).pack(pady=5, fill=tk.X)
        
        ttk.Label(control_frame, text="Run for N Generations:").pack(pady=5)
        ttk.Entry(control_frame, textvariable=self.num_gens_to_run).pack(pady=5)
        ttk.Button(control_frame, text="Run N Gens", command=self.run_n_gens).pack(pady=5, fill=tk.X)

        ttk.Button(control_frame, text="Reset", command=self.reset_sim).pack(pady=10, fill=tk.X)
        
        ttk.Label(control_frame, textvariable=self.gen_count_var, font=("Segoe UI", 14, "bold")).pack(pady=20)

        self.fig, (self.ax_grid, self.ax_graph) = plt.subplots(2, 1, figsize=(7, 9), gridspec_kw={'height_ratios': [1, 1]})
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.colors = plt.get_cmap('tab20').colors
        self.grid_colors = ['#eeeeee'] + list(self.colors)
        self.cmap = mcolors.ListedColormap(self.grid_colors)
        self.norm = mcolors.BoundaryNorm(np.arange(-1.5, 20.5, 1), len(self.grid_colors))

        self.img_grid = None
        self.lines_graph = {}

    def on_mutation_toggle(self):
        if self.mutation_enabled_var.get():
            self.mut_entry.state(['!disabled'])
        else:
            self.mut_entry.state(['disabled'])
        self.on_param_change()

    def on_param_change(self, *args):
        if self.sim and self.sim.generation == 0 and not self.is_running:
            try:
                p = self.pop_size_var.get()
                s = self.num_species_var.get()
                if p > 0 and s > 0:
                    self.reset_sim()
            except tk.TclError:
                pass

    def reset_sim(self):
        self.is_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        
        pop_size = self.pop_size_var.get()
        num_species = min(self.num_species_var.get(), 20)
        
        mutation_rate = self.mutation_rate_var.get() if self.mutation_enabled_var.get() else 0.0
        
        self.sim = GeneticDriftSimulator(pop_size, num_species, mutation_rate)
        
        self.ax_grid.clear()
        self.ax_graph.clear()
        self.img_grid = None
        self.lines_graph = {}
        
        self.update_gen_label()
        self.refresh_plots()

    def update_gen_label(self):
        self.gen_count_var.set(f"Gen: {self.sim.generation}")

    def update_sim_mutation_rate(self, *args):
        """Updates the simulator's mutation rate based on UI values."""
        if self.sim:
            try:
                rate = self.mutation_rate_var.get() if self.mutation_enabled_var.get() else 0.0
                self.sim.mutation_rate = rate
            except tk.TclError:
                pass

    def refresh_plots(self):
        side = int(np.sqrt(self.sim.population_size))
        if side * side < self.sim.population_size:
            side += 1
        
        grid_data = np.full(side * side, -1, dtype=int)
        grid_data[:self.sim.population_size] = self.sim.population
        grid_data = grid_data.reshape((side, side))
        
        if self.img_grid is None:
            self.img_grid = self.ax_grid.imshow(grid_data, cmap=self.cmap, norm=self.norm, interpolation='nearest')
            self.ax_grid.set_title("Population Grid")
            self.ax_grid.axis('off')
        else:
            self.img_grid.set_data(grid_data)

        history = self.sim.get_history_array()
        gens = np.arange(history.shape[0])
        
        for s in range(20):
            counts = history[:, s]
            if np.any(counts > 0) or s in self.lines_graph:
                if s not in self.lines_graph:
                    line, = self.ax_graph.plot(gens, counts, color=self.colors[s], label=f"Sp {s}")
                    self.lines_graph[s] = line
                else:
                    self.lines_graph[s].set_data(gens, counts)

        self.ax_graph.set_xlim(0, max(1, self.sim.generation))
        self.ax_graph.set_ylim(-self.sim.population_size * 0.02, self.sim.population_size * 1.02)
        
        self.ax_graph.set_title("Species Counts Over Time")
        self.ax_graph.set_xlabel("Generations")
        self.ax_graph.set_ylabel("Individuals")
        
        if self.sim.generation == 0:
            self.fig.tight_layout()
            
        self.canvas.draw_idle()

    def toggle_run(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.run_loop()

    def step_sim(self):
        self.sim.step()
        self.update_gen_label()
        self.refresh_plots()

    def run_n_gens(self):
        try:
            n = self.num_gens_to_run.get()
        except tk.TclError:
            return
            
        for _ in range(n):
            self.sim.step()
            if self.check_fixation():
                break
        self.update_gen_label()
        self.refresh_plots()

    def check_fixation(self):
        """Checks if any species has reached the total population size and pauses."""
        if not self.stop_on_fixation_var.get():
            return False
        counts = self.sim.get_counts()
        if np.any(counts == self.sim.population_size):
            self.is_running = False
            return True
        return False

    def run_loop(self):
        if self.is_running:
            self.sim.step()
            self.update_gen_label()
            self.refresh_plots()
            
            if self.check_fixation():
                return
                
            self.after_id = self.root.after(self.speed_var.get(), self.run_loop)

    def on_close(self):
        """Stops the simulation and closes the application."""
        self.is_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        plt.close(self.fig)
        self.root.destroy()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    gui = DriftGUI(root)
    root.mainloop()
