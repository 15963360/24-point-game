import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from itertools import permutations, combinations
import concurrent.futures
from fractions import Fraction
from functools import lru_cache

FONT_SETTINGS = ("Microsoft YaHei", 12)
TARGET = 24
EPSILON = 1e-6

def format_number(num):
    if abs(num - round(num)) < EPSILON:
        return f"{int(round(num))}"
    f = Fraction(num).limit_denominator()
    return f"{f.numerator}/{f.denominator}" if f.denominator != 1 else f"{f.numerator}"

@lru_cache(maxsize=None)
def find_solutions(numbers):
    if len(numbers) == 1:
        return [([format_number(numbers[0])], numbers[0])] if abs(numbers[0] - TARGET) < EPSILON else []

    solutions = []
    for a, b in combinations(numbers, 2):
        remaining = tuple(num for num in numbers if num not in (a, b))
        for op, func in [('+', lambda x, y: x + y), ('-', lambda x, y: x - y),
                         ('×', lambda x, y: x * y), ('÷', lambda x, y: x / y if y != 0 else float('inf'))]:
            new_num = func(a, b)
            for sub_solution, sub_result in find_solutions(remaining + (new_num,)):
                solutions.append((
                    [f"{format_number(a)} {op} {format_number(b)} = {format_number(new_num)}"] + sub_solution,
                    sub_result
                ))
    return solutions

def solve_24(numbers):
    numbers = tuple(map(float, numbers))
    seen = set()
    solutions = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_perm = {executor.submit(find_solutions, perm): perm for perm in set(permutations(numbers))}
        for future in concurrent.futures.as_completed(future_to_perm):
            for solution, result in future.result():
                solution_str = " → ".join(solution)
                if solution_str not in seen:
                    seen.add(solution_str)
                    solutions.append(solution_str)
    return solutions if solutions else ["无解"]

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("24点游戏（五数字版）")
        self.master.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.master, text="请输入5个数字，用逗号分隔：", font=FONT_SETTINGS).grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.entry = ttk.Entry(self.master, font=FONT_SETTINGS, width=40)
        self.entry.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.calculate_button = ttk.Button(self.master, text="计算", command=self.calculate)
        self.calculate_button.grid(row=2, column=0, padx=10, pady=10)

        self.result_text = tk.Text(self.master, height=15, width=60, font=FONT_SETTINGS)
        self.result_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(self.master, command=self.result_text.yview)
        scrollbar.grid(row=3, column=2, sticky='ns')
        self.result_text.config(yscrollcommand=scrollbar.set)

    def calculate(self):
        input_str = self.entry.get()
        numbers = input_str.replace(' ', '').split(',')
        try:
            numbers = list(map(float, numbers))
        except ValueError:
            tkinter.messagebox.showerror("错误", "输入无效，请输入数字，用逗号分隔。")
            return
        if len(numbers) != 5:
            tkinter.messagebox.showerror("错误", "请输入5个数字。")
            return

        self.calculate_button.config(state=tk.DISABLED)
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, "计算中，请稍候...")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(solve_24, numbers)
            self.master.after(100, self.check_result, future)

    def check_result(self, future):
        if future.done():
            exprs = future.result()
            self.update_result(exprs)
        else:
            self.master.after(100, self.check_result, future)

    def update_result(self, exprs):
        self.result_text.delete('1.0', tk.END)
        if exprs and exprs[0].startswith("错误"):
            self.result_text.insert(tk.END, exprs[0])
        else:
            self.result_text.insert(tk.END, "\n\n".join(exprs[:20]) if exprs != ["无解"] else "无解")
        self.calculate_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
