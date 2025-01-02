import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk, ImageFont
from io import BytesIO
import tkinter.font as tkfont
import os

class PokemonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pokédex")
        self.geometry("550x820")

        font_path = "MinecraftRegular-Bmg3.ttf"

        # Set a custom icon for the application (Title Bar)
        icon_path = "Poké_Ball_icon.png"
        try:
            self.icon_image = tk.PhotoImage(file=icon_path)
            self.iconphoto(True, self.icon_image)
        except Exception as e:
            print(f"Error loading icon: {e}")

        # Path to the font.
        font_path = "MinecraftRegular-Bmg3.ttf"

        try:
            # Attempt to load the font specified and set the default size.
            pillow_font = ImageFont.truetype(font_path, size=12)
            
            # Use the font family name after installation that the rest of the code will utilize.
            self.global_font = tkfont.Font(
                family="Minecraft",
                size=12,
                weight="bold"
                )
        except Exception as e:
            print(f"Error loading custom font: {e}")
            self.global_font = tkfont.Font(family="Arial", size=12, weight="bold")  # Fallback font incase the original font isnt displayed.

        # Cache to store Pokémon data
        self.cache = {}

        # Type-to-color mapping for details section.
        self.TYPE_COLORS_DETAILS = {
            "normal": "#a5b3a5", 
            "fire": "#EE8130", 
            "water": "#6390F0",
            "electric": "#F7D02C", 
            "grass": "#7AC74C", 
            "ice": "#96D9D6",
            "fighting": "#C22E28", 
            "poison": "#A33EA1", 
            "ground": "#E2BF65",
            "flying": "#A98FF3", 
            "psychic": "#F95587", 
            "bug": "#A6B91A",
            "rock": "#B6A136", 
            "ghost": "#8a92b5", 
            "dragon": "#9969d9",
            "dark": "#333333", 
            "steel": "#B7B7CE", 
            "fairy": "#e7c7e4",
        }

        # Type-to-color mapping for background
        self.TYPE_COLORS_BACKGROUND = {
            "normal": "#9198a1", 
            "fire": "#fe9c53", 
            "water": "#83a8f9",
            "electric": "#fdb84b", 
            "grass": "#63bc59", 
            "ice": "#74cfc0",
            "fighting": "#ef613a", 
            "poison": "#a869c7", 
            "ground": "#dda86d",
            "flying": "#8fa8de", 
            "psychic": "#fa7077", 
            "bug": "#6da04a",
            "rock": "#c8b78b", 
            "ghost": "#a684a7", 
            "dragon": "#a869c7",
            "dark": "#515976", 
            "steel": "#717891", 
            "fairy": "#ec8fe7",
        }

        # Add loading screen
        self.loading_label = tk.Label(self, text="Loading Pokémon data...", font=self.global_font)
        self.loading_label.pack(pady=300)

        # Start fetching initial data
        self.after(100, self.initialize_bare_minimum)  # Delay to ensure UI updates before loading screen is done.

    def initialize_bare_minimum(self):
        print("Fetching initial Pokémon data...")
        self.current_pokemon_data = self.get_pokemon_data(1)  # Fetch Bulbasaur
        if self.current_pokemon_data:
            print("Initial Pokémon data fetched successfully.")  # Debug
            self.loading_label.destroy()  # Remove loading screen once everything is inizialized to the bare minimum.
            self.initialize_ui()  # Initialize the main UI
            self.update_pokemon_info(1)  # Display the first Pokémon (Bulbasaur)
        else:
            print("Failed to fetch initial Pokémon data.")  # Debug
            self.loading_label.config(text="Failed to load Pokémon data. Please try again.")

    def initialize_ui(self):
        # Creates a frame to hold the navigation buttons and search box
        self.nav_frame = tk.Frame(self)
        self.nav_frame.pack(pady=10)

        # Previous Button
        self.prev_button = tk.Button(self.nav_frame, text="Previous", font=self.global_font, command=self.prev_pokemon)
        self.prev_button.grid(row=0, column=0, padx=5)

        # Search Box
        self.search_box = tk.Entry(self.nav_frame, width=30, font=self.global_font)
        self.search_box.grid(row=0, column=1, padx=5)
        self.search_box.bind("<Return>", self.fetch_pokemon)

        # Next Button
        self.next_button = tk.Button(self.nav_frame, text="Next", font=self.global_font, command=self.next_pokemon)
        self.next_button.grid(row=0, column=2, padx=5)

        # Pokémon Name and Customization
        self.pokemon_name = tk.Label(
        self, 
        text="POKEMON NAME", 
        font=tkfont.Font(family="Minecraft", size=24, weight="bold"),
        wraplength=300
        )
        self.pokemon_name.pack(pady=10)

        # Pokémon Image Customization
        self.pokemon_image = tk.Label(self, width=400, height=250)
        self.pokemon_image.pack(pady=10)

        # Type Frame
        self.type_frame = tk.Frame(self)
        self.type_frame.pack(pady=5)

        # Shiny Checkbox (centered above the pokemon types)
        self.shiny_var = tk.BooleanVar()
        self.shiny_checkbox = tk.Checkbutton(self.type_frame, text="Shiny", variable=self.shiny_var, font=self.global_font, command=self.update_pokemon_image)
        self.shiny_checkbox.pack(side=tk.TOP, pady=5)

        # Pokémon Types Customization
        self.type1 = tk.Label(self.type_frame, text="", font=self.global_font, width=15, wraplength=100)
        self.type1.pack(side=tk.LEFT, padx=5)

        self.type2 = tk.Label(self.type_frame, text="", font=self.global_font, width=15, wraplength=100)
        self.type2.pack(side=tk.RIGHT, padx=5)

        # Hollow Box that encloses the "Pokemon description"
        self.description_box = tk.Frame(self, bg="white", bd=2, relief="solid", padx=10, pady=10)
        self.description_box.pack(pady=10, fill="x", padx=50)

        self.description_label = tk.Label(self.description_box, text="", font=self.global_font, wraplength=350, bg="white")
        self.description_label.pack()

        # Hollow Box that encloses the "Pokemon details"
        self.details_box = tk.Frame(self, bg="white", bd=2, relief=tk.SOLID, padx=10, pady=10)
        self.details_box.pack(pady=5)

        self.details_box.grid_columnconfigure(0, weight=1)
        self.details_box.grid_columnconfigure(1, weight=1)

        self.height_label = tk.Label(self.details_box, text="", font=self.global_font, width=15, bg="white", wraplength=120, anchor="center")
        self.height_label.grid(row=0, column=0, padx=0, pady=10)

        self.weight_label = tk.Label(self.details_box, text="", font=self.global_font, width=15, bg="white", wraplength=120, anchor="center")
        self.weight_label.grid(row=0, column=1, padx=0, pady=10)

        self.species_label = tk.Label(self.details_box, text="", font=self.global_font, width=15, bg="white", wraplength=120, anchor="center")
        self.species_label.grid(row=1, column=0, padx=0, pady=10)

        self.id_label = tk.Label(self.details_box, text="", font=self.global_font, width=15, bg="white", wraplength=120, anchor="center")
        self.id_label.grid(row=1, column=1, padx=0, pady=10)

        # Abilities Section
        self.abilities_frame = tk.Frame(self)
        self.abilities_frame.pack(pady=10)

    def get_pokemon_data(self, query):
        if query in self.cache:
            return self.cache[query]

        # query pokemon data from pokeapi.co
        url = f"https://pokeapi.co/api/v2/pokemon/{query}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.cache[query] = data
                return data
        except requests.RequestException as e:
            print(f"Error fetching Pokémon data: {e}")

        return None

    def update_pokemon_info(self, query=None):
        if query is None:
            query = self.pokemon_index

        # Reset the shiny checkbox to unticked when next pokemon is updated to.
        self.shiny_var.set(False)

        # Fetch and display Pokémon
        self.fetch_and_display_pokemon(query)


    def fetch_and_display_pokemon(self, query):
        data = self.get_pokemon_data(query)
        if data:
            self.current_pokemon_data = data
            self.pokemon_index = data["id"]
            self.pokemon_name.config(text=data["name"].upper())

            # Update Image
            self.update_pokemon_image()

            # Update Types
            types = [t["type"]["name"].upper() for t in data["types"]]
            self.type1.config(
            text=types[0] if len(types) > 0 else "N/A",
            bg=self.TYPE_COLORS_DETAILS.get(types[0].lower(), "lightgrey"),
            )

            # Update Type 2
            if len(types) > 1:
                self.type2.config(
                text=types[1],
                bg=self.TYPE_COLORS_DETAILS.get(types[1].lower(), "lightgrey"),
                )
            else:
                self.type2.config(text="N/A", bg="lightgrey")

        # Update Borders and Colors
        self.update_widget_borders(types)

        # Update Background
        self.update_background(types[0].lower() if types else "normal")

        # Update Details
        self.height_label.config(text=f"HEIGHT: {data['height']}")
        self.weight_label.config(text=f"WEIGHT: {data['weight']}")
        self.id_label.config(text=f"ID: {data['id']}")

        # Update Species
        self.fetch_and_display_species(data["species"]["url"])

        # Update Abilities
        self.fetch_and_display_abilities(types[0].lower() if types else "normal", data["abilities"])


    def fetch_and_display_species(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                species_data = response.json()

                # Get the flavor text description
                flavor_text_entries = species_data["flavor_text_entries"]
                description = next((entry["flavor_text"] for entry in flavor_text_entries if entry["language"]["name"] == "en"), "No description available.")
                self.description_label.config(text=description.replace("\n", " "))

                # Get the species
                genus = next((gen["genus"] for gen in species_data["genera"] if gen["language"]["name"] == "en"), "Unknown")
                self.species_label.config(text=f"SPECIES: {genus}")
        except requests.RequestException as e:
            print(f"Error fetching species data: {e}")

    def fetch_and_display_abilities(self, primary_type, abilities):
        for widget in self.abilities_frame.winfo_children():
            widget.destroy()

        color = self.TYPE_COLORS_DETAILS.get(primary_type, "lightgrey")

        # Pokemon abilities customization.
        for ability in abilities:
            ability_name = ability["ability"]["name"].replace("-", " ").capitalize()
            ability_label = tk.Label(
                self.abilities_frame, 
                text=ability_name, 
                width=30, 
                bg=color, 
                font=tkfont.Font(family="Minecraft", size=14, weight="bold")
            )
            ability_label.pack(pady=5)


    def update_widget_borders(self, types):
        # Update Type 1 border color
        if types:
            type1_color = self.TYPE_COLORS_DETAILS.get(types[0].lower(), "lightgrey")
            self.type1.config(bg=type1_color)

        # Update Type 2 border color or reset if not available from database.
        if len(types) > 1:
            type2_color = self.TYPE_COLORS_DETAILS.get(types[1].lower(), "lightgrey")
            self.type2.config(bg=type2_color)
        else:
            self.type2.config(bg="lightgrey")

    def update_background(self, primary_type):
        bg_color = self.TYPE_COLORS_BACKGROUND.get(primary_type, "lightgrey")

        # Update background color for all frames and labels
        self.configure(bg=bg_color)
        self.nav_frame.config(bg=bg_color)
        self.shiny_checkbox.config(bg=bg_color)
        self.pokemon_name.config(bg=bg_color)
        self.pokemon_image.config(bg=bg_color)
        self.type_frame.config(bg=bg_color)
        self.description_box.config(bg=bg_color)
        self.description_label.config(bg=bg_color)
        self.details_box.config(bg=bg_color)
        self.height_label.config(bg=bg_color)
        self.weight_label.config(bg=bg_color)
        self.species_label.config(bg=bg_color)
        self.id_label.config(bg=bg_color)
        self.abilities_frame.config(bg=bg_color)

    # Load the Pokemon image witha dimension of 300x300
    def load_and_display_image(self, url):
        try:
            response = requests.get(url)
            image_data = Image.open(BytesIO(response.content))
            image_data = image_data.resize((300, 300), Image.LANCZOS)
            image = ImageTk.PhotoImage(image_data)
            self.pokemon_image.config(image=image)
            self.pokemon_image.image = image
        except requests.RequestException as e:
            print(f"Error loading image: {e}")

    # Search Bar Stuff
    def fetch_pokemon(self, event=None):
        pokemon_name = self.search_box.get().lower().strip()
        data = self.get_pokemon_data(pokemon_name)
        if data:
            # Update Pokémon details if a valid pokemon is inputted.
            self.pokemon_name.config(fg="black")
            self.update_pokemon_info(query=pokemon_name)
        else:
            # If wrong input display "POKEMON NOT FOUND" and remove most of the GUI
            self.pokemon_name.config(text="POKÉMON NOT FOUND")
            self.pokemon_image.config(image="")  # Remove the image
            self.type1.config(text="", bg="lightgrey")  # Reset pokemon type labels
            self.type2.config(text="", bg="lightgrey")
            self.description_label.config(text="")  # Delete pokemon description
            self.height_label.config(text="")  # Delete all details
            self.weight_label.config(text="")
            self.species_label.config(text="")
            self.id_label.config(text="")
            
            # Delete abilities
            for widget in self.abilities_frame.winfo_children():
                widget.destroy()

    def update_pokemon_image(self):
        if self.current_pokemon_data:
            image_url = (
                self.current_pokemon_data["sprites"]["front_shiny"]
                if self.shiny_var.get()
                else self.current_pokemon_data["sprites"]["front_default"]
            )
        self.load_and_display_image(image_url)

        # Update the Pokémon name with "SHINY" prefix if shiny is selected
        name_prefix = "SHINY " if self.shiny_var.get() else ""
        self.pokemon_name.config(text=f"{name_prefix}{self.current_pokemon_data['name'].upper()}")


    def prev_pokemon(self):
        if self.pokemon_index > 1:
            self.pokemon_index -= 1
            self.update_pokemon_info()

    def next_pokemon(self):
        self.pokemon_index += 1
        self.update_pokemon_info()    

if __name__ == "__main__":
    app = PokemonApp()
    app.mainloop()