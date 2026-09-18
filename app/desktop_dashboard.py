import math
import tkinter as tk
from tkinter import ttk
from src.game.engine import SiegeEngine

WIDTH, HEIGHT = 900, 560
MAX_MAP_RADIUS = 290

class MonsterSiegeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monster Siege — Prototype 0.4")
        self.root.geometry("1080x800")
        self.root.minsize(900, 720)
        self.game = SiegeEngine()
        self.running = False
        self.selected_id = None
        self.message = "Click a monster on the map to encounter it."
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
        self.base_bar = ttk.Progressbar(root, maximum=100)
        self.base_bar.pack(fill="x", pady=(0, 4))
        self.threat = ttk.Progressbar(root, maximum=100)
        self.threat.pack(fill="x", pady=(0, 8))

        body = ttk.Frame(root)
        body.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(body, bg="#dfe7dc", highlightthickness=1, highlightbackground="#b9c2b5")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.map_click)

        encounter = ttk.Frame(body, padding=(14, 8))
        encounter.pack(side="right", fill="y")
        ttk.Label(encounter, text="ENCOUNTER", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Separator(encounter).pack(fill="x", pady=8)
        self.encounter_icon = ttk.Label(encounter, text="👾", font=("Segoe UI Emoji", 42))
        self.encounter_icon.pack(pady=(10, 4))
        self.encounter_name = ttk.Label(encounter, text="No target", font=("Segoe UI", 14, "bold"))
        self.encounter_name.pack()
        self.encounter_info = ttk.Label(encounter, text="Select a monster.", justify="center")
        self.encounter_info.pack(pady=8)
        self.hp_bar = ttk.Progressbar(encounter, maximum=100, length=180)
        self.hp_bar.pack(pady=4)
        self.hp_label = ttk.Label(encounter, text="")
        self.hp_label.pack()
        self.attack_button = ttk.Button(encounter, text="⚔ Attack", command=self.attack_selected, state="disabled")
        self.attack_button.pack(fill="x", pady=(16, 6))
        self.flee_button = ttk.Button(encounter, text="Flee", command=self.flee, state="disabled")
        self.flee_button.pack(fill="x")
        self.encounter_message = ttk.Label(encounter, text="", wraplength=190, justify="center")
        self.encounter_message.pack(pady=18)

        controls = ttk.Frame(root)
        controls.pack(fill="x", pady=(10, 0))
        self.toggle_button = ttk.Button(controls, text="Start Siege", command=self.toggle)
        self.toggle_button.pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Spawn Monster", command=self.spawn).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Advance 10 sec", command=self.advance).pack(side="left", padx=(0, 8))
        self.boss_button = ttk.Button(controls, text="⚔ Attack Boss", command=self.boss_attack, state="disabled")
        self.boss_button.pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Reset", command=self.reset).pack(side="right")
        self.status = ttk.Label(root, font=("Segoe UI", 12, "bold"))
        self.status.pack(anchor="w", pady=(8, 0))

    def toggle(self):
        if self.game.state.game_over:
            return
        self.running = not self.running
        self.toggle_button.config(text="Pause Siege" if self.running else "Start Siege")
        if self.running:
            self.tick()

    def tick(self):
        if not self.running:
            return
        self.game.advance(1)
        self.refresh()
        if not self.game.state.game_over:
            self.root.after(1000, self.tick)

    def spawn(self):
        self.game.spawn_monster()
        self.refresh()

    def advance(self):
        self.game.advance(10)
        self.refresh()

    def get_selected(self):
        if self.selected_id is None:
            return None
        return next((m for m in self.game.monsters if m.id == self.selected_id and m.alive), None)

    def attack_selected(self):
        monster = self.get_selected()
        if not monster:
            self.selected_id = None
            self.refresh()
            return
        before = monster.hp
        self.game.attack(monster.id, 25)
        if monster.alive:
            self.message = f"You dealt {before - monster.hp} damage. It is still {monster.distance_m:.0f}m away."
        else:
            self.message = f"{monster.name} defeated! +{5 + monster.threat_value} coins."
            self.selected_id = None
        self.refresh()

    def flee(self):
        monster = self.get_selected()
        if monster:
            self.message = f"You fled from {monster.name}. It keeps approaching."
        self.selected_id = None
        self.refresh()

    def boss_attack(self):
        boss = self.game.state.raid_boss
        if boss:
            before = boss.hp
            self.game.attack_boss(35)
            if self.game.state.raid_active:
                self.message = f"You dealt {before - boss.hp} damage to {boss.name}."
            else:
                self.message = "RAID CLEARED! The next invasion is beginning."
        self.refresh()

    def reset(self):
        self.running = False
        self.toggle_button.config(text="Start Siege")
        self.game = SiegeEngine()
        self.selected_id = None
        self.message = "Click a monster on the map to encounter it."
        self.refresh()

    def world_position(self, monster, cx, cy):
        angle = (monster.id * 2.399963) % (math.tau)
        radius = 38 + (min(monster.distance_m, 950) / 950) * (MAX_MAP_RADIUS - 38)
        return cx + math.cos(angle) * radius, cy + math.sin(angle) * radius

    def map_click(self, event):
        if self.game.state.raid_active or self.game.state.game_over:
            return
        w = max(self.canvas.winfo_width(), WIDTH)
        h = max(self.canvas.winfo_height(), HEIGHT)
        cx, cy = w / 2, h / 2
        closest = None
        closest_distance = 40
        for monster in [m for m in self.game.monsters if m.alive]:
            x, y = self.world_position(monster, cx, cy)
            distance = math.hypot(event.x - x, event.y - y)
            if distance < closest_distance:
                closest = monster
                closest_distance = distance
        if closest:
            self.selected_id = closest.id
            self.message = f"{closest.name} is {closest.distance_m:.0f}m from your base."
            self.refresh()

    def draw_world(self):
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), WIDTH)
        h = max(c.winfo_height(), HEIGHT)
        cx, cy = w / 2, h / 2
        c.create_text(16, 14, anchor="nw", text="LOCAL SIEGE ZONE · SCHEMATIC / NOT A REAL MAP",
                      fill="#526052", font=("Segoe UI", 10, "bold"))

        for r, label in [(MAX_MAP_RADIUS, "SPAWN"), (185, "APPROACH"), (95, "DANGER")]:
            c.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#aab5a6", dash=(4, 5))
            c.create_text(cx + r - 8, cy - 9, anchor="e", text=label, fill="#718071",
                          font=("Segoe UI", 8, "bold"))

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
                selected = monster.id == self.selected_id
                if monster.distance_m <= 120:
                    outline = "#b91c1c"
                elif monster.distance_m <= 350:
                    outline = "#c47b18"
                else:
                    outline = "#526b53"
                if monster.breached:
                    outline = "#7f1d1d"
                size = 31 if monster.rarity.value == "elite" else 25
                if selected:
                    c.create_oval(x-size-7, y-size-7, x+size+7, y+size+7, outline="#2563eb", width=2)
                c.create_oval(x-size, y-size, x+size, y+size, fill="#fff", outline=outline, width=3)
                c.create_text(x, y-2, text=monster.icon, font=("Segoe UI Emoji", size))
                label = "BREACH!" if monster.breached else monster.name
                c.create_text(x, y+size+13, text=label, fill="#7f1d1d" if monster.breached else "#293329",
                              font=("Segoe UI", 9, "bold"))
                c.create_text(x, y+size+27, text=f"{monster.distance_m:.0f}m", fill="#526052", font=("Segoe UI", 8))

        c.create_oval(cx-48, cy-48, cx+48, cy+48, fill="#e7f0ff", outline="#2563eb", width=3)
        c.create_text(cx, cy-4, text="🏠", font=("Segoe UI Emoji", 30))
        c.create_text(cx, cy+34, text="YOUR BASE", fill="#1e40af", font=("Segoe UI", 9, "bold"))

        if self.game.state.game_over:
            c.create_rectangle(cx-240, cy-70, cx+240, cy+70, fill="#fff", outline="#b91c1c", width=3)
            c.create_text(cx, cy-25, text="BASE DESTROYED", fill="#991b1b", font=("Segoe UI", 24, "bold"))
            c.create_text(cx, cy+18, text="Press Reset to begin a new siege.", fill="#526052", font=("Segoe UI", 11))

    def refresh(self):
        s = self.game.state
        boss = s.raid_boss
        living = [m for m in self.game.monsters if m.alive]
        self.stats.config(text=f"Wave {s.wave}   |   Base HP {s.base_hp}/{s.max_base_hp}   |   Threat {s.threat}/{s.threat_threshold}   |   Defeated {s.defeated}   |   Coins {s.coins}   |   Monsters {len(living)}")
        self.base_bar["value"] = s.base_hp
        self.threat["value"] = s.threat

        selected = self.get_selected()
        if selected and not boss:
            self.encounter_icon.config(text=selected.icon)
            self.encounter_name.config(text=selected.name)
            distance_state = "BREACHED" if selected.breached else (
                "CRITICAL" if selected.distance_m <= 120 else
                "DANGER" if selected.distance_m <= 350 else "APPROACHING"
            )
            self.encounter_info.config(text=f"{selected.rarity.value.title()} · {distance_state}\n{selected.distance_m:.0f}m from base")
            self.hp_bar["value"] = (selected.hp / 35) * 100
            self.hp_label.config(text=f"HP {selected.hp}/35")
            self.attack_button.config(state="disabled" if s.game_over else "normal")
            self.flee_button.config(state="disabled" if s.game_over else "normal")
            self.encounter_message.config(text=self.message)
        else:
            self.encounter_icon.config(text=boss.icon if boss else "👾")
            self.encounter_name.config(text=boss.name if boss else "No target")
            self.encounter_info.config(text=f"Raid battle\n{boss.hp}/{boss.max_hp} HP" if boss else "Click a monster on the map.")
            self.hp_bar["value"] = ((boss.hp / boss.max_hp) * 100) if boss else 0
            self.hp_label.config(text=f"HP {boss.hp}/{boss.max_hp}" if boss else "")
            self.attack_button.config(state="disabled")
            self.flee_button.config(state="disabled")
            self.encounter_message.config(text=self.message)

        if s.game_over:
            self.status.config(text="💥 YOUR BASE HAS BEEN DESTROYED — reset to start another siege.")
            self.boss_button.config(state="disabled")
            self.running = False
            self.toggle_button.config(text="Start Siege")
        elif boss:
            self.status.config(text=f"🚨 RAID BOSS INCOMING — {boss.icon} {boss.name} · {boss.hp}/{boss.max_hp} HP")
            self.boss_button.config(state="normal")
        else:
            nearest = min((m.distance_m for m in living), default=None)
            breached = sum(m.breached for m in living)
            status = "🏠 Siege active. Click a monster to fight it."
            if nearest is not None:
                status += f" Nearest threat: {nearest:.0f}m."
            if breached:
                status += f" ⚠ {breached} monster(s) at the base!"
            self.status.config(text=status)
            self.boss_button.config(state="disabled")

        self.draw_world()

    def destroy(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    MonsterSiegeApp(root)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
