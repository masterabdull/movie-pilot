import tkinter as tk

# Function to calculate and display result
def show_result():
    voltage_mv = 70              # in millivolts
    thickness_m = 1.0e-8         # in meters
    voltage_v = voltage_mv / 1000
    electric_field = voltage_v / thickness_m

    result = f"E = V / d = ({voltage_v:.2e} V) / ({thickness_m:.1e} m)\n"
    result += f"Electric Field Magnitude: {electric_field:.2e} V/m"

    result_label.config(text=result, foreground="blue")

# GUI Setup
root = tk.Tk()
root.title("Electric Field Calculator - Umar Rajab Abdullahi (24120111107)")
root.geometry("600x350")
root.configure(bg="#e6f2ff")

# Heading
heading = tk.Label(
    root, text="Umar Rajab Abdullahi – 24120111107",
    font=("Helvetica", 16, "bold"), bg="#e6f2ff", fg="#003366"
)
heading.pack(pady=20)

# Description
desc = tk.Label(
    root,
    text="Given:\nResting Potential = 70 mV\nMembrane Thickness = 1.0 × 10⁻⁸ m",
    font=("Arial", 12), bg="#e6f2ff"
)
desc.pack(pady=10)

# Result Label (initially empty)
result_label = tk.Label(root, text="", font=("Arial", 13), bg="#e6f2ff")
result_label.pack(pady=20)

# Calculate button
btn = tk.Button(
    root, text="Calculate Electric Field", command=show_result,
    font=("Arial", 12), bg="#003366", fg="white", padx=10, pady=5
)
btn.pack()

# Start the GUI loop
root.mainloop()
