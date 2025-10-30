import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import networkx as nx
import matplotlib.patches as mpatches
import time
import threading

class RomaniaDFSTkinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🇷🇴 Romania DFS Pathfinder")
        self.root.geometry("1400x900")
        
        # Romania cities data
        self.cities = {
            'Arad': (1.2, 5.8), 'Bucharest': (8.5, 3.2), 'Craiova': (6.2, 2.5),
            'Drobeta': (4.5, 3.0), 'Eforie': (10.5, 2.0), 'Fagaras': (6.8, 5.0),
            'Giurgiu': (8.0, 2.0), 'Hirsova': (10.0, 3.5), 'Iasi': (9.5, 7.0),
            'Lugoj': (3.5, 4.0), 'Mehadia': (4.0, 3.3), 'Neamt': (8.0, 7.5),
            'Oradea': (2.5, 6.5), 'Pitesti': (7.2, 3.8), 'Rimnicu Vilcea': (5.8, 4.5),
            'Sibiu': (5.0, 5.2), 'Timisoara': (2.5, 4.5), 'Urziceni': (9.0, 3.8),
            'Vaslui': (9.2, 6.0), 'Zerind': (2.0, 6.0)
        }

        # Road connections
        self.roads = [
            ('Arad', 'Zerind', 75), ('Arad', 'Sibiu', 140), ('Arad', 'Timisoara', 118),
            ('Zerind', 'Oradea', 71), ('Oradea', 'Sibiu', 151),
            ('Timisoara', 'Lugoj', 111), ('Lugoj', 'Mehadia', 70), 
            ('Mehadia', 'Drobeta', 75), ('Drobeta', 'Craiova', 120),
            ('Craiova', 'Rimnicu Vilcea', 146), ('Craiova', 'Pitesti', 138),
            ('Sibiu', 'Fagaras', 99), ('Sibiu', 'Rimnicu Vilcea', 80),
            ('Rimnicu Vilcea', 'Pitesti', 97), ('Fagaras', 'Bucharest', 211),
            ('Pitesti', 'Bucharest', 101), ('Bucharest', 'Giurgiu', 90),
            ('Bucharest', 'Urziceni', 85), ('Urziceni', 'Hirsova', 98),
            ('Urziceni', 'Vaslui', 142), ('Hirsova', 'Eforie', 86),
            ('Vaslui', 'Iasi', 92), ('Iasi', 'Neamt', 87)
        ]

        # Build graph
        self.graph = nx.Graph()
        for city1, city2, dist in self.roads:
            self.graph.add_edge(city1, city2, weight=dist)

        # Color scheme
        self.colors = {
            'source': '#ff4500', 'destination': '#9370db', 'current': '#32cd32',
            'visited': '#ffd700', 'current_path': '#ff4444', 'final_path': '#1e90ff',
            'cities': '#2f4f4f', 'roads': '#a9a9a9', 'background': '#f0f8ff'
        }

        # Initialize state
        self.reset_state()
        self.setup_ui()

    def reset_state(self):
        """Reset algorithm state"""
        self.visited = set()
        self.stack = []
        self.current_city = None
        self.current_path = []
        self.found = False
        self.completed = False
        self.step_count = 0
        self.final_path = []
        self.source_city = None
        self.dest_city = None
        self.auto_running = False

    def setup_ui(self):
        """Create user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # City selection
        city_frame = ttk.Frame(control_frame)
        city_frame.pack(fill=tk.X, pady=5)

        ttk.Label(city_frame, text="🚩 Source:").pack(side=tk.LEFT, padx=(0, 10))
        self.source_var = tk.StringVar(value='Arad')
        self.source_combo = ttk.Combobox(city_frame, textvariable=self.source_var, 
                                        values=list(self.cities.keys()), state="readonly")
        self.source_combo.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(city_frame, text="🎯 Destination:").pack(side=tk.LEFT, padx=(0, 10))
        self.dest_var = tk.StringVar(value='Bucharest')
        self.dest_combo = ttk.Combobox(city_frame, textvariable=self.dest_var, 
                                      values=list(self.cities.keys()), state="readonly")
        self.dest_combo.pack(side=tk.LEFT)

        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(button_frame, text="🚀 Start DFS", command=self.start_dfs)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.step_btn = ttk.Button(button_frame, text="⏭️ Next Step", command=self.next_step)
        self.step_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.auto_btn = ttk.Button(button_frame, text="⚡ Auto Run", command=self.toggle_auto_run)
        self.auto_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.reset_btn = ttk.Button(button_frame, text="🔄 Reset", command=self.reset)
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.show_path_btn = ttk.Button(button_frame, text="🔵 Show Path", command=self.show_final_path)
        self.show_path_btn.pack(side=tk.LEFT)

        # Speed control
        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(fill=tk.X, pady=5)

        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=1.5)
        self.speed_scale = ttk.Scale(speed_frame, from_=0.5, to=3.0, variable=self.speed_var, 
                                   orient=tk.HORIZONTAL)
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # Status display
        status_frame = ttk.LabelFrame(control_frame, text="Status")
        status_frame.pack(fill=tk.X, pady=5)

        self.status_var = tk.StringVar(value="🇷🇴 Romania DFS Pathfinder - Select cities and click Start DFS")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                    wraplength=1000, justify=tk.LEFT)
        self.status_label.pack(fill=tk.X, padx=5, pady=5)

        self.info_var = tk.StringVar()
        self.info_label = ttk.Label(status_frame, textvariable=self.info_var, 
                                  wraplength=1000, justify=tk.LEFT)
        self.info_label.pack(fill=tk.X, padx=5, pady=5)

        # Matplotlib figure
        fig_frame = ttk.Frame(main_frame)
        fig_frame.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, fig_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Draw initial map
        self.draw_initial_map()

    def reset(self):
        """Reset visualization"""
        self.auto_running = False
        self.reset_state()
        self.status_var.set("🇷🇴 Romania DFS Pathfinder - Select cities and click Start DFS")
        self.update_info()
        self.draw_initial_map()

    def start_dfs(self):
        """Start DFS algorithm"""
        source = self.source_var.get()
        dest = self.dest_var.get()

        if source == dest:
            messagebox.showerror("Error", "Source and destination cannot be the same!")
            return

        self.reset_state()
        self.source_city = source
        self.dest_city = dest
        self.stack = [(source, [source])]

        self.status_var.set(f"Started DFS: {source} → {dest}")
        self.update_info()
        self.draw_map()

    def next_step(self):
        """Execute next DFS step"""
        if self.completed or not self.stack:
            if not self.found:
                self.status_var.set("Result: No path found!")
            return

        # DFS step
        self.current_city, self.current_path = self.stack.pop()
        self.step_count += 1

        # Check if destination reached
        if self.current_city == self.dest_city:
            self.found = True
            self.completed = True
            self.final_path = self.current_path
            distance = self.calculate_path_distance(self.final_path)
            self.status_var.set(f"🎉 Path Found!\nSteps: {self.step_count}\nDistance: {distance} km\nPath: {' → '.join(self.final_path)}")
            self.update_info()
            self.draw_map()
            return

        # Process current city
        if self.current_city not in self.visited:
            self.visited.add(self.current_city)

            # Add neighbors to stack
            for neighbor in self.graph.neighbors(self.current_city):
                if neighbor not in self.visited:
                    self.stack.append((neighbor, self.current_path + [neighbor]))

        self.status_var.set(f"Step {self.step_count}: Visiting {self.current_city}")
        self.update_info()
        self.draw_map()

    def toggle_auto_run(self):
        """Toggle auto run mode"""
        if not self.auto_running:
            self.auto_running = True
            self.auto_btn.config(text="⏹️ Stop Auto")
            self.auto_thread = threading.Thread(target=self.auto_run)
            self.auto_thread.daemon = True
            self.auto_thread.start()
        else:
            self.auto_running = False
            self.auto_btn.config(text="⚡ Auto Run")

    def auto_run(self):
        """Run DFS automatically"""
        if not self.stack and not self.completed:
            self.root.after(0, self.start_dfs)

        while self.auto_running and not self.completed and self.stack:
            self.root.after(0, self.next_step)
            time.sleep(2.0 / self.speed_var.get())
            if not self.auto_running:
                break

        self.auto_running = False
        self.root.after(0, lambda: self.auto_btn.config(text="⚡ Auto Run"))

    def show_final_path(self):
        """Show only final path"""
        if not self.found:
            self.status_var.set("Info: No path found yet. Run DFS first.")
            return

        self.draw_map(show_final_only=True)

    def calculate_path_distance(self, path):
        """Calculate total path distance"""
        total = 0
        for i in range(len(path) - 1):
            city1, city2 = path[i], path[i+1]
            for road in self.roads:
                if (road[0] == city1 and road[1] == city2) or (road[0] == city2 and road[1] == city1):
                    total += road[2]
                    break
        return total

    def update_info(self):
        """Update information panel"""
        info = f"Steps: {self.step_count} | Visited: {len(self.visited)} | Stack: {len(self.stack)}"
        if self.current_path:
            info += f"\nCurrent Path: {' → '.join(self.current_path)}"
        if self.found:
            info += f"\nFinal Path: {' → '.join(self.final_path)}"
        self.info_var.set(info)

    def draw_initial_map(self):
        """Draw initial map"""
        self.draw_map(show_algorithm=False)

    def draw_map(self, show_algorithm=True, show_final_only=False):
        """Draw the Romania map with highlighted features"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        ax.set_facecolor(self.colors['background'])
        ax.set_xlim(0.5, 11.5)
        ax.set_ylim(1.0, 8.5)
        ax.set_aspect('equal')
        ax.axis('off')

        # Draw backdrop roads
        for city1, city2, dist in self.roads:
            x1, y1 = self.cities[city1]
            x2, y2 = self.cities[city2]
            
            # Determine line color and width based on state
            line_color = self.colors['roads']
            line_width = 3
            alpha = 0.4
            
            # Highlight if this road is in current path
            if show_algorithm and self.current_path:
                for i in range(len(self.current_path) - 1):
                    if (city1 == self.current_path[i] and city2 == self.current_path[i+1]) or \
                       (city2 == self.current_path[i] and city1 == self.current_path[i+1]):
                        line_color = self.colors['current_path']
                        line_width = 6
                        alpha = 0.9
                        break
            
            # Shadow/glow underline
            ax.plot([x1, x2], [y1, y2], color='white', linewidth=line_width+4, alpha=0.2, zorder=1)
            # Main road line
            ax.plot([x1, x2], [y1, y2], 'o-', 
                    color=line_color, linewidth=line_width, alpha=alpha, markersize=0, zorder=2)
            
            # Distance label
            if show_final_only or alpha > 0.7:
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(mid_x, mid_y, str(dist), fontsize=9, fontweight='bold', ha='center', va='center',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor=line_color, alpha=0.85))

        # Draw all cities with basic styling
        for city, (x, y) in self.cities.items():
            # Base city dot
            ax.plot(x, y, 'o', markersize=10, markerfacecolor=self.colors['cities'],
                    markeredgecolor='black', markeredgewidth=1.5, alpha=0.7, zorder=3)
            
            # City name
            ax.text(x, y - 0.25, city, fontsize=9, fontweight='normal', ha='center', va='top',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#666', alpha=0.8))

        # Highlight visited cities
        for city in self.visited:
            x, y = self.cities[city]
            ax.plot(x, y, 'o', markersize=20, markerfacecolor='yellow', alpha=0.3, zorder=4)
            ax.plot(x, y, 's', markersize=12, markerfacecolor=self.colors['visited'],
                    markeredgecolor='orange', markeredgewidth=3, zorder=5)
            ax.text(x, y - 0.25, city, fontsize=10, fontweight='bold', ha='center', va='top',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', edgecolor='orange', alpha=0.9))

        # Highlight current exploration path
        if self.current_path and show_algorithm:
            for i in range(len(self.current_path) - 1):
                city1, city2 = self.current_path[i], self.current_path[i+1]
                x1, y1 = self.cities[city1]
                x2, y2 = self.cities[city2]
                
                ax.plot([x1, x2], [y1, y2], '-', color='red', linewidth=10, alpha=0.3, zorder=6)
                ax.plot([x1, x2], [y1, y2], '-', color=self.colors['current_path'], 
                        linewidth=6, alpha=0.9, zorder=7)
                
                ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle="->,head_length=0.8,head_width=0.8",
                                         lw=2, color='red', alpha=0.8))
            
            for city in self.current_path:
                x, y = self.cities[city]
                ax.plot(x, y, 'o', markersize=16, markerfacecolor=self.colors['current_path'],
                        markeredgecolor='darkred', markeredgewidth=4, zorder=8)

        # Highlight final path
        if self.found and (show_algorithm or show_final_only):
            for i in range(len(self.final_path) - 1):
                city1, city2 = self.final_path[i], self.final_path[i+1]
                x1, y1 = self.cities[city1]
                x2, y2 = self.cities[city2]
                
                ax.plot([x1, x2], [y1, y2], '-', color='white', linewidth=14, alpha=0.4, zorder=9)
                ax.plot([x1, x2], [y1, y2], '-', color=self.colors['final_path'], 
                        linewidth=10, alpha=1.0, zorder=10)
                
                ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle="->,head_length=1.0,head_width=1.0",
                                         lw=3, color='blue', alpha=0.9))
            
            for city in self.final_path:
                x, y = self.cities[city]
                ax.plot(x, y, 'D', markersize=14, markerfacecolor=self.colors['final_path'],
                        markeredgecolor='navy', markeredgewidth=4, zorder=11)
                ax.text(x, y - 0.25, city, fontsize=11, fontweight='bold', ha='center', va='top',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', edgecolor='blue', alpha=0.95))

        # Current city highlight
        if self.current_city and show_algorithm:
            x, y = self.cities[self.current_city]
            ax.plot(x, y, 'o', markersize=30, markerfacecolor='lime', alpha=0.4, zorder=12)
            ax.plot(x, y, 'o', markersize=20, markerfacecolor=self.colors['current'],
                    markeredgecolor='darkgreen', markeredgewidth=5, zorder=13)
            ax.text(x, y + 0.4, 'CURRENT', fontsize=12, fontweight='bold', ha='center', va='bottom',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor='lightgreen', edgecolor='green', alpha=0.9),
                    zorder=14)

        # Source and destination
        if self.source_city:
            x, y = self.cities[self.source_city]
            ax.plot(x, y, '^', markersize=22, markerfacecolor=self.colors['source'],
                    markeredgecolor='darkred', markeredgewidth=4, zorder=15)
            ax.text(x, y - 0.4, 'START', fontsize=12, fontweight='bold', ha='center', va='top',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor='red', edgecolor='darkred', alpha=0.9))
        
        if self.dest_city:
            x, y = self.cities[self.dest_city]
            ax.plot(x, y, 'v', markersize=22, markerfacecolor=self.colors['destination'],
                    markeredgecolor='navy', markeredgewidth=4, zorder=15)
            ax.text(x, y - 0.4, 'GOAL', fontsize=12, fontweight='bold', ha='center', va='top',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor='purple', edgecolor='navy', alpha=0.9))

        # Title and status
        title = f"🇷🇴 Romania Map - DFS Pathfinding: {self.source_city} → {self.dest_city}" 
        if show_final_only:
            title += " (Final Path)"
        elif self.found:
            title += " ✓ PATH FOUND"
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

        # Enhanced status info
        status_info = f"Step: {self.step_count} | Visited: {len(self.visited)} | Stack: {len(self.stack)}"
        if self.current_city:
            status_info += f"\n● Exploring: {self.current_city}"
        if self.current_path:
            status_info += f"\n🛣️ Current Path: {' → '.join(self.current_path)}"
        if self.found:
            distance = self.calculate_path_distance(self.final_path)
            status_info += f"\n🎉 PATH FOUND! Distance: {distance} km"
        elif self.completed:
            status_info += f"\n❌ NO PATH FOUND"
        
        ax.text(0.02, 0.98, status_info, transform=ax.transAxes, fontsize=11, fontweight='bold',
                verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", facecolor='#e1ffee', edgecolor='#2e8b57', alpha=0.95))

        # Legend
        self.create_legend(ax, show_final_only)
        
        self.fig.tight_layout()
        self.canvas.draw()

    def create_legend(self, ax, show_final_only=False):
        """Create proper legend"""
        if show_final_only:
            elements = [
                mpatches.Patch(color=self.colors['final_path'], label='Final Path'),
                mpatches.Patch(color=self.colors['source'], label='Source City'),
                mpatches.Patch(color=self.colors['destination'], label='Destination City'),
            ]
        else:
            elements = [
                mpatches.Patch(color=self.colors['source'], label='Source City'),
                mpatches.Patch(color=self.colors['destination'], label='Destination City'),
                mpatches.Patch(color=self.colors['current'], label='Current Node'),
                mpatches.Patch(color=self.colors['visited'], label='Visited Nodes'),
                mpatches.Patch(color=self.colors['current_path'], label='Current Path'),
                mpatches.Patch(color=self.colors['final_path'], label='Final Path'),
            ]

        ax.legend(handles=elements, loc='lower left', framealpha=0.9, fontsize=10,
                 bbox_to_anchor=(0.0, 0.0))

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = RomaniaDFSTkinterApp(root)
    root.mainloop()
