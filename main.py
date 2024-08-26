import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from matplotlib.figure import Figure

G = nx.Graph()

nodes = [
    "Gate 1", "Gate 2", "Gate 3", "Gate 4", "Gate 5", "Gate 6", "Gate 7",
    "Gate 8", "Gate 9", "Gate 10", "Gate 11", "Gate 12", "Gate 13", "Gate 14", "Gate 15",
    "Restaurant A", "Restaurant B", "Restaurant C", "Shuttle Stop 1", "Shuttle Stop 2",
    "Immigration", "Baggage Claim", "Help Desk", "Duty Free", "Drug Store", "Smoking Lounge"
]
G.add_nodes_from(nodes)

edges = [
    ("Gate 1", "Restaurant A", 5),
    ("Gate 1", "Shuttle Stop 1", 2),
    ("Shuttle Stop 1", "Gate 2", 7),
    ("Gate 2", "Restaurant B", 4),
    ("Gate 2", "Shuttle Stop 2", 6),
    ("Shuttle Stop 2", "Gate 3", 8),
    ("Gate 3", "Restaurant C", 3),
    ("Gate 3", "Immigration", 10),
    ("Immigration", "Baggage Claim", 5),
    ("Baggage Claim", "Help Desk", 2),
    ("Help Desk", "Duty Free", 4),
    ("Duty Free", "Drug Store", 6),
    ("Drug Store", "Smoking Lounge", 3),
    ("Smoking Lounge", "Gate 4", 7),
    ("Gate 4", "Gate 5", 5),
    ("Gate 5", "Gate 6", 4),
    ("Gate 6", "Gate 7", 8),
    ("Gate 7", "Gate 8", 2),
    ("Gate 8", "Gate 9", 6),
    ("Gate 9", "Gate 10", 4),
    ("Gate 10", "Gate 11", 7),
    ("Gate 11", "Gate 12", 3),
    ("Gate 12", "Gate 13", 8),
    ("Gate 13", "Gate 14", 5),
    ("Gate 14", "Gate 15", 6),
]
G.add_weighted_edges_from(edges)

pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)

def find_shortest_path(graph, source, destination):
    try:
        path = nx.dijkstra_path(graph, source, destination, weight='weight')
        distance = nx.dijkstra_path_length(graph, source, destination, weight='weight')
        return path, distance
    except nx.NetworkXNoPath:
        return None, None

