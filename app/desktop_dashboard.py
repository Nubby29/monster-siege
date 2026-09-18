import math
import tkinter as tk
from tkinter import ttk
from src.game.engine import SiegeEngine

WIDTH, HEIGHT = 900, 560
CENTER = (WIDTH // 2, HEIGHT // 2)

class MonsterSiegeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monster Siege — Visual Prototype")
        self.root.geometry("980x760")
        self.root.minsize(820, 680)
        self.game = SiegeEngine()
        self.running = False
        self.build()
        self.refresh()

    def build(self):
        root = ttk.Frame(self.root, padding=14)
        root.pack(fill="both", expand=True)

        header = ttk.Frame(root)
        header.pack(fill="x")
        ttk.Label(header, text="MONSTER SIEGE", font=("Segoe UI", 24, "bold")).pack(side="left")
        ttk.Label(header, text="The monsters come to you.", font=("Segoe UI", 11)).pack(side="left", padx=14, pady=(8, 0))

        self.stats = ttk.Label(root, font=("Segoe UI", 11))
        self.stats.pack(anchor="w", pady=(10, 5))

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#dfe7dc",
                                highlightthickness=1, highlightbackground="#b9c2b5")
        self.canvas.pack(fill="both", expand=True)

        controls = ttk.Frame(root)
        controls.pack(fill="x", pady=(10, 0))
        self.toggle_button = ttk.Button(controls, text="Start Siege", command=self.toggle)
        self.toggle_button.pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Spawn Monster", command=self.spawn).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Advance 10 sec", command=self.advance).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Attack Nearest", command=self.attack_nearest).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Attack Boss", command=self.boss_attack).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Reset", command=self.reset).pack(side="right")

        self.status = ttk.Label(root, font=("Segoe UI", 12, "bold"))
        self.status.pack(anchor="w", pady=(8, 0))

    def toggle(self):
        self.running = not self.running
        self.toggle_button.config(text="Pause Siege" if self.running else "Start Siege")
        if self.running:
            self.tick()

    def tick(self):
        if not self.running:
            return
        self.game.advance(5)
        self.refresh()
        self.root.after(1000, self.tick)

    def spawn(self):
        self.game.spawn_monster()
        self.refresh()

    def advance(self):
        self.game.advance(10)
        self.refresh()

    def attack_nearest(self):
        living = [m for m in self.game.monsters if m.alive]
        if living:
            target = min(living, key=lambda m: m.distance_m)
            self.game.attack(target.id)
            self.refresh()

    def boss_attack(self):
        self.game.attack_boss()
        self.refresh()

    def reset(self):
        self.running = False
        self.toggle_button.config(text="Start Siege")
        self.game = SiegeEngine()
        self.refresh()

    def world_position(self, monster):
        # Deterministic angle from monster id; distance controls how close it is.
        angle = (monster.id * 2.399963) % (math.tau)
        max_distance = 900.0
        radius = 35 + (min(monster.distance_m, max_distance) / max_distance) * 230
        return CENTER[0] + math.cos(angle) * radius, CENTER[1] + math.sin(angle) * radius

    def draw_world(self):
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), WIDTH)
        h = max(c.winfo_height(), HEIGHT)
        cx, cy = w / 2, h / 2

        # Quiet, schematic neighborhood. This is not a real map.
        c.create_text(16, 14, anchor="nw", text="LOCAL SIEGE ZONE · SCHEMATIC", fill="#526052",
                      font=("Segoe UI", 10, "bold"))
        for r, label in [(260, "spawn zone"), (175, "approach zone"), (90, "base zone")]:
            c.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#aab5a6", dash=(4, 5))
            c.create_text(cx + r - 5, cy - 8, anchor="e", text=label, fill="#718071",
                          font=("Segoe UI", 8))

        # Roads / blocks
        for x in (cx-300, cx-100, cx+120, cx+320):
            c.create_rectangle(x, cy-260, x+38, cy+260, fill="#d3dbd0", outline="")
        for y in (cy-210, cy-40, cy+140):
            c.create_rectangle(cx-430, y, cx+430, y+34, fill="#d3dbd0", outline="")

        boss = self.game.state.raid_boss
        if boss:
            c.create_oval(cx-72, cy-72, cx+72, cy+72, fill="#f3d4d4", outline="#b23a3a", width=3)
            c.create_text(cx, cy-8, text=boss.icon, font=("Segoe UI Emoji", 52))
            c.create_text(cx, cy+55, text=f"{boss.name} · {boss.hp}/{boss.max_hp} HP",
                          fill="#7f1d1d", font=("Segoe UI", 11, "bold"))
        else:
            for monster in [m for m in self.game.monsters if m.alive]:
                x, y = self.world_position(monster)
                if monster.distance_m <= 120:
                    outline = "#b91c1c"
                elif monster.distance_m <= 350:
                    outline = "#c47b18"
                else:
                    outline = "#526b53"
                c.create_oval(x-27, y-27, x+27, y+27, fill="#fff", outline=outline, width=3)
                c.create_text(x, y-2, text=monster.icon, font=("Segoe UI Emoji", 26))
                c.create_text(x, y+38, text=f"{monster.name} · {monster.distance_m:.0f}m",
                              fill="#293329", font=("Segoe UI", 9, "bold"))

        # Base always sits in the center.
        c.create_oval(cx-43, cy-43, cx+43, cy+43, fill="#e7f0ff", outline="#2563eb", width=3)
        c.create_text(cx, cy-2, text="🏠", font=("Segoe UI Emoji", 28))
        c.create_text(cx, cy+30, text="YOUR BASE", fill="#1e40af", font=("Segoe UI", 9, "bold"))

    def refresh(self):
        s = self.game.state
        boss = s.raid_boss
        self.stats.config(text=f"Wave {s.wave}   |   Threat {s.threat}/{s.threat_threshold}   |   Defeated {s.defeated}   |   Coins {s.coins}")
        if boss:
            self.status.config(text=f"RAID BOSS INCOMING: {boss.icon} {boss.name} — attack the boss to clear the wave")
        else:
            nearest = min((m.distance_m for m in self.game.monsters if m.alive), default=None)
            distance_text = f" · Nearest threat: {nearest:.0f}m" if nearest is not None else ""
            self.status.config(text=f"🏠 Your base is under siege{distance_text}.")
        self.draw_world()

if __name__ == "__main__":
    root = tk.Tk()
    MonsterSiegeApp(root)
    root.mainloop()
