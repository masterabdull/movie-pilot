import tkinter as tk
from tkinter import ttk
import pyglet, os, psycopg2, subprocess, sys
from PIL import Image, ImageTk
import tkinter.messagebox

class MoviePilot:
    def set_default_styles(self):
        self.font_path = './fonts/Poppins-Regular.ttf'

        if os.path.exists(self.font_path):
            pyglet.font.add_file(self.font_path)
            self.tab_font = ("Poppins", 14, "bold")
            self.header_font = ('Poppins', 40)
            self.content_font = ("Poppins", 34)
        else:
            print(f"Warning: Font file not found at {self.font_path}. Using default system font.")
            self.tab_font = ("Arial", 12, "bold")
            self.content_font = ("Arial", 18)
        
        self.root.configure(background='black')
        self.__style = ttk.Style()
        self.__style.theme_use('clam')        # Configure Combobox style for larger items and better appearance
        self.__style.configure('TCombobox', 
                             padding=10,
                             selectbackground='#333333',
                             selectforeground='white',
                             fieldbackground='#222222',
                             background='white',  # Arrow color
                             foreground='white',  # Text color
                             arrowcolor='#000'  # Gold/yellow for high contrast
                             )  
        
        # Additional Combobox styling for the entry part
        self.__style.map('TCombobox',
                        fieldbackground=[('readonly', '#222222')],
                        selectbackground=[('readonly', '#222222')],
                        foreground=[('readonly', 'white')],
                        selectforeground=[('readonly', 'white')])
        
        # Configure the Combobox listbox with larger size and better styling
        self.root.option_add('*TCombobox*Listbox.font', ('Poppins', int(16*1.5)))  # Larger font
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#444444')  # Selection background
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')   # Selection text
        self.root.option_add('*TCombobox*Listbox.background', '#222222')       # List background
        self.root.option_add('*TCombobox*Listbox.foreground', 'white')        # List text
        self.root.option_add('*TCombobox*Listbox.selectMode', 'browse')       # Single selection mode
        self.root.option_add('*TCombobox*Listbox.padding', 20)                # More padding around items
        self.root.option_add('*TCombobox*Listbox.relief', 'flat')            # Flat appearance
        
        self.__style.configure('TNotebook', background='#333333', borderwidth=0)
        self.__style.configure('TNotebook.Tab',
                               background='#555555',    
                               foreground='white',      
                               font=self.tab_font,
                               padding=[15, 8, 15, 8])
                                                        
        self.__style.map('TNotebook.Tab',
                         background=[('selected', '#000000'), 
                                     ('active', '#3D3D3D')],   
                         foreground=[('selected', 'white'),   
                                     ('active', 'white')],       
                         padding=[('selected', [20, 10, 20, 10]), 
                                  ('active', [20, 10, 20, 10])])  
        self.__style.configure('TFrame', background='#1c1c1c')
        
        # Style for a nice looking close button with hover effect
        self.__style.configure('Close.TButton', background='#222', foreground='white', font=('Poppins', 16, 'bold'))
        self.__style.map('Close.TButton', foreground=[('active', 'black')])
        
    def initialise_database(self):
        db_name = 'movie_pilot'
        db_user = 'postgres'
        db_password = 'cos101'
        
        try:
            self.connection = psycopg2.connect(f'dbname = {db_name} user={db_user} password = {db_password}')
            self.cursor = self.connection.cursor()
            print('Database connected successfully')
            
            self.cursor.execute('SELECT * FROM movies;')
            columns = ['movie_id', 'title', 'synopsis', 'content_rating', 'average_user_rating', 'release_year', 'runtime_minutes', 'genre']
            self.movies = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            print(self.movies)
        except Exception as e:
            print('Error during database connection: \n', e)        

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Movie Pilot")
        self.root.geometry('1200x800')
        self.tab_counter = 0

        self.set_default_styles()
        self.initialise_database()

        self.root.state('zoomed')
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=0, pady=0)

        self.display_home()
        self.display_search()
        self.notebook.select(0)
        
    def display_image(self, path, frame, relx, rely, hasBorder=False):
        image_pil = Image.open(path)
        image_tk = ImageTk.PhotoImage(image_pil)
        if hasBorder:
            image_img = tk.Label(frame, image=image_tk)
        else:
            image_img = tk.Label(frame, image=image_tk, borderwidth=0)
        image_img.image = image_tk
        # Use relx/rely for positioning
        place_args = {}
        place_args['relx'] = relx
        place_args['rely'] = rely
        image_img.place(**place_args)
        
        return image_img
        
    def display_home(self):
        home_frame = ttk.Frame(self.notebook)
        self.notebook.add(home_frame, text='Home')
        self.tab_counter += 1
        sinners_file_path = './images/sinners.png'
        sinners_watch_trailer_button_file_path = './images/sinners-watch-trailer.png'
        get_movie_tickets_file_path = './images/get-movie-tickets.png'
        logo_file_path = './images/logo.png'
        movie_slides_file_path = './images/movie-slides.png'
        view_sinners_description_file_path = './images/view-sinners-description.png'
        
        # Place logo at the top left corner
        self.display_image(logo_file_path, home_frame, relx=0, rely=-0.01)
        
        welcome_message = 'Welcome to Movie Pilot. Your world-class cinematic experience.'
        ttk.Label(home_frame, text=welcome_message, font=self.header_font,
                  foreground="white", background=self.__style.lookup("TFrame", "background")).pack(pady=30)
        
        recommended_movie_desc = 'Recommended Movie'
        ttk.Label(home_frame, text=recommended_movie_desc, font=self.content_font,
                  foreground="white", background=self.__style.lookup("TFrame", "background")).pack(pady=10)
        
        self.display_image(sinners_file_path, home_frame, relx=0.1, rely=0.2, hasBorder=True)
        watch_sinners_trailer_button = self.display_image(sinners_watch_trailer_button_file_path, home_frame, relx=0.2, rely=0.8)
        
        # Display view-sinners-description.png a little to the left and slightly above get-movie-tickets.png
        view_sinners_description = self.display_image(view_sinners_description_file_path, home_frame, relx=0.37, rely=0.78)
        # Display movie-slides.png slightly on top of get-movie-tickets.png
        self.display_image(movie_slides_file_path, home_frame, relx=0.6, rely=0.68)
        get_movie_tickets_button = self.display_image(get_movie_tickets_file_path, home_frame, relx=0.6, rely=0.82)
        
        watch_sinners_trailer_button.bind("<Button-1>", self.watch_sinners_trailer)
        get_movie_tickets_button.bind("<Button-1>", self.get_movie_tickets)
        view_sinners_description.bind("<Button-1>", self.view_sinners_description)
        
    def display_search(self):
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text='Search')
        self.tab_counter += 1

        ttk.Label(search_frame, text="Search for movies...", font=self.content_font,
                  foreground="white", background=self.__style.lookup("TFrame", "background")).pack(pady=50)

    def start(self):
        self.root.mainloop()
        
    def watch_sinners_trailer(self, event=None):
        trailer_frame = ttk.Frame(self.notebook)
        self.notebook.add(trailer_frame, text='Sinners Trailer')
        self.tab_counter += 1
        self.notebook.select(self.notebook.tabs()[-1])
        close_button = ttk.Button(trailer_frame, text='Close', style='Close.TButton', command=lambda: self.notebook.forget(trailer_frame))
        close_button.pack(side=tk.TOP, anchor='ne', padx=10, pady=10)

        ttk.Label(trailer_frame, text="Playing Sinners Trailer...", font=self.header_font,
                  foreground="white", background=self.__style.lookup("TFrame", "background")).pack(pady=30)

        # Attempt to play the video using the system's default player (cross-platform)
        video_path = os.path.join(os.path.dirname(__file__), '..', 'videos', 'sinners-trailer.mp4')
        video_path = os.path.abspath(video_path)
        try:
            if sys.platform.startswith('win'):
                os.startfile(video_path)  
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', video_path])
            else:
                subprocess.Popen(['xdg-open', video_path])
        except Exception as e:
            ttk.Label(trailer_frame, text=f"Could not play video: {e}", foreground="red").pack()

        get_movie_tickets_file_path = './images/get-movie-tickets.png'
        get_movie_tickets_button = self.display_image(get_movie_tickets_file_path, trailer_frame, relx=0.6, rely=0.8)
        get_movie_tickets_button.bind("<Button-1>", self.get_movie_tickets)
        
    def get_movie_tickets(self, event=None):
        tickets_frame = ttk.Frame(self.notebook)
        self.notebook.add(tickets_frame, text='Select Showtime')
        self.tab_counter += 1
        self.notebook.select(self.notebook.tabs()[-1])
        close_button = ttk.Button(tickets_frame, text='Close', style='Close.TButton', command=lambda: self.notebook.forget(tickets_frame))
        close_button.pack(side=tk.TOP, anchor='ne', padx=10, pady=10)

        # Dropdowns for movie, show date, and show time
        ttk.Label(tickets_frame, text="Select Showtime", font=(self.header_font[0], int(self.header_font[1]*1.5)), foreground="white", background=self.__style.lookup("TFrame", "background")).place(relx=0.05, rely=0.05)

        # Movie dropdown
        movie_names = [m['title'] for m in self.movies]
        movie_var = tk.StringVar(value=movie_names[0] if movie_names else "")
        ttk.Label(tickets_frame, text="Movie", font=("Poppins", int(18*1.5), "bold"), foreground="white", background=self.__style.lookup("TFrame", "background")).place(relx=0.05, rely=0.15)
        movie_dropdown = ttk.Combobox(tickets_frame, textvariable=movie_var, values=movie_names, font=("Poppins", int(16*1.5)), state="readonly")
        movie_dropdown.place(relx=0.05, rely=0.20, relwidth=0.4)

        # Show date dropdown
        self.cursor.execute("SELECT DISTINCT show_date FROM showtimes ORDER BY show_date")
        show_dates = [row[0] for row in self.cursor.fetchall()]
        show_date_var = tk.StringVar(value=show_dates[0] if show_dates else "")
        ttk.Label(tickets_frame, text="Date", font=("Poppins", int(18*1.5), "bold"), foreground="white", background=self.__style.lookup("TFrame", "background")).place(relx=0.05, rely=0.28)
        show_date_dropdown = ttk.Combobox(tickets_frame, textvariable=show_date_var, values=show_dates, font=("Poppins", int(16*1.5)), state="readonly")
        show_date_dropdown.place(relx=0.05, rely=0.33, relwidth=0.4)

        # Show time dropdown
        self.cursor.execute("SELECT DISTINCT show_time FROM showtimes ORDER BY show_time")
        show_times = [row[0].strftime("%H:%M") for row in self.cursor.fetchall()]
        show_time_var = tk.StringVar(value=show_times[0] if show_times else "")
        ttk.Label(tickets_frame, text="Time", font=("Poppins", int(18*1.5), "bold"), foreground="white", background=self.__style.lookup("TFrame", "background")).place(relx=0.05, rely=0.41)
        show_time_dropdown = ttk.Combobox(tickets_frame, textvariable=show_time_var, values=show_times, font=("Poppins", int(16*1.5)), state="readonly")
        show_time_dropdown.place(relx=0.05, rely=0.46, relwidth=0.4)# Continue and Back buttons
        continue_btn = ttk.Button(tickets_frame, text="Continue", style='Close.TButton',
            command=lambda: self.book_seats(movie_var.get(), show_date_var.get(), show_time_var.get()))
        continue_btn.place(relx=0.75, rely=0.85, relwidth=0.18, relheight=0.09)
        back_btn = ttk.Button(tickets_frame, text="Back", style='Close.TButton', command=lambda: self.notebook.forget(tickets_frame))
        back_btn.place(relx=0.07, rely=0.85, relwidth=0.18, relheight=0.09)
        
    def view_sinners_description(self, event=None):
        # Create a new tab for the description
        desc_frame = ttk.Frame(self.notebook)
        self.notebook.add(desc_frame, text='Sinners Description')
        self.tab_counter += 1
        self.notebook.select(self.notebook.tabs()[-1])
        close_button = ttk.Button(desc_frame, text='Close', style='Close.TButton', command=lambda: self.notebook.forget(desc_frame))
        close_button.pack(side=tk.TOP, anchor='ne', padx=10, pady=10)

        # Left: Sinners front cover image
        sinners_front_cover_path = './images/sinners-front-cover.png'
        left_img = self.display_image(sinners_front_cover_path, desc_frame, relx=0, rely=0)

        # Right: Content frame
        right_frame = ttk.Frame(desc_frame, style='TFrame')
        right_frame.place(relx=0.38, rely=0, relwidth=0.62, relheight=1)

        # Nav hero image at the top right
        nav_hero_path = './images/view-sinners-description-nav-hero.png'
        self.display_image(nav_hero_path, right_frame, relx=0, rely=0.0)

        # Get Sinners movie details
        sinners_movie = next((m for m in self.movies if m['title'].lower() == 'sinners'), None)
        if not sinners_movie:
            ttk.Label(right_frame, text="Movie not found.", font=(self.header_font[0], int(self.header_font[1]*1.3)), foreground="white", background=self.__style.lookup("TFrame", "background")).pack(pady=30)
            return

        # Title
        ttk.Label(right_frame, text=sinners_movie['title'], font=(self.header_font[0], int(self.header_font[1]*1.3)), foreground="white", background=self.__style.lookup("TFrame", "background")).place(relx=0.5, rely=0.08, anchor='n')
        # Release year | Genre | Runtime
        meta = f"{sinners_movie['release_year']} | {sinners_movie['genre']} | {sinners_movie['runtime_minutes']} min"
        ttk.Label(right_frame, text=meta, font=(self.content_font[0], int(self.content_font[1]*1.3)), foreground="#b0b0b0", background=self.__style.lookup("TFrame", "background")).place(relx=0.5, rely=0.17, anchor='n')
        # Synopsis (much bigger and further down)
        ttk.Label(right_frame, text=sinners_movie['synopsis'], font=("Poppins", int(32*1.3)), wraplength=650, justify="left", foreground="white", background=self.__style.lookup("TFrame", "background")).place(relx=0.5, rely=0.32, anchor='n')
        # Select Showtime header
        ttk.Label(right_frame, text="Select Showtime", font=(self.header_font[0], int(self.header_font[1]*1.3)), foreground="white", background=self.__style.lookup("TFrame", "background")).place(relx=0.5, rely=0.55, anchor='n')

        # Get 4 random showtimes for Sinners (movie_id=1)
        self.cursor.execute("SELECT showtime_id, show_date, show_time, screen FROM showtimes WHERE movie_id=1 ORDER BY RANDOM() LIMIT 4;")
        showtimes = self.cursor.fetchall()
        for idx, showtime in enumerate(showtimes):
            showtime_id, show_date, show_time, screen = showtime
            btn_text = f"{show_date} | {show_time[:-3]} | {screen}"
            btn = ttk.Button(right_frame, text=btn_text, style='Close.TButton', command=lambda s=showtime_id: self.open_showtime_tab(s))
            btn.place(relx=0.5, rely=0.62+idx*0.08, anchor='n')

    def open_showtime_tab(self, showtime_id):
        showtime_frame = ttk.Frame(self.notebook)
        self.notebook.add(showtime_frame, text='Showtime')
        self.tab_counter += 1
        self.notebook.select(self.notebook.tabs()[-1])
        close_button = ttk.Button(showtime_frame, text='Close', style='Close.TButton', command=lambda: self.notebook.forget(showtime_frame))
        close_button.pack(side=tk.TOP, anchor='ne', padx=10, pady=10)
        ttk.Label(showtime_frame, text=f"Showtime ID: {showtime_id}", font=self.header_font, foreground="white", background=self.__style.lookup("TFrame", "background")).pack(pady=30)
        
    def book_seats(self, movie, show_date, show_time):
        # Find the showtime_id for the selected movie, date, and time
        self.cursor.execute("""
            SELECT showtime_id FROM showtimes
            WHERE movie_id = (SELECT movie_id FROM movies WHERE title = %s)
              AND show_date = %s AND show_time = %s
        """, (movie, show_date, show_time))
        result = self.cursor.fetchone()
        if not result:
            tk.messagebox.showerror("Error", "Showtime not found.")
            return
        showtime_id = result[0]

        # Get seat status for this showtime (reload from DB for persistence)
        self.cursor.execute("""
            SELECT ts.seat_id, ts.status, s.seat_number, s.row, s.column_number
            FROM showtime_seats ts
            JOIN seats s ON ts.seat_id = s.seat_id
            WHERE ts.showtime_id = %s
            ORDER BY s.row, s.column_number
        """, (showtime_id,))
        seats = self.cursor.fetchall()

        icon_paths = {
            'Available': './icons/seat-available.png',
            'Sold': './icons/seat-sold.png',
            'Selected': './icons/seat-selected.png',
        }
        icons = {k: ImageTk.PhotoImage(Image.open(v).resize((48, 48))) for k, v in icon_paths.items()}

        seat_frame = ttk.Frame(self.notebook)
        self.notebook.add(seat_frame, text='Select Seats')
        self.tab_counter += 1
        self.notebook.select(self.notebook.tabs()[-1])

        # Counter label
        counter_var = tk.StringVar()
        counter_label = ttk.Label(seat_frame, textvariable=counter_var, font=("Poppins", 28, "bold"), foreground="#00FF00", background=self.__style.lookup("TFrame", "background"))
        counter_label.pack(pady=10)

        # Instructions
        ttk.Label(seat_frame, text="Select up to 5 seats", font=("Poppins", 18, "bold"), foreground="white", background=self.__style.lookup("TFrame", "background")).pack(pady=5)

        seat_btns = {}
        selected_seats = set(seat_id for seat_id, status, *_ in seats if status == 'Selected')
        max_select = 5
        grid = ttk.Frame(seat_frame, style='TFrame')
        grid.pack(pady=20)
        row_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

        def update_counter():
            counter_var.set(f"{len(selected_seats)}/5 seats selected")
        update_counter()

        def seat_callback(seat_id, btn, current_status):
            self.cursor.execute("SELECT status FROM showtime_seats WHERE showtime_id=%s AND seat_id=%s", (showtime_id, seat_id))
            db_status = self.cursor.fetchone()[0]
            if db_status == 'Sold':
                return
            if seat_id in selected_seats:
                # Deselect
                self.cursor.execute("UPDATE showtime_seats SET status='Available' WHERE showtime_id=%s AND seat_id=%s", (showtime_id, seat_id))
                self.connection.commit()
                selected_seats.remove(seat_id)
                btn.config(image=icons['Available'])
            else:
                if len(selected_seats) >= max_select:
                    tkinter.messagebox.showinfo("Limit reached", "You can select up to 5 seats only.")
                    return
                self.cursor.execute("UPDATE showtime_seats SET status='Selected' WHERE showtime_id=%s AND seat_id=%s", (showtime_id, seat_id))
                self.connection.commit()
                selected_seats.add(seat_id)
                btn.config(image=icons['Selected'])
            update_counter()

        for seat_id, status, seat_number, row, col in seats:
            icon = icons['Selected'] if status == 'Selected' else icons['Sold' if status == 'Sold' else 'Available']
            btn = tk.Button(grid, image=icon, bd=0, bg='black', activebackground='black')
            btn.grid(row=row_map[row], column=col-1, padx=8, pady=8)
            if status != 'Sold':
                btn.config(command=lambda sid=seat_id, b=btn, s=status: seat_callback(sid, b, s))
            seat_btns[seat_id] = btn

        legend = ttk.Frame(seat_frame, style='TFrame')
        legend.pack(pady=10)
        for i, (label, icon) in enumerate([
            ("Selected", icons['Selected']),
            ("Sold", icons['Sold']),
            ("Available", icons['Available'])
        ]):
            tk.Label(legend, image=icon, bg='black').grid(row=0, column=2*i, padx=5)
            ttk.Label(legend, text=label, font=("Poppins", 14), foreground='white', background='black').grid(row=0, column=2*i+1, padx=10)

movie_pilot = MoviePilot()
movie_pilot.start()