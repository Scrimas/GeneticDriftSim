from __future__ import annotations
import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
import numpy as np
from simulator import GeneticDriftSimulator
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    from matplotlib.image import AxesImage
    from matplotlib.lines import Line2D


class DriftGUI:
    def __init__(self, root: ctk.CTk) -> None:
        self.root: ctk.CTk = root
        self.root.title("Genetic Drift Simulator")
        self.root.geometry("1100x900")

        self.sim: GeneticDriftSimulator | None = None
        self.is_running: bool = False
        self.after_id: str | None = None

        self.pop_size_var: tk.StringVar = tk.StringVar(value="400")
        self.num_alleles_var: tk.StringVar = tk.StringVar(value="10")

        self.pop_size_var.trace_add("write", self.on_param_change)
        self.num_alleles_var.trace_add("write", self.on_param_change)

        self.mutation_enabled_var: tk.BooleanVar = tk.BooleanVar(value=False)
        self.mutation_rate_var: tk.StringVar = tk.StringVar(value="0.01")
        self.speed_var: tk.IntVar = tk.IntVar(value=100)
        self.delay_label_var: tk.StringVar = tk.StringVar(value="100 ms")
        self.speed_var.trace_add(
            "write",
            lambda *args: self.delay_label_var.set(f"{self.speed_var.get()} ms"),
        )

        self.num_gens_to_run: tk.StringVar = tk.StringVar(value="50")
        self.gen_count_var: tk.StringVar = tk.StringVar(value="Generation: 0")
        self.stop_on_fixation_var: ctk.BooleanVar = ctk.BooleanVar(value=True)

        self.mutation_rate_var.trace_add("write", self.update_sim_mutation_rate)
        self.mutation_enabled_var.trace_add("write", self.update_sim_mutation_rate)

        self.font_header = ctk.CTkFont(family="Inter", size=14, weight="bold")
        self.font_label = ctk.CTkFont(family="Inter", size=12)

        mode = ctk.get_appearance_mode()
        self.mpl_bg = "#FFFFFF" if mode == "Light" else "#2B2B2B"
        self.mpl_text_main = "#333333" if mode == "Light" else "#F9F9FA"
        self.mpl_text_sub = "#555555" if mode == "Light" else "#CCCCCC"
        self.mpl_grid = "#F0F0F0" if mode == "Light" else "#444444"
        self.mpl_spine = "#E0E0E0" if mode == "Light" else "#444444"
        self.empty_cell = "#F9F9FA" if mode == "Light" else "#1A1A1A"

        self.card_bg = ("#FFFFFF", "#2B2B2B")
        self.text_main = ("#333333", "#F9F9FA")
        self.text_sub = ("#555555", "#CCCCCC")
        self.border_color = ("#E0E0E0", "#444444")

        self.setup_ui()
        self.reset_sim()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self) -> None:
        control_sidebar = ctk.CTkFrame(self.root, width=300, fg_color="transparent")
        control_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)

        plot_container = ctk.CTkFrame(
            self.root, fg_color=self.card_bg, corner_radius=12
        )
        plot_container.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=20
        )

        # --- 1st Card: Population Settings ---
        pop_card = ctk.CTkFrame(control_sidebar, corner_radius=8, fg_color=self.card_bg)
        pop_card.pack(fill=tk.X, pady=(0, 15))

        ctk.CTkLabel(
            pop_card,
            text="Population Size",
            font=self.font_header,
            text_color=self.text_main,
        ).pack(pady=(15, 0), padx=15, anchor="w")
        ctk.CTkEntry(
            pop_card,
            textvariable=self.pop_size_var,
            border_width=1,
            border_color=self.border_color,
            text_color=self.text_main,
            corner_radius=6,
        ).pack(pady=(5, 10), padx=15, fill=tk.X)

        ctk.CTkLabel(
            pop_card,
            text="Initial Alleles (Max 20)",
            font=self.font_label,
            text_color=self.text_sub,
        ).pack(pady=(5, 0), padx=15, anchor="w")
        ctk.CTkEntry(
            pop_card,
            textvariable=self.num_alleles_var,
            border_width=1,
            border_color=self.border_color,
            text_color=self.text_main,
            corner_radius=6,
        ).pack(pady=(5, 15), padx=15, fill=tk.X)

        # --- 2nd Card: Mutation Settings ---
        mut_card = ctk.CTkFrame(control_sidebar, corner_radius=8, fg_color=self.card_bg)
        mut_card.pack(fill=tk.X, pady=(0, 15))

        ctk.CTkLabel(
            mut_card,
            text="Mutation Dynamics",
            font=self.font_header,
            text_color=self.text_main,
        ).pack(pady=(15, 10), padx=15, anchor="w")

        self.mut_check = ctk.CTkSwitch(
            mut_card,
            text="Enable Mutation",
            font=self.font_label,
            text_color=self.text_main,
            variable=self.mutation_enabled_var,
            command=self.on_mutation_toggle,
        )
        self.mut_check.pack(pady=(0, 10), padx=15, anchor="w")

        ctk.CTkLabel(
            mut_card,
            text="Mutation Rate",
            font=self.font_label,
            text_color=self.text_sub,
        ).pack(pady=0, padx=15, anchor="w")
        self.mut_entry = ctk.CTkEntry(
            mut_card,
            textvariable=self.mutation_rate_var,
            border_width=1,
            border_color=self.border_color,
            text_color=self.text_main,
            corner_radius=6,
        )
        self.mut_entry.pack(pady=(5, 15), padx=15, fill=tk.X)
        self.on_mutation_toggle()

        # --- 3rd Card: Execution Controls ---
        ctrl_card = ctk.CTkFrame(
            control_sidebar, corner_radius=8, fg_color=self.card_bg
        )
        ctrl_card.pack(fill=tk.X, pady=(0, 15))

        # Delay Slider
        delay_frame = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        delay_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        ctk.CTkLabel(
            delay_frame,
            text="Delay Speed",
            font=self.font_label,
            text_color=self.text_main,
        ).pack(side=tk.LEFT)
        ctk.CTkLabel(
            delay_frame,
            textvariable=self.delay_label_var,
            font=self.font_label,
            text_color=("#1F6AA5", "#569CD6"),
        ).pack(side=tk.RIGHT)

        ctk.CTkSlider(ctrl_card, from_=1, to=1000, variable=self.speed_var).pack(
            fill=tk.X, padx=15, pady=(0, 15)
        )

        # Action Buttons
        ctk.CTkButton(
            ctrl_card,
            text="Start / Pause",
            font=self.font_header,
            command=self.toggle_run,
            height=40,
        ).pack(pady=5, padx=15, fill=tk.X)
        ctk.CTkButton(
            ctrl_card,
            text="Step 1 Gen",
            fg_color="transparent",
            border_width=1,
            border_color=self.border_color,
            text_color=self.text_main,
            command=self.step_sim,
        ).pack(pady=5, padx=15, fill=tk.X)

        # Run N Generations
        run_n_frame = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        run_n_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        ctk.CTkEntry(
            run_n_frame,
            textvariable=self.num_gens_to_run,
            text_color=self.text_main,
            border_color=self.border_color,
            width=60,
        ).pack(side=tk.LEFT, padx=(0, 10))
        ctk.CTkButton(
            run_n_frame,
            text="Run N Gens",
            fg_color="transparent",
            border_width=1,
            border_color=self.border_color,
            text_color=self.text_main,
            command=self.run_n_gens,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ctk.CTkCheckBox(
            ctrl_card,
            text="Auto-stop on Fixation",
            variable=self.stop_on_fixation_var,
            text_color=self.text_main,
            font=self.font_label,
        ).pack(pady=15, padx=15, anchor="w")

        # System Controls
        ctk.CTkButton(
            control_sidebar,
            text="Reset Simulation",
            fg_color="#E74C3C",
            hover_color="#C0392B",
            text_color="#FFFFFF",
            command=self.reset_sim,
        ).pack(pady=(10, 0), fill=tk.X)
        ctk.CTkLabel(
            control_sidebar,
            textvariable=self.gen_count_var,
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color=("#1F6AA5", "#569CD6"),
        ).pack(pady=25)

        # --- Matplotlib Integration ---
        self.fig, (self.ax_grid, self.ax_graph) = plt.subplots(
            2, 1, figsize=(7, 9), gridspec_kw={"height_ratios": [1, 1.2]}
        )
        self.fig.patch.set_facecolor(self.mpl_bg)
        self.canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(
            self.fig, master=plot_container
        )
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Apply Dynamic Theme to Graph
        self.ax_graph.set_facecolor(self.mpl_bg)
        self.ax_graph.spines["top"].set_visible(False)
        self.ax_graph.spines["right"].set_visible(False)
        self.ax_graph.spines["left"].set_color(self.mpl_spine)
        self.ax_graph.spines["bottom"].set_color(self.mpl_spine)
        self.ax_graph.grid(axis="y", color=self.mpl_grid, linestyle="-", linewidth=1)
        self.ax_graph.tick_params(colors=self.mpl_text_sub)

        self.colors: list[tuple[float, ...]] = list(plt.get_cmap("tab20").colors)
        self.grid_colors: list[str | tuple[float, ...]] = [
            self.empty_cell
        ] + self.colors
        self.cmap: mcolors.ListedColormap = mcolors.ListedColormap(self.grid_colors)
        self.norm: mcolors.BoundaryNorm = mcolors.BoundaryNorm(
            np.arange(-1.5, 20.5, 1), len(self.grid_colors)
        )

        self.img_grid: AxesImage | None = None
        self.lines_graph: dict[int, Line2D] = {}

    def on_mutation_toggle(self) -> None:
        if self.mutation_enabled_var.get():
            self.mut_entry.configure(state="normal", text_color=self.text_main)
        else:
            self.mut_entry.configure(
                state="disabled", text_color=("#AAAAAA", "#777777")
            )
        self.on_param_change()

    def on_param_change(self, *args: Any) -> None:
        if self.sim and self.sim.generation == 0 and not self.is_running:
            try:
                p = int(self.pop_size_var.get())
                s = int(self.num_alleles_var.get())
                if p > 0 and s > 0:
                    self.reset_sim()
            except ValueError:
                pass

    def reset_sim(self) -> None:
        self.is_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        try:
            pop_size = int(self.pop_size_var.get())
            num_alleles = min(int(self.num_alleles_var.get()), 20)
            mutation_rate = (
                float(self.mutation_rate_var.get())
                if self.mutation_enabled_var.get()
                else 0.0
            )
        except ValueError:
            return

        self.sim = GeneticDriftSimulator(pop_size, num_alleles, mutation_rate)

        self.ax_grid.clear()
        self.ax_graph.clear()
        self.img_grid = None
        self.lines_graph = {}

        self.update_gen_label()
        self.refresh_plots()

    def update_gen_label(self) -> None:
        if self.sim:
            self.gen_count_var.set(f"Generation: {self.sim.generation}")

    def update_sim_mutation_rate(self, *args: Any) -> None:
        if self.sim:
            try:
                rate = (
                    float(self.mutation_rate_var.get())
                    if self.mutation_enabled_var.get()
                    else 0.0
                )
                self.sim.mutation_rate = rate
            except ValueError:
                pass

    def refresh_plots(self) -> None:
        if not self.sim:
            return

        side: int = int(np.sqrt(self.sim.population_size))
        if side * side < self.sim.population_size:
            side += 1

        grid_data: np.ndarray[Any, np.dtype[np.int_]] = np.full(
            side * side, -1, dtype=int
        )
        grid_data[: self.sim.population_size] = self.sim.population
        grid_data = grid_data.reshape((side, side))

        if self.img_grid is None:
            self.img_grid = self.ax_grid.imshow(
                grid_data, cmap=self.cmap, norm=self.norm, interpolation="nearest"
            )
            self.ax_grid.set_title(
                "Population Distribution",
                fontdict={
                    "fontsize": 14,
                    "fontweight": "bold",
                    "color": self.mpl_text_main,
                },
                pad=15,
            )
            self.ax_grid.axis("off")
        else:
            self.img_grid.set_data(grid_data)

        history: np.ndarray[Any, np.dtype[np.int_]] = self.sim.get_history_array()
        gens: np.ndarray[Any, np.dtype[np.int_]] = np.arange(history.shape[0])

        self.ax_graph.set_facecolor(self.mpl_bg)
        self.ax_graph.spines["top"].set_visible(False)
        self.ax_graph.spines["right"].set_visible(False)
        self.ax_graph.spines["left"].set_color(self.mpl_spine)
        self.ax_graph.spines["bottom"].set_color(self.mpl_spine)
        self.ax_graph.grid(axis="y", color=self.mpl_grid, linestyle="-", linewidth=1)

        for s in range(20):
            counts: np.ndarray[Any, np.dtype[np.int_]] = history[:, s]
            if np.any(counts > 0) or s in self.lines_graph:
                if s not in self.lines_graph:
                    line: Line2D
                    (line,) = self.ax_graph.plot(
                        gens, counts, color=self.colors[s], label=f"Sp {s}", linewidth=2
                    )
                    self.lines_graph[s] = line
                else:
                    self.lines_graph[s].set_data(gens, counts)

        self.ax_graph.set_xlim(0, max(1, self.sim.generation))
        self.ax_graph.set_ylim(
            -self.sim.population_size * 0.02, self.sim.population_size * 1.05
        )

        self.ax_graph.set_title(
            "Alleles Distribution Over Time",
            fontdict={
                "fontsize": 14,
                "fontweight": "bold",
                "color": self.mpl_text_main,
            },
            pad=15,
        )
        self.ax_graph.set_xlabel(
            "Generations", color=self.mpl_text_sub, fontweight="bold"
        )
        self.ax_graph.set_ylabel(
            "Individuals", color=self.mpl_text_sub, fontweight="bold"
        )
        self.ax_graph.tick_params(colors=self.mpl_text_sub)

        if self.sim.generation == 0:
            self.fig.tight_layout()

        self.canvas.draw_idle()

    def toggle_run(self) -> None:
        self.is_running = not self.is_running
        if self.is_running:
            self.run_loop()

    def step_sim(self) -> None:
        if self.sim:
            self.sim.step()
            self.update_gen_label()
            self.refresh_plots()

    def run_n_gens(self) -> None:
        if not self.sim:
            return
        try:
            n = int(self.num_gens_to_run.get())
        except ValueError:
            return

        for _ in range(n):
            self.sim.step()
            if self.check_fixation():
                break
        self.update_gen_label()
        self.refresh_plots()

    def check_fixation(self) -> bool:
        if not self.sim or not self.stop_on_fixation_var.get():
            return False
        counts: np.ndarray[Any, np.dtype[np.int_]] = self.sim.get_counts()
        if np.any(counts == self.sim.population_size):
            self.is_running = False
            return True
        return False

    def run_loop(self) -> None:
        if self.is_running and self.sim:
            self.sim.step()
            self.update_gen_label()
            self.refresh_plots()

            if self.check_fixation():
                return

            self.after_id = self.root.after(self.speed_var.get(), self.run_loop)

    def on_close(self) -> None:
        self.is_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        plt.close(self.fig)
        self.root.destroy()
        self.root.quit()
