import tkinter as tk
from tkinter import ttk
import pyglet, os, psycopg2, subprocess, sys
from PIL import Image, ImageTk

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
        self.__style.theme_use('clam')
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
        
        welcome_message = 'Welcome to Movie Pilot. Your world-class cinematic experience.'
        ttk.Label(home_frame, text=welcome_message, font=self.header_font,
                  foreground="white", background=self.__style.lookup("TFrame", "background")).pack(pady=30)
        
        recommended_movie_desc = 'Recommended Movie'
        ttk.Label(home_frame, text=recommended_movie_desc, font=self.content_font,
                  foreground="white", background=self.__style.lookup("TFrame", "background")).pack(pady=10)
        
        self.display_image(sinners_file_path, home_frame, relx=0.1, rely=0.2, hasBorder=True)
        watch_sinners_trailer_button = self.display_image(sinners_watch_trailer_button_file_path, home_frame, relx=0.2, rely=0.8)
        get_movie_tickets_button = self.display_image(get_movie_tickets_file_path, home_frame, relx=0.6, rely=0.8)
        
        watch_sinners_trailer_button.bind("<Button-1>", self.watch_sinners_trailer)
        get_movie_tickets_button.bind("<Button-1>", self.get_movie_tickets)
        
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
        self.notebook.add(tickets_frame, text='Get Movie Tickets')
        self.tab_counter += 1
        self.notebook.select(self.notebook.tabs()[-1])
        close_button = ttk.Button(tickets_frame, text='Close', style='Close.TButton', command=lambda: self.notebook.forget(tickets_frame))
        close_button.pack(side=tk.TOP, anchor='ne', padx=10, pady=10)

        ttk.Label(tickets_frame, text="Select a Movie to Get Tickets", font=self.header_font,
                  foreground="white", background=self.__style.lookup("TFrame", "background")).pack(pady=30)

        # Here I would implement the logic to display movies and allow ticket selection
        # For now, we will just show a placeholder message
        # Also, TODO: BUGFIX: Ensure a new tab is created only if it doesn't already exist when clicking any buttons that spawn new tabs
        
        ttk.Label(tickets_frame, text="Movie selection feature coming soon!", font=self.content_font,
                  foreground="white", background=self.__style.lookup("TFrame", "background")).pack(pady=50)
        
movie_pilot = MoviePilot()
movie_pilot.start()