class AirportNavigationApp(tk.Tk):
    def _init_(self, graph):
        super()._init_()
        self.title("Airport Navigation System")
        self.geometry("1000x700")
        self.graph = graph
        self.pos = pos  # Use the precomputed layout positions
        self.boarding_time = None

        self.figure = Figure(figsize=(12, 8))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)

        self.create_widgets()
        self.plot_graph()
        self.update_clock()

    def create_widgets(self):
      
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(control_frame, text="Source Location:", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.source_var = tk.StringVar()
        self.source_entry = tk.OptionMenu(control_frame, self.source_var, *self.graph.nodes)
        self.source_entry.config(width=20)
        self.source_var.set("Gate 1")  # Default value
        self.source_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(control_frame, text="Destination Location:", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.destination_var = tk.StringVar()
        self.destination_entry = tk.OptionMenu(control_frame, self.destination_var, *self.graph.nodes)
        self.destination_entry.config(width=20)
        self.destination_var.set("Gate 15")  # Default value
        self.destination_entry.grid(row=1, column=1, padx=5, pady=5)

        boarding_button = tk.Button(control_frame, text="Enter Boarding Time", font=("Helvetica", 12, "bold"), command=self.prompt_boarding_time)
        boarding_button.grid(row=2, column=1, padx=5, pady=5, sticky='w')  # Position the button below the destination entry

        calculate_button = tk.Button(control_frame, text="Find Shortest Path", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", command=self.calculate_path)
        calculate_button.grid(row=2, column=2, rowspan=2, padx=10, pady=5)

        self.output_area = tk.Text(self, height=5, width=100, state='disabled', font=("Helvetica", 12))
        self.output_area.pack(pady=10)

        self.clock_label = tk.Label(self, text="", font=("Helvetica", 14))
        self.clock_label.pack(anchor='ne', padx=20, pady=10)

        self.time_remaining_label = tk.Label(self, text="", font=("Helvetica", 12), fg='red')
        self.time_remaining_label.pack(anchor='ne', padx=20, pady=10)  # Positioned below the clock label

        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def prompt_boarding_time(self):
        boarding_time_str = simpledialog.askstring("Boarding Time", "Enter Boarding Gate Time (HH:MM):")
        if boarding_time_str:
            self.boarding_time = boarding_time_str
            self.update_remaining_time()  # Start the countdown

    def update_remaining_time(self):
        if self.boarding_time:
            try:
                boarding_time = datetime.strptime(self.boarding_time, "%H:%M")
                current_time = datetime.now()
                boarding_time_today = current_time.replace(hour=boarding_time.hour, minute=boarding_time.minute, second=0, microsecond=0)
                if boarding_time_today < current_time:
                    boarding_time_today += timedelta(days=1)  # If time has already passed today, assume next day
                time_remaining = boarding_time_today - current_time
                self.time_remaining_label.config(text=f"Time Remaining for Boarding: {str(time_remaining).split('.')[0]}")
                self.after(1000, self.update_remaining_time)  # Update every second
            except ValueError:
                messagebox.showerror("Error", "Invalid time format. Please enter in HH:MM format.")

    def calculate_path(self):
        source = self.source_var.get()
        destination = self.destination_var.get()

        if source == destination:
            messagebox.showwarning("Warning", "Source and Destination cannot be the same.")
            return

        path, distance = find_shortest_path(self.graph, source, destination)

        self.output_area.config(state='normal')
        self.output_area.delete(1.0, tk.END)

        if path:
            self.output_area.insert(tk.END, f"Shortest path from {source} to {destination}:\n")
            self.output_area.insert(tk.END, f"{' -> '.join(path)}\n")
            self.output_area.insert(tk.END, f"Total Distance: {distance} metres\n")
            self.plot_graph(path)  # Highlight the path on the graph
        else:
            self.output_area.insert(tk.END, "No path found between the selected locations.\n")
            self.plot_graph()  # Plot without highlighting

        self.output_area.config(state='disabled')

    def plot_graph(self, path=None):
        self.ax.clear()  # Clear previous plots

        node_colors = []
        for node in self.graph.nodes:
            if "Gate" in node:
                node_colors.append('#8BC34A')  # Light Green
            elif "Restaurant" in node:
                node_colors.append('#FF9800')  # Orange
            elif node == "Smoking Lounge":
                node_colors.append('#F44336')  # Red
            elif "Shuttle Stop" in node:
                node_colors.append('#9C27B0')  # Purple
            else:
                node_colors.append('#03A9F4')  # Light Blue

        nx.draw_networkx_edges(self.graph, self.pos, ax=self.ax, edge_color='gray', width=1)
        nx.draw_networkx_nodes(self.graph, self.pos, ax=self.ax, node_color=node_colors, node_size=800)
        nx.draw_networkx_labels(self.graph, self.pos, ax=self.ax, font_size=8, font_weight='bold')

        if path:
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_edges(self.graph, self.pos, edgelist=path_edges, ax=self.ax, edge_color='#FF5722', width=3)
            nx.draw_networkx_nodes(self.graph, self.pos, nodelist=path, ax=self.ax, node_color='#FFC107', node_size=900)

        self.ax.set_title('Airport Navigation Map', fontsize=16, fontweight='bold')
        self.ax.axis('off')
        self.canvas.draw()

    def update_clock(self):
        now = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)  # Update clock every second

if _name_ == "_main_":
    app = AirportNavigationApp(G)
    app.mainloop()
