import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors

def calculate_pH(PaCO2, HCO3):
    pK = 6.1
    PCO2_conversion = 0.03
    pH = pK + np.log10(HCO3 / (PCO2_conversion * PaCO2))
    return pH

def classify_abg(pH, PaCO2, HCO3):
    if pH < 7.35:
        if PaCO2 > 45:
            if HCO3 > 26:
                return "Partially Compensated Respiratory Acidosis", 'Yellow'
            elif HCO3 < 22:
                return "Mixed Acidosis", 'Red'
            else:
                return "Uncompensated Respiratory Acidosis", 'Orange'
        elif HCO3 < 22:
            if PaCO2 < 35:
                return "Partially Compensated Metabolic Acidosis", 'Yellow'
            elif PaCO2 > 45:
                return "Mixed Acidosis", 'Red'
            else:
                return "Uncompensated Metabolic Acidosis", 'Orange'
        else:
            return "Undefined", 'gray'
    elif pH > 7.45:
        if PaCO2 < 35:
            if HCO3 < 22:
                return "Partially Compensated Respiratory Alkalosis", 'cyan'
            elif HCO3 > 26:
                return "Mixed Alkalosis", 'Purple'
            else:
                return "Uncompensated Respiratory Alkalosis", 'blue'
        elif HCO3 > 26:
            if PaCO2 > 45:
                return "Partially Compensated Metabolic Alkalosis", 'cyan'
            elif PaCO2 < 35:
                return "Mixed Alkalosis", 'Purple'
            else:
                return "Uncompensated Metabolic Alkalosis", 'Blue'
        else:
            return "Undefined", 'gray'
    else:
        if 35 <= PaCO2 <= 45 and 22 <= HCO3 <= 26:
            return "Normal", 'green'
        else:
            return "Undefined", 'gray'

def calculate_possible_PaCO2_HCO3(pH, PaCO2, HCO3, radius=2, num_points=100):
    pK = 6.1
    PCO2_conversion = 0.03

    angles = np.linspace(0, 2 * np.pi, num_points)
    dHCO3_values = np.zeros(num_points)
    dPaCO2_values = np.zeros(num_points)

    for i, angle in enumerate(angles):
        dHCO3 = radius * np.sin(angle)
        dPaCO2 = radius * np.cos(angle)

        dHCO3_values[i] = HCO3 + dHCO3
        dPaCO2_values[i] = PaCO2 + dPaCO2

    pH_values = pK + np.log10(dHCO3_values / (PCO2_conversion * dPaCO2_values))

    return pH_values, dHCO3_values

def plot_PaCO2_lines(ax):
    pK = 6.1
    PCO2_conversion = 0.03

    for PaCO2 in range(10, 110, 10):
        HCO3_values = np.linspace(5, 50, 100)
        pH_values = pK + np.log10(HCO3_values / (PaCO2 * PCO2_conversion))
        ax.plot(pH_values, HCO3_values, 'k', alpha=0.5)
        ax.text(pH_values[-1], HCO3_values[-1], f'{PaCO2}', fontsize=8, verticalalignment='bottom')


def create_widgets():
    global equation_label, classification_label, PaCO2_slider, HCO3_slider

    PaCO2_slider = tk.Scale(root, from_=10, to=100, orient=tk.HORIZONTAL, label="PaCO2", command=lambda x: update())
    PaCO2_slider.grid(row=0, column=0)

    HCO3_slider = tk.Scale(root, from_=5, to=50, orient=tk.HORIZONTAL, label="HCO3", command=lambda x: update())
    HCO3_slider.grid(row=1, column=0)

    equation_label = tk.Label(root, text="", font=("Arial", 10), width=30, wraplength=250)
    equation_label.grid(row=0, column=1)

    classification_label = tk.Label(root, text="", font=("Arial", 10), width=30, wraplength=250)
    classification_label.grid(row=1, column=1)


def update():
    global circle

    PaCO2 = PaCO2_slider.get()
    HCO3 = HCO3_slider.get()

    pH = calculate_pH(PaCO2, HCO3)
    equation_label.config(text=f"pH = {pH:.2f}")

    classification = classify_abg(pH, PaCO2, HCO3)
    classification_label.config(text=f"Classification: {classification[0]}")

    dot.set_data([pH], [HCO3])

    pH_values, HCO3_values = calculate_possible_PaCO2_HCO3(pH, PaCO2, HCO3, radius=2)  # You can change the radius to modify the size of the circle
    circle.set_data(pH_values, HCO3_values)

    plt.draw()



def create_graph():
    global dot

    fig, ax = plt.subplots()
    ax.set_xlim(6.2, 8.4)
    ax.set_ylim(0, 55)

    fig, ax = plt.subplots(figsize=(8, 8))  # Set custom width and height in inches
    ax.set_xlabel("pH")
    ax.set_ylabel("HCO3")

    dot, = ax.plot([], [], 'ro', markersize=10)
    circle, = ax.plot([], [], 'r-', linewidth=2)  # Add this line

    # Create grids
    pH_grid, HCO3_grid = np.meshgrid(np.linspace(6.2, 8.4, 200), np.linspace(5, 50, 200))
    pK = 6.1
    PCO2_conversion = 0.03
    PaCO2_grid = HCO3_grid / (10 ** (pH_grid - pK) * PCO2_conversion)

    color_map = np.empty((200, 200), dtype=object)
    for i in range(200):
        for j in range(200):
            color_map[i, j] = classify_abg(pH_grid[i, j], PaCO2_grid[i, j], HCO3_grid[i, j])[1]

    # Convert color_map to RGBA
    color_rgba = np.empty((200, 200, 4), dtype=np.float32)
    for i, color_name in enumerate(np.unique(color_map)):
        color_rgba[color_map == color_name] = mcolors.to_rgba(color_name)

    ax.imshow(color_rgba, extent=[6.2, 8.4, 5, 50], origin='lower', alpha=0.6, aspect='auto')

    # Add PaCO2 lines
    plot_PaCO2_lines(ax)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)  # Updated this line

    return canvas, circle

root = tk.Tk()
root.title("ABG Simulator")

create_widgets()

graph_canvas, circle = create_graph()

update()

root.mainloop()
