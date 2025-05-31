import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.colorchooser import askcolor
import numpy as np
from scipy.optimize import minimize

# 颜色混合函数
def mix_colors(palette, target):
    n = len(palette)
    x0 = np.ones(n) / n

    def loss(w):
        mixed = np.dot(w, palette)
        return np.sum((mixed - target) ** 2)

    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    bounds = [(0, 1) for _ in range(n)]

    result = minimize(loss, x0, bounds=bounds, constraints=constraints)
    return result.x

class ColorMixerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 颜色混合器")
        self.palette = []
        self.color_blocks = []
        self.target_color = None

        self.create_widgets()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        tk.Button(top_frame, text="添加颜料", command=self.add_palette_color).pack(side="left")
        tk.Button(top_frame, text="导入色板", command=self.import_palette).pack(side="left")
        tk.Button(top_frame, text="导出色板", command=self.export_palette).pack(side="left")

        # 色块区域（多行布局）
        self.color_display_frame = tk.Frame(self.root)
        self.color_display_frame.grid(row=1, column=0, columnspan=2, pady=5)

        self.row_frames = []  # 每行一个Frame
        self.colors_per_row = 10

        tk.Label(self.root, text="目标颜色:").grid(row=2, column=0, sticky="w")
        self.target_button = tk.Button(self.root, text="选择目标颜色", command=self.select_target_color)
        self.target_button.grid(row=2, column=1)

        self.result_button = tk.Button(self.root, text="计算混合比例", command=self.calculate)
        self.result_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.result_text = tk.Text(self.root, height=20, width=50)
        self.result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    def add_palette_color(self):
        color = askcolor(title="选择颜料颜色")[0]
        if color:
            rgb = [c / 255.0 for c in color]
            self.palette.append(rgb)
            self.display_palette_color(rgb, len(self.palette))

    def display_palette_color(self, rgb, index):
        color_hex = '#%02x%02x%02x' % tuple(int(c * 255) for c in rgb)

        row_index = (index - 1) // self.colors_per_row
        if row_index >= len(self.row_frames):
            row_frame = tk.Frame(self.color_display_frame)
            row_frame.pack()
            self.row_frames.append(row_frame)
        else:
            row_frame = self.row_frames[row_index]

        block = tk.Frame(row_frame)
        block.pack(side="left", padx=5, pady=2)

        color_frame = tk.Frame(block, width=30, height=30, bg=color_hex)
        color_frame.pack()
        label = tk.Label(block, text=f"颜色 {index}")
        label.pack()
        self.color_blocks.append(block)

    def select_target_color(self):
        color = askcolor(title="选择目标颜色")[0]
        if color:
            self.target_color = [c / 255.0 for c in color]
            color_hex = '#%02x%02x%02x' % tuple(int(c) for c in color)
            self.target_button.configure(bg=color_hex)

    def calculate(self):
        self.result_text.delete("1.0", tk.END)

        if not self.palette:
            messagebox.showerror("错误", "请先添加或导入颜料颜色。")
            return

        if not self.target_color:
            messagebox.showerror("错误", "请先选择目标颜色。")
            return

        weights = mix_colors(np.array(self.palette), np.array(self.target_color))

        self.result_text.insert(tk.END, "🔍 混合结果：\n")
        for i, w in enumerate(weights):
            if w > 1e-3:
                rgb = [int(c * 255) for c in self.palette[i]]
                self.result_text.insert(tk.END, f"颜色 {i+1}（RGB: {rgb}）: {w*100:.2f}%\n")

        mixed = np.dot(weights, self.palette)
        self.show_result_colors(self.target_color, mixed)

    def show_result_colors(self, target_rgb, mixed_rgb):
        win = tk.Toplevel(self.root)
        win.title("颜色对比")

        tk.Label(win, text="目标颜色").grid(row=0, column=0)
        tk.Label(win, text="混合结果").grid(row=0, column=1)

        t_color_hex = '#%02x%02x%02x' % tuple(int(c * 255) for c in target_rgb)
        m_color_hex = '#%02x%02x%02x' % tuple(int(c * 255) for c in mixed_rgb)

        tk.Frame(win, bg=t_color_hex, width=100, height=50).grid(row=1, column=0, padx=10, pady=5)
        tk.Frame(win, bg=m_color_hex, width=100, height=50).grid(row=1, column=1, padx=10, pady=5)

        tk.Label(win, text=f"RGB: {tuple(int(c * 255) for c in target_rgb)}").grid(row=2, column=0)
        tk.Label(win, text=f"RGB: {tuple(int(c * 255) for c in mixed_rgb)}").grid(row=2, column=1)

    def import_palette(self):
        path = filedialog.askopenfilename(title="选择色板文件", filetypes=[("文本文件", "*.txt")])
        if not path:
            return
        try:
            with open(path, "r") as f:
                lines = f.readlines()
                self.palette.clear()
                for block in self.color_blocks:
                    block.destroy()
                self.color_blocks.clear()
                for frame in self.row_frames:
                    frame.destroy()
                self.row_frames.clear()

                for i, line in enumerate(lines):
                    r, g, b = map(int, line.strip().split(","))
                    rgb = [r / 255.0, g / 255.0, b / 255.0]
                    self.palette.append(rgb)
                    self.display_palette_color(rgb, i + 1)

                messagebox.showinfo("成功", f"成功导入 {len(self.palette)} 种颜色。")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{e}")

    def export_palette(self):
        if not self.palette:
            messagebox.showerror("错误", "当前没有颜色可导出。")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt")])
        if not path:
            return
        try:
            with open(path, "w") as f:
                for rgb in self.palette:
                    line = ",".join(str(int(c * 255)) for c in rgb)
                    f.write(line + "\n")
            messagebox.showinfo("成功", "色板已成功导出。")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{e}")

def main():
    root = tk.Tk()
    app = ColorMixerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
