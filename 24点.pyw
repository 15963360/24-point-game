import tkinter as tk
from itertools import permutations
import tkinter.messagebox
import threading
from fractions import Fraction

def format_number(num):
    """将浮点数转换为分数或整数形式的字符串"""
    if num.is_integer():
        return f"{int(num)}"
    else:
        f = Fraction(num).limit_denominator()
        if f.denominator == 1:
            return f"{f.numerator}"
        else:
            return f"{f.numerator}/{f.denominator}"

def find_solutions(numbers, steps=None):
    if steps is None:
        steps = []
    solutions = []
    if len(numbers) == 1:
        if abs(numbers[0] - 24) < 1e-6:
            solutions.append(steps)
        return solutions

    # 剪枝条件：估算最大最小值范围
    remaining_steps = len(numbers) - 1
    max_num = max(numbers)
    min_num = min(numbers)
    max_possible = max_num * (10 ** remaining_steps)
    min_possible = min_num / (10 ** remaining_steps)
    if max_possible < 24 or min_possible > 24:
        return solutions

    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i == j:
                continue
            a = numbers[i]
            b = numbers[j]
            remaining = [num for idx, num in enumerate(numbers) if idx not in {i, j}]
            
            # 加法
            if i < j:
                new_num = a + b
                a_str = format_number(a)
                b_str = format_number(b)
                new_num_str = format_number(new_num)
                step_str = f"{a_str} + {b_str} = {new_num_str}"
                new_steps = steps + [step_str]
                solutions += find_solutions(remaining + [new_num], new_steps.copy())
            
            # 减法
            if a >= b:
                new_num = a - b
                a_str = format_number(a)
                b_str = format_number(b)
                new_num_str = format_number(new_num)
                step_str = f"{a_str} - {b_str} = {new_num_str}"
                new_steps = steps + [step_str]
                solutions += find_solutions(remaining + [new_num], new_steps.copy())
            
            # 乘法
            if i < j:
                new_num = a * b
                a_str = format_number(a)
                b_str = format_number(b)
                new_num_str = format_number(new_num)
                step_str = f"{a_str} × {b_str} = {new_num_str}"
                new_steps = steps + [step_str]
                solutions += find_solutions(remaining + [new_num], new_steps.copy())
            
            # 除法
            if b != 0:
                new_num = a / b
                if new_num >= 0:
                    a_str = format_number(a)
                    b_str = format_number(b)
                    new_num_str = format_number(new_num)
                    step_str = f"{a_str} ÷ {b_str} = {new_num_str}"
                    new_steps = steps + [step_str]
                    solutions += find_solutions(remaining + [new_num], new_steps.copy())
    return solutions

def solve_24(numbers):
    numbers = [float(num) for num in numbers]
    seen = set()
    solutions = []
    unique_perms = set(permutations(numbers))
    for perm in unique_perms:
        for solution in find_solutions(list(perm)):
            solution_str = " → ".join(solution)
            if solution_str not in seen:
                seen.add(solution_str)
                solutions.append(solution_str)
    return solutions if solutions else ["无解"]

# 以下部分保持不变，包括UI和事件处理
def calculate(entry, result_text):
    input_str = entry.get()
    numbers = input_str.replace(' ', '').split(',')
    try:
        numbers = list(map(float, numbers))
    except:
        tkinter.messagebox.showerror("错误", "输入无效，请输入数字，用逗号分隔。")
        return
    if len(numbers) != 5:
        tkinter.messagebox.showerror("错误", "请输入5个数字。")
        return

    calculate_button = root.grid_slaves(row=2, column=0)[0]
    calculate_button.config(state=tk.DISABLED)
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, "计算中，请稍候...")

    def run_solve():
        try:
            exprs = solve_24(numbers)
        except Exception as e:
            exprs = [f"错误: {str(e)}"]
        root.after(0, lambda: update_result(exprs, result_text, calculate_button))
    
    threading.Thread(target=run_solve, daemon=True).start()

def update_result(exprs, result_text, calculate_button):
    result_text.delete('1.0', tk.END)
    if exprs and exprs[0].startswith("错误"):
        result_text.insert(tk.END, exprs[0])
    else:
        result_text.insert(tk.END, "\n\n".join(exprs[:20]) if exprs != ["无解"] else "无解")
    calculate_button.config(state=tk.NORMAL)

root = tk.Tk()
root.title("24点游戏（五数字版）")
root.geometry("800x600")

font_settings = ("Microsoft YaHei", 12)

tk.Label(root, text="请输入5个数字，用逗号分隔：", font=font_settings).grid(row=0, column=0, columnspan=3, padx=10, pady=10)

entry = tk.Entry(root, font=font_settings, width=40)
entry.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

calculate_button = tk.Button(root, text="计算", command=lambda: calculate(entry, result_text), font=font_settings)
calculate_button.grid(row=2, column=0, padx=10, pady=10)

result_text = tk.Text(root, height=15, width=60, font=font_settings)
result_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

scrollbar = tk.Scrollbar(root, command=result_text.yview)
scrollbar.grid(row=3, column=2, sticky='ns')
result_text.config(yscrollcommand=scrollbar.set)

root.mainloop()