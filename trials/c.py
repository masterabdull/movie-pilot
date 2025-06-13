import tkinter as tk
from tkinter import messagebox
import json
import os

# Movies and time slots (hardcoded)
MOVIES = {
    "The Matrix": ["10:00 AM", "2:00 PM", "6:00 PM"],
    "Inception": ["12:00 PM", "4:00 PM", "8:00 PM"],
    "Interstellar": ["11:00 AM", "3:00 PM", "7:00 PM"]
}

ROWS, COLS = 5, 8  # 40 seats
BOOKING_FILE = 'bookings.json'


def load_bookings():
    if not os.path.exists(BOOKING_FILE):
        with open(BOOKING_FILE, 'w') as f:
            json.dump({}, f)
    with open(BOOKING_FILE, 'r') as f:
        return json.load(f)


def save_bookings(bookings):
    with open(BOOKING_FILE, 'w') as f:
        json.dump(bookings, f, indent=2)


class BookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Panaview Movie Ticket Booking")

        self.selected_movie = tk.StringVar()
        self.selected_time = tk.StringVar()
        self.selected_seats = set()

        self.bookings = load_bookings()

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Select Movie:").grid(row=0, column=0, sticky='w')
        movie_menu = tk.OptionMenu(self.root, self.selected_movie, *MOVIES.keys(), command=self.update_times)
        movie_menu.grid(row=0, column=1)

        tk.Label(self.root, text="Select Time:").grid(row=1, column=0, sticky='w')
        self.time_menu = tk.OptionMenu(self.root, self.selected_time, '')
        self.time_menu.grid(row=1, column=1)

        self.canvas = tk.Frame(self.root)
        self.canvas.grid(row=2, column=0, columnspan=3, pady=10)

        tk.Button(self.root, text="Confirm Booking", command=self.confirm_booking).grid(row=3, column=1, pady=5)

        self.selected_movie.trace_add("write", lambda *_: self.render_seats())
        self.selected_time.trace_add("write", lambda *_: self.render_seats())

    def update_times(self, selected_movie):
        times = MOVIES[selected_movie]
        menu = self.time_menu['menu']
        menu.delete(0, 'end')
        for time in times:
            menu.add_command(label=time, command=lambda t=time: self.selected_time.set(t))
        self.selected_time.set('')

    def get_booking_key(self):
        return f"{self.selected_movie.get()}_{self.selected_time.get()}"

    def render_seats(self):
        for widget in self.canvas.winfo_children():
            widget.destroy()
        self.selected_seats.clear()

        if not self.selected_movie.get() or not self.selected_time.get():
            return

        key = self.get_booking_key()
        booked = set(self.bookings.get(key, []))

        for r in range(ROWS):
            for c in range(COLS):
                seat_id = f"{chr(65+r)}{c+1}"
                btn = tk.Button(self.canvas, text=seat_id, width=4)

                if seat_id in booked:
                    btn.config(bg='red', state='disabled')
                else:
                    btn.config(bg='lightgray')
                    btn.config(command=lambda s=seat_id, b=btn: self.toggle_seat(s, b))

                btn.grid(row=r, column=c, padx=2, pady=2)

    def toggle_seat(self, seat_id, button):
        if seat_id in self.selected_seats:
            self.selected_seats.remove(seat_id)
            button.config(bg='lightgray')
        else:
            self.selected_seats.add(seat_id)
            button.config(bg='green')

    def confirm_booking(self):
        if not self.selected_movie.get() or not self.selected_time.get():
            messagebox.showerror("Error", "Please select a movie and time.")
            return
        if not self.selected_seats:
            messagebox.showerror("Error", "No seats selected.")
            return

        key = self.get_booking_key()
        if key not in self.bookings:
            self.bookings[key] = []

        # Prevent double booking
        already_booked = set(self.bookings[key])
        conflict = already_booked & self.selected_seats
        if conflict:
            messagebox.showerror("Error", f"Seats already booked: {', '.join(conflict)}")
            return

        self.bookings[key].extend(self.selected_seats)
        save_bookings(self.bookings)
        messagebox.showinfo("Success", f"Seats booked: {', '.join(self.selected_seats)}")
        self.render_seats()


if __name__ == "__main__":
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()
