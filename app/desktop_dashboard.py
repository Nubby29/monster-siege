import math
import tkinter as tk
from tkinter import ttk
from src.game.engine import SiegeEngine

WIDTH, HEIGHT = 900, 560
MAX_MAP_RADIUS = 290

class MonsterSiegeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monster Siege — Prototype 0.2")
        self.root.geometry("1000x760")
        self.root.minsize(850, 680)
        self.game = SiegeEngine()
        self.running = False
        self.last_tick_ms = None
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
        self.stats.pack(anchor="w", pady=(10, 4))
        self.threat = ttk.Progressbar(root, maximum=100, length=500)
        self.threat.pack(fill="x", pady=(0, 8))
        self.canvas = tk.Canvas(root, bg="#dfe7dc", highlightthickness=1, highlightbackground="#b9c2b5")
        self.canvas.pack(fill="both", expand=True)
        controls = ttk.Frame(root)
        controls.pack(fill="x", pady=(10, 0))
        self.toggle_button = ttk.Button(controls, text="Start Siege", command=self.toggle)
        self.toggle_button.pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Spawn Monster", command=self.spawn).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Advance 10 sec", command=self.advance).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Attack Nearest", command=self.attack_nearest).pack(side="left", padx=(0, 8))
        self.boss_button = ttk.Button(controls, text="Attack Boss", command=self.boss_attack, state="disabled")
        self.boss_button.pack(side="left", padx=(0, 8))
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
        self.game.advance(1)
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
        if self.game.state.raid_active:
            self.game.attack_boss()
            self.refresh()

    def reset(self):
        self.running = False
        self.toggle_button.config(text="Start Siege")
        self.game = SiegeEngine()
        self.refresh()

    def world_position(self, monster, cx, cy):
        angle = (monster.id * 2.399963) % (math.tau)
        radius = 38 + (min(monster.distance_m, 950) / 950) * (MAX_MAP_RADIUS - 38)
        return cx + math.cos(angle) * radius, cy + math.sin(angle) * radius

    def draw_world(self):
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), WIDTH)
        h = max(c.winfo_height(), HEIGHT)
        cx, cy = w / 2, h / 2
        c.create_text(16, 14, anchor="nw", text="LOCAL SIEGE ZONE · SCHEMATIC / NOT A REAL MAP",
                      fill="#526052", font=("Segoe UI", 10, "bold"))
        for r, label in [(MAX_MAP_RADIUS, "spawn"), (185, "approach"), (95, "danger")]:
            c.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#aab5a6", dash=(4, 5))
            c.create_text(cx + r - 8, cy - 9, anchor="e", text=label, fill="#718071",
                          font=("Segoe UI", 8))
        for x in (cx-300, cx-100, cx+120, cx+320):
            c.create_rectangle(x, cy-260, x+38, cy+260, fill="#d3dbd0", outline="")
        for y in (cy-210, cy-40, cy+140):
            c.create_rectangle(cx-430, y, cx+430, y+34, fill="#d3dbd0", outline="")
        boss = self.game.state.raid_boss
        if boss:
            c.create_oval(cx-105, cy-105, cx+105, cy+105, fill="#f3d4d4", outline="#b23a3a", width=4)
            c.create_text(cx, cy-8, text=boss.icon, font=("Segoe UI Emoji", 64))
            c.create_text(cx, cy+72, text=f"{boss.name} · {boss.hp}/{boss.max_hp} HP",
                          fill="#7f1d1d", font=("Segoe UI", 12, "bold"))
            c.create_text(cx, cy-145, text="RAID BOSS", fill="#991b1b", font=("Segoe UI", 18, "bold"))
        else:
            for monster in [m for m in self.game.monsters if m.alive]:
                x, y = self.world_position(monster, cx, cy)
                outline = "#b91c1c" if monster.distance_m <= 120 else "#c47b18" if monster.distance_m <= 350 else "#526b53"
                size = 30 if monster.rarity.value == "elite" else 25
                c.create_oval(x-size, y-size, x+size, y+size, fill="#fff", outline=outline, width=3)
                c.create_text(x, y-2, text=monster.icon, font=("Segoe UI Emoji", size))
                c.create_text(x, y+size+13, text=f"{monster.name}", fill="#293329", font=("Segoe UI", 9, "bold"))
                c.create_text(x, y+size+27, text=f"{monster.distance_m:.0f}m", fill="#526052", font=("Segoe UI", 8))
        c.create_oval(cx-48, cy-48, cx+48, cy+48, fill="#e7f0ff", outline="#2563eb", width=3)
        c.create_text(cx, cy-4, text="🏠", font=("Segoe UI Emoji", 30))
        c.create_text(cx, cy+34, text="YOUR BASE", fill="#1e40af", font=("Segoe UI", 9, "bold"))

    def refresh(self):
        s = self.game.state
        boss = s.raid_boss
        self.stats.config(text=f"Wave {s.wave}   |   Threat {s.threat}/{s.threat_threshold}   |   Defeated {s.defeated}   |   Coins {s.coins}   |   Monsters {sum(m.alive for m in self.game.monsters)}")
        self.threat["value"] = s.threat
        if boss:
            self.status.config(text=f"🚨 RAID BOSS INCOMING — {boss.icon} {boss.name} · {boss.hp}/{boss.max_hp} HP")
            self.boss_button.config(state="normal")
        else:
            nearest = min((m.distance_m for m in self.game.monsters if m.alive), default=None)
            text = "🏠 Siege active. Monsters are approaching your base."
            if nearest is not None:
                text += f" Nearest threat: {nearest:.0f}m."
            self.status.config(text=text)
            self.boss_button.config(state="disabled")
        self.draw_world()

if __name__ == "__main__":
    root = tk.Tk()
    MonsterSiegeApp(root)
    root.mainloop()
