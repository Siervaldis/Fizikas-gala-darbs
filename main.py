import tkinter as tk
from tkinter import ttk, messagebox
import math

G = 9.81        #gravitācijas paātrinājums


class CannonSimulator:
    def __init__(self, root):                   #programmas loga izskats
        self.root = root
        self.root.title("Lielgabala lodes trajektorijas simulators")
        self.root.geometry("1100x700")
        self.root.configure(bg="#e8f0f7")
                                                # inicializē animācijas mainīgos
        self.animation_points = []
        self.current_index = 0
        self.projectile = None
        self.path_segments = []
        self.is_animating = False

        self.setup_ui()              #izsauc funkciju, kas izveido interfeisu

    def setup_ui(self):                         #interfeiss
        title = tk.Label(                        #virsraksts
            self.root,
            text="Lielgabala lodes trajektorijas simulators",
            font=("Arial", 20, "bold"),
            bg="#e8f0f7",
            fg="#1f3b5b"
        )
        title.pack(pady=10)

                                                                                    #kopējais logs
        main_frame = tk.Frame(self.root, bg="#e8f0f7")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

                                                                                     #ievades daļa
        left_frame = tk.Frame(main_frame, bg="#dce7f2", bd=2, relief="groove")
        left_frame.pack(side="left", fill="y", padx=(0, 10))
                                                                                    #grafika daļa
        right_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove")
        right_frame.pack(side="right", fill="both", expand=True)

        self.build_controls(left_frame)                                             #izveido ievades laukus
        self.build_canvas(right_frame)                                              #izveido grafisko lauku

    def build_controls(self, parent):
        tk.Label(
            parent,                                                                  #virsraksts ievadei
            text="Ievades dati",
            font=("Arial", 16, "bold"),
            bg="#dce7f2",
            fg="#1f3b5b"
        ).pack(pady=12)

        form_frame = tk.Frame(parent, bg="#dce7f2")
        form_frame.pack(padx=15, pady=10)
                                                    #sākuma ātruma ievade
        tk.Label(
            form_frame,
            text="Sākuma ātrums v₀ (m/s):",
            font=("Arial", 11),
            bg="#dce7f2"
        ).grid(row=0, column=0, sticky="w", pady=6)

        self.entry_v0 = ttk.Entry(form_frame, width=18)
        self.entry_v0.grid(row=0, column=1, pady=6)
        self.entry_v0.insert(0, "20")       #noklusējuma vērtība

        tk.Label(                                       #leņķa ievade
            form_frame,
            text="Leņķis α (°):",
            font=("Arial", 11),
            bg="#dce7f2"
        ).grid(row=1, column=0, sticky="w", pady=6)

        self.entry_angle = ttk.Entry(form_frame, width=18)
        self.entry_angle.grid(row=1, column=1, pady=6)
        self.entry_angle.insert(0, "45")

        tk.Label(
            form_frame,                                     #masas ievade
            text="Masa m (kg):",
            font=("Arial", 11),
            bg="#dce7f2"
        ).grid(row=2, column=0, sticky="w", pady=6)

        self.entry_mass = ttk.Entry(form_frame, width=18)
        self.entry_mass.grid(row=2, column=1, pady=6)
        self.entry_mass.insert(0, "2")

        button_frame = tk.Frame(parent, bg="#dce7f2")       #rāmis ap tekstu
        button_frame.pack(pady=10)
                                                        #pogas
        ttk.Button(button_frame, text="Izšaut", command=self.start_simulation).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Notīrīt", command=self.clear_canvas).grid(row=0, column=1, padx=5)

        example_frame = tk.Frame(parent, bg="#dce7f2")      #rāmis ap pogām
        example_frame.pack(padx=15, pady=8, fill="x")

        tk.Label(
            example_frame,                              #izveido piemēru
            text="Piemērs:\nv₀ = 20 m/s\nα = 45°\nm = 2 kg",
            font=("Arial", 10),
            bg="#dce7f2",
            justify="left"
        ).pack(anchor="w")

        result_title = tk.Label(                        #izveido virsrakstu rezultāti
            parent,
            text="Rezultāti",
            font=("Arial", 15, "bold"),
            bg="#dce7f2",
            fg="#1f3b5b"
        )
        result_title.pack(pady=(15, 5))

        self.result_label = tk.Label(                   #rezultātu logs
            parent,
            text="Šeit parādīsies rezultāti",
            font=("Consolas", 11),
            bg="#f7fbff",
            fg="#222222",
            justify="left",
            anchor="nw",
            width=30,
            height=14,
            relief="sunken",
            bd=1
        )
        self.result_label.pack(padx=15, pady=(0, 15), fill="both")

    def build_canvas(self, parent):                             #izveido zīmēšanas laukumu
        self.canvas = tk.Canvas(parent, bg="#ffffff", width=760, height=620, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas_width = 760
        self.canvas_height = 620
        self.ground_y = 560                                     #zemes līnija
        self.origin_x = 80                                      #sākuma x koordinātas

        self.draw_static_scene()                                #uzzīmē fonu

    def draw_static_scene(self):
        self.canvas.delete("all")                               #notīra visu

        self.canvas.create_rectangle(                           #uzzīmē zemi
            0, self.ground_y, self.canvas_width, self.canvas_height,
            fill="#cfe8b4", outline=""
        )
        self.canvas.create_line(                                #uzzīmē asi
            0, self.ground_y, self.canvas_width, self.ground_y,
            width=3, fill="#3d5a2b"
        )

        self.canvas.create_text(35, 25, text="y", font=("Arial", 12, "bold"))
        self.canvas.create_text(
            self.canvas_width - 15, self.ground_y + 20,
            text="x", font=("Arial", 12, "bold")
        )

        self.canvas.create_line(
            self.origin_x, self.ground_y,
            self.origin_x, 20,
            width=2, arrow="last"
        )
        self.canvas.create_line(
            self.origin_x, self.ground_y,
            self.canvas_width - 20, self.ground_y,
            width=2, arrow="last"
        )

        self.draw_cannon()                          #uzzīmē lielgabalu

    def draw_cannon(self, angle_deg=45):
        base_x = self.origin_x
        base_y = self.ground_y

        self.canvas.create_oval(
            base_x - 20, base_y - 20,
            base_x + 20, base_y + 20,
            fill="#444444", outline="#222222", width=2
        )

        barrel_length = 60
        angle_rad = math.radians(angle_deg)
        end_x = base_x + barrel_length * math.cos(angle_rad)
        end_y = base_y - barrel_length * math.sin(angle_rad)

        self.canvas.create_line(
            base_x, base_y, end_x, end_y,
            width=12, fill="#666666", capstyle="round"
        )

    def validate_inputs(self):
        try:
                                                #Pārvērš ievadi par skaitļiem
            v0 = float(self.entry_v0.get())
            angle_deg = float(self.entry_angle.get())
            mass = float(self.entry_mass.get())
                                                #pārbaudes
            if v0 <= 0:
                raise ValueError("Sākuma ātrumam jābūt lielākam par 0.")
            if mass <= 0:
                raise ValueError("Masai jābūt lielākai par 0.")
            if angle_deg < 0 or angle_deg > 90:
                raise ValueError("Leņķim jābūt no 0 līdz 90 grādiem.")

            return v0, angle_deg, mass

        except ValueError as e:
            messagebox.showerror("Ievades kļūda", str(e))
            return None

    def calculate_trajectory(self, v0, angle_deg):
        angle_rad = math.radians(angle_deg)      #pārvērš grādus radiānos
        v0x = v0 * math.cos(angle_rad)          #aprēķina horizontālo komponenti
        v0y = v0 * math.sin(angle_rad)          #aprēķina vertikālo komponenti

        points = []                             #saglabās punktus
        dt = 0.03                               #laika solis
        t = 0.0

        while True:
            x = v0x * t     #aprēķina horizontālo attālumu
            y = v0y * t - 0.5 * G * t * t    #aprēķina augstumu

            if y < 0:
                break

            points.append((x, y))                #palielina punktu
            t += dt                              #saglabā laiku

        return points, v0x, v0y

    def get_scale(self, points):
        if not points:                          #izmaina mērrogu
            return 10

        max_x = max(p[0] for p in points)
        max_y = max(p[1] for p in points)

        usable_width = self.canvas_width - self.origin_x - 40
        usable_height = self.ground_y - 40

        scale_x = usable_width / max(max_x, 1)
        scale_y = usable_height / max(max_y, 1) if max_y > 0 else 10

        scale = min(scale_x, scale_y)
        return max(scale, 2)
                                                    #pārveido fizikas koordinātas (x, y) uz ekrāna koordinātām.
    def physics_to_screen(self, x, y, scale):
        screen_x = self.origin_x + x * scale
        screen_y = self.ground_y - y * scale
        return screen_x, screen_y

    def display_results(self, v0, angle_deg, mass, v0x, v0y):
        angle_rad = math.radians(angle_deg)
        energy = 0.5 * mass * v0 * v0       #kinētiskā enerģija
        flight_time = (2 * v0 * math.sin(angle_rad)) / G    #lidojuma laiks
        max_height = (v0y ** 2) / (2 * G)   #maksimālais augstums
        distance = v0x * flight_time        #Lidojuma attālums

        text = (
            f"v₀x       = {v0x:.2f} m/s\n"
            f"v₀y       = {v0y:.2f} m/s\n"
            f"Laiks     = {flight_time:.2f} s\n"
            f"Augstums  = {max_height:.2f} m\n"
            f"Attālums  = {distance:.2f} m\n"
            f"Enerģija  = {energy:.2f} J\n\n"
        )

        self.result_label.config(text=text)
                                                    #animācija
    def start_simulation(self):
        if self.is_animating:
            return

        values = self.validate_inputs()             #pārbauda ievades datus
        if values is None:
            return

        v0, angle_deg, mass = values                #saglabā ievadītās vērtības

        self.clear_canvas(redraw_only=True)
        self.draw_cannon(angle_deg)

        points, v0x, v0y = self.calculate_trajectory(v0, angle_deg)     # Aprēķina trajektoriju
        self.display_results(v0, angle_deg, mass, v0x, v0y)             #parāda rezultātus

        scale = self.get_scale(points)                                  #dabū mērrogu

        self.animation_points = [
            self.physics_to_screen(x, y, scale) for x, y in points      #pārvērš kordinātes
        ]
        self.current_index = 0                                          #sāk animāciju no pirmā punkta
        self.path_segments = []                                         #notīra ieprieksējo trajektoriju
        self.is_animating = True                                        #atzīmē ka animācija ir sākta

        if self.animation_points:                                       #uzzīmē lodi
            x, y = self.animation_points[0]
            self.projectile = self.canvas.create_oval(
                x - 7, y - 7, x + 7, y + 7,
                fill="#d62828", outline="#7f0000", width=2
            )
            self.animate()                                              #palaiž animāciju

    def animate(self):
        if self.current_index >= len(self.animation_points):            #ja visi animācijas punkti izmantoti
            self.is_animating = False                                   #animacija beidzas
            return                                                      #funkcija apstājas

        x, y = self.animation_points[self.current_index]                #dabū pašreizējā punkta koordinātas

        if self.projectile is not None:
            self.canvas.coords(self.projectile, x - 7, y - 7, x + 7, y + 7) #pārvieto lodi uz jaunu punktu ekrānā

        if self.current_index > 0:
            prev_x, prev_y = self.animation_points[self.current_index - 1]  #dabū iepriekšējo punktu
            segment = self.canvas.create_line(                              #un savieno ar līniju
                prev_x, prev_y, x, y,
                fill="#ff7b00", width=2
            )
            self.path_segments.append(segment)

        self.current_index += 1                                         #pāriet pie nākamā punkta
        self.root.after(20, self.animate)                               #pēc 20 milisekundēm izsauc funkciju vēlreiz

                                                                        #definē funkciju kas notīra kanvu
    def clear_canvas(self, redraw_only=False):
        self.is_animating = False                                       #pārtrauc animāciju
        self.animation_points = []
        self.current_index = 0                                          #atiestata ar ar animāciju saaistītos mainīgos
        self.projectile = None
        self.path_segments = []

        self.draw_static_scene()

        if not redraw_only:
            self.result_label.config(text="Šeit parādīsies rezultāti")


if __name__ == "__main__":          #pārbauda, vai šis fails tiek palaists kā galvenā programma
    root = tk.Tk()                  #izveido galveno logu

    style = ttk.Style()             #iestata vizuālo noformējumu pogām un ievades laukiem
    style.theme_use("clam")
    style.configure("TButton", font=("Arial", 10), padding=6)
    style.configure("TEntry", padding=5)

    app = CannonSimulator(root)         #izveido simulatora objektu un palaiž visas klases funkcijas
    root.mainloop()                     #palaiž programmas galveno ciklu, lai logs paliktu aktīvs un reaģētu uz lietotāja darbībām