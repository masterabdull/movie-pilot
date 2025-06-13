import tkinter as tk
from tkinter import messagebox
import psycopg2
import psycopg2.extras

# ──────────────── Adjust these to match your Postgres settings ────────────────
DB_PARAMS = {
    'host':     'localhost',
    'port':     5432,
    'dbname':   'movie_pilot',
    'user':     'postgres',
    'password': 'cos101'
}
# ────────────────────────────────────────────────────────────────────────────────


class BookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Panaview Cinemas Booking System")

        # Connect to PostgreSQL
        try:
            self.conn = psycopg2.connect(**DB_PARAMS)
            self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to database:\n{e}")
            root.destroy()
            return

        # Track selected IDs
        self.selected_movie_id = None
        self.selected_timeslot_id = None
        self.selected_seat_ids = set()

        # On window close, ensure DB connection is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start with the movie‐selection screen
        self.show_movie_selection()

    def on_close(self):
        """Cleanup DB connection and exit."""
        try:
            self.cur.close()
            self.conn.close()
        except:
            pass
        self.root.destroy()

    # ─────────────── Data Access Methods ───────────────

    def get_movies(self):
        self.cur.execute("SELECT  movie_id, title FROM movies ORDER BY title;")
        return self.cur.fetchall()

    def get_timeslots(self, movie_id):
        self.cur.execute(
            "SELECT  movie_id, slot_time FROM timeslots WHERE movie_id = %s ORDER BY slot_time;",
            (movie_id,)
        )
        return self.cur.fetchall()

    def get_seats(self, timeslot_id):
        self.cur.execute(
            "SELECT id, row, col, status FROM seats WHERE timeslot_id = %s;",
            (timeslot_id,)
        )
        return self.cur.fetchall()

    def book_seats_in_db(self, seat_id_list):
        """
        Mark the given seat IDs as 'booked'. We assume seat.status was 'available'.
        """
        if not seat_id_list:
            return

        sql = """
            UPDATE seats
            SET status = 'booked'
            WHERE id = ANY(%s) AND status = 'available';
        """
        self.cur.execute(sql, (seat_id_list,))
        self.conn.commit()

    # ─────────────── GUI Screens ───────────────

    def clear_screen(self):
        """Remove all widgets from root."""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.selected_seat_ids.clear()

    def show_movie_selection(self):
        """Screen 1: Let user pick a movie from the list."""
        self.clear_screen()
        tk.Label(self.root, text="Select a Movie:", font=("TkDefaultFont", 14)).pack(pady=10)

        movies = self.get_movies()
        self.movie_listbox = tk.Listbox(self.root, width=40, height=6, exportselection=False)
        for mv in movies:
            self.movie_listbox.insert(tk.END, f"{mv['id']}: {mv['title']}")
        self.movie_listbox.pack(pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Next →", command=self.on_movie_selected).pack(side=tk.RIGHT, padx=5)

    def on_movie_selected(self):
        """Called when user clicks Next after selecting a movie."""
        sel = self.movie_listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a movie first.")
            return

        entry = self.movie_listbox.get(sel[0])
        # Format: "ID: Title"
        mv_id = int(entry.split(":", 1)[0])
        self.selected_movie_id = mv_id
        self.show_timeslot_selection()

    def show_timeslot_selection(self):
        """Screen 2: List timeslots for the chosen movie."""
        self.clear_screen()
        tk.Label(
            self.root,
            text="Select a Time Slot:",
            font=("TkDefaultFont", 14)
        ).pack(pady=10)

        timeslots = self.get_timeslots(self.selected_movie_id)
        if not timeslots:
            tk.Label(self.root, text="No timeslots available for this movie.").pack(pady=10)
            tk.Button(self.root, text="← Back", command=self.show_movie_selection).pack(pady=5)
            return

        self.timeslot_listbox = tk.Listbox(self.root, width=50, height=6, exportselection=False)
        for ts in timeslots:
            # Display slot_time as string (e.g., "2025-06-05 18:00")
            self.timeslot_listbox.insert(tk.END, f"{ts['id']}: {ts['slot_time']}")
        self.timeslot_listbox.pack(pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="← Back", command=self.show_movie_selection).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Next →", command=self.on_timeslot_selected).pack(side=tk.RIGHT, padx=5)

    def on_timeslot_selected(self):
        sel = self.timeslot_listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a time slot first.")
            return

        entry = self.timeslot_listbox.get(sel[0])
        ts_id = int(entry.split(":", 1)[0])
        self.selected_timeslot_id = ts_id
        self.show_seat_selection()

    def show_seat_selection(self):
        """
        Screen 3: Visual seat‐selection grid (6 rows × 8 columns).
        Available seats: green; Booked seats: red; Selected seats (by user): blue.
        """
        self.clear_screen()

        # Fetch all seats for this timeslot
        seats = self.get_seats(self.selected_timeslot_id)
        if not seats:
            tk.Label(self.root, text="No seats found for this time slot.").pack(pady=10)
            tk.Button(self.root, text="← Back", command=self.show_timeslot_selection).pack(pady=5)
            return

        tk.Label(self.root, text="Select Your Seats:", font=("TkDefaultFont", 14)).pack(pady=10)

        # Frame to hold the seat buttons
        grid_frame = tk.Frame(self.root)
        grid_frame.pack(padx=10, pady=10)

        # Build a mapping (row_char → row_index)
        rows = sorted({row['row'] for row in seats})
        cols = sorted({row['col'] for row in seats})
        row_index_map = {r: i for i, r in enumerate(rows)}
        col_index_map = {c: j for j, c in enumerate(cols)}

        # 2D array to hold button references (by [row_index][col_index])
        self.seat_buttons = [[None for _ in cols] for __ in rows]

        for seat in seats:
            r_char = seat['row']
            c_num = seat['col']
            st = seat['status']
            s_id = seat['id']

            i = row_index_map[r_char]
            j = col_index_map[c_num]

            btn = tk.Button(
                grid_frame,
                text=f"{r_char}{c_num}",
                width=4, height=2,
                relief=tk.RAISED
            )
            # Color‐code based on status
            if st == 'booked':
                btn.configure(bg='red', state=tk.DISABLED)
            else:  # 'available'
                btn.configure(bg='green')
                # Attach toggle behavior
                btn.configure(command=lambda b=btn, sid=s_id: self.toggle_seat(b, sid))

            btn.grid(row=i, column=j, padx=2, pady=2)
            self.seat_buttons[i][j] = btn

        # Legend
        legend_frame = tk.Frame(self.root)
        legend_frame.pack(pady=5)
        tk.Label(legend_frame, text="🟩 Available   🟥 Booked   🟦 Selected").pack()

        # Bottom buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="← Back", command=self.show_timeslot_selection).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Confirm Booking", command=self.confirm_booking).pack(side=tk.RIGHT, padx=5)

    def toggle_seat(self, button, seat_id):
        """
        When an available (green) seat is clicked:
        - If not yet selected → turn blue and add to selected_seat_ids
        - If already selected (blue) → revert to green and remove from selected_seat_ids
        """
        current_color = button.cget('bg')
        if current_color == 'green':
            button.configure(bg='blue')
            self.selected_seat_ids.add(seat_id)
        elif current_color == 'blue':
            button.configure(bg='green')
            self.selected_seat_ids.discard(seat_id)

    def confirm_booking(self):
        """Attempt to book all seats in self.selected_seat_ids, then refresh the grid."""
        if not self.selected_seat_ids:
            messagebox.showinfo("No Seats Selected", "Please select at least one seat to book.")
            return

        # Update DB: only seats that are still 'available' will be booked
        try:
            self.book_seats_in_db(list(self.selected_seat_ids))
        except Exception as e:
            messagebox.showerror("Booking Error", f"Could not complete booking:\n{e}")
            return

        messagebox.showinfo("Booking Confirmed", "Your seats have been booked successfully!")
        # Reset selection and refresh the seat grid
        self.selected_seat_ids.clear()
        self.show_seat_selection()


if __name__ == "__main__":
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()
