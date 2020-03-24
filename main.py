import tkinter as tk
from tkinter import ttk, colorchooser as clr, messagebox as msg
from math import cos, sin, pi
from itertools import permutations
from typing import *


def non_repeating_per(l):
    result = []
    for i in permutations(l):
        for j in result:
            if is_same_alignment(i, j):
                break
        else:
            result.append(i)
            yield i


def is_same_alignment(l1, l2):
    for i in range(len(l1)):
        if l1 == l2[i:] + l2[:i]:
            return True
    return False


class Instruction(tk.Toplevel):
    def __init__(self, *args, text: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes("-topmost", True)
        self.resizable(False, False)
        
        self.title("Bilgi")
        
        self.info_title = ttk.Label(self, text="BİLGİ")
        self.info_title.pack(expand=True, pady=20)
        self.instruction_text = ttk.Label(self, text=text)
        self.instruction_text.pack(
            expand=True, padx=20, pady=20
        )
    
    def show(self):
        self.deiconify()
        self.transient(self.master)
        self.grab_set()


class CustomCanvas(tk.Canvas):
    def __init__(self, parent, r=200, **kw):
        super().__init__(parent, width=r * 2, height=r * 2, **kw)
        
        self.r = r

    def draw_perm(self, bead_colors: List[str]):
        self.delete("all")
        
        screen_spacing = 15
        
        total_points = len(bead_colors)
        
        r = self.r - screen_spacing
        point_r = 10
        
        self.create_oval(
            screen_spacing, screen_spacing,
            r * 2 + screen_spacing,
            r * 2 + screen_spacing,
            outline="light gray", width=5
        )
        
        for i, bead_color in enumerate(bead_colors):
            angle = (i * pi * 2) / total_points - pi / 2
            x = r * cos(angle) + r + screen_spacing
            y = r * sin(angle) + r + screen_spacing
            
            self.create_oval(
                x - point_r, y - point_r, x + point_r, y + point_r,
                fill=bead_color
            )


class ColorFrame(tk.LabelFrame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.color = None

        self.color_select_button = ttk.Button(
            self, text="Renk Seç".center(20), command=self.button_command
        )
        self.color_count_entry = ttk.Entry(self, width=11)

        self.grid_widgets()

    def grid_widgets(self):
        self.color_select_button.pack(side="left", fill="x")
        self.color_count_entry.pack(side="right", fill="x", padx=3)

    def button_command(self):
        color = clr.askcolor()
        if color != (None, None):
            rgb_color, hex_color = color
            self.color = hex_color
            self.color_select_button.config(text=[int(i) for i in rgb_color])
            self.config(bg=hex_color)
    
    def color_count(self):
        if self.color_count_entry.get().isdecimal():
            return int(self.color_count_entry.get())
        return False


class BeadAlignment(tk.Tk):
    def __init__(self, *args, r: int = 300, **kwargs):
        super().__init__(*args, **kwargs)
        self.resizable(False, False)
        self.config(bg="gray")

        self.permutations = []
        self.len_per = 0
        self.per_iterator = iter(self.permutations)
        self.align_index = 0
        self.known_permutations = []
        
        self.canvas = CustomCanvas(self, r=r)
        self.canvas.config(bg="#dddddd")
        
        self.nav_bar = tk.Frame(self)
        self.back_button = ttk.Button(
            self.nav_bar, text="Geri", command=self.nav_back
        )
        self.nav_label = tk.Label(self.nav_bar, text="? / ?")
        self.forward_button = ttk.Button(
            self.nav_bar, text="İleri", command=self.nav_forward
        )

        self.hud = tk.Frame(self)
        self.hud_main = tk.LabelFrame(self.hud)
        
        self.info_button = ttk.Button(
            self.hud_main, text="?", command=self.instruction
        )
        
        self.color_frame_list = []
        self.colors_frame = tk.Frame(self.hud_main)

        self.color_cfg_frame = tk.LabelFrame(self.hud_main)
        self.color_add_button = ttk.Button(
            self.color_cfg_frame, text="+", command=self.add_color
        )
        self.color_del_button = ttk.Button(
            self.color_cfg_frame, text="-", command=self.del_color
        )

        self.calc_button = ttk.Button(
            self.hud_main, text="HESAPLA: ", command=self.calculate
        )

        self.place_widgets()

    def instruction(self):
        text = open(file="instruction.txt", mode="r", encoding="utf-8").read()
        Instruction(self, text=text).show()

    def nav_back(self):
        if self.align_index > 0:
            self.align_index -= 1
            self.draw_alignment_by_index(self.align_index)
 
    def nav_forward(self):
        if self.draw_alignment_by_index(self.align_index + 1) is False:
            self.align_index += 1
        else:
            msg.showwarning(
                "Uyarı !",
                """
                Hesaplanan tüm dizilimleri zaten gördünüz !
                """
            ) 

    def add_color(self):
        new_frame = ColorFrame(self.colors_frame)
        self.color_frame_list.append(new_frame)
        new_frame.pack(fill="x")

    def del_color(self):
        if len(self.color_frame_list) > 1:
            self.color_frame_list[-1].pack_forget()
            self.color_frame_list[-1].destroy()
            self.color_frame_list.pop()

    def calculate(self):
        color_list = []
        for color_frame in self.color_frame_list:
            if color_frame.color is None:
                msg.showwarning(
                    "Uyarı !",
                    """
                    Lütfen renk seçimlerini yaptığınızdan
                    emin olunuz !
                    """
                )
                return
            if not color_frame.color_count():
                msg.showwarning(
                    "Uyarı !",
                    """
                    Lütfen tüm renklere ait boncuk sayılarını sayı
                    cinsinden giriniz !
                    """)
                return
            for _ in range(color_frame.color_count()):
                color_list.append(color_frame.color)
        
        self.permutations = non_repeating_per(color_list)
        self.per_iterator = iter(self.permutations)
        self.known_permutations = []
        self.draw_alignment_by_index(0)

    def draw_alignment_by_index(self, index):
        if index >= len(self.known_permutations):
            try:
                self.known_permutations.append(next(self.per_iterator))
            except StopIteration:
                return False
            else:
                return self.draw_alignment_by_index(index)
        else:
            self.canvas.draw_perm(self.known_permutations[index])
            self.nav_label.config(
                text="{} / {}".format(
                    index, len(self.known_permutations)
                )
            )
            return True

    def place_widgets(self):
        self.canvas.grid(row=0, column=0, padx=1, pady=1)
        self.nav_bar.grid(row=1, column=0, sticky="we", padx=1, pady=1)
        self.back_button.pack(side="left", padx=10)
        self.forward_button.pack(side="right",padx=10)
        self.nav_label.pack()
        self.hud.grid(row=0, column=1, rowspan=2, sticky="nsew",
        	          padx=1, pady=1, ipadx=5)
        self.hud_main.pack(expand=True)
        self.info_button.pack(fill="x")
        self.colors_frame.pack(fill="x")
        self.color_cfg_frame.pack()
        self.color_add_button.grid(row=0, column=0, sticky="we")
        self.color_del_button.grid(row=0, column=1, sticky="we")
        self.calc_button.pack(fill="x")


def main():
    root = BeadAlignment(r=300)
    root.title("Boncuk Dizilişleri")
    root.mainloop()


if __name__ == "__main__":
    main()
