import tkinter as tk
from tkinter import ttk
from src.game.engine import SiegeEngine

class MonsterSiegeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monster Siege — Prototype")
        self.root.geometry("760x620")
        self.game = SiegeEngine()
        self.build()
        self.refresh()

    def build(self):
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="MONSTER SIEGE", font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(frame, text="The monsters come to you.", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 14))
        self.stats = ttk.Label(frame, text="")
        self.stats.pack(anchor="w")
        self.status = ttk.Label(frame, text="", font=("Segoe UI", 12, "bold"))
        self.status.pack(anchor="w", pady=10)
        self.listbox = tk.Listbox(frame, height=16, font=("Segoe UI", 11))
        self.listbox.pack(fill="both", expand=True)
        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=12)
        ttk.Button(actions, text="Spawn Monster", command=self.spawn).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Advance 10 sec", command=self.advance).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Attack Selected", command=self.attack).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Attack Raid Boss", command=self.boss_attack).pack(side="left")

    def spawn(self):
        self.game.spawn_monster()
        self.refresh()

    def advance(self):
        self.game.advance(10)
        self.refresh()

    def attack(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        living = [m for m in self.game.monsters if m.alive]
        if selection[0] < len(living):
            self.game.attack(living[selection[0]].id)
        self.refresh()

    def boss_attack(self):
        self.game.attack_boss()
        self.refresh()

    def refresh(self):
        s = self.game.state
        boss = s.raid_boss
        self.stats.config(text=f"Wave {s.wave}   |   Threat {s.threat}/{s.threat_threshold}   |   Defeated {s.defeated}   |   Coins {s.coins}")
        self.status.config(text=(f"RAID BOSS: {boss.icon} {boss.name} — {boss.hp}/{boss.max_hp} HP" if boss else "BASE STATUS: Your home is under siege."))
        self.listbox.delete(0, tk.END)
        for m in [x for x in self.game.monsters if x.alive]:
            self.listbox.insert(tk.END, f"{m.icon} {m.name} [{m.rarity.value}] — {m.distance}m — {m.hp} HP — +{m.threat_value} threat")

if __name__ == "__main__":
    root = tk.Tk()
    MonsterSiegeApp(root)
    root.mainloop()
