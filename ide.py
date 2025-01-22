import tkinter as tk
from tkinter import filedialog, messagebox
import assembler as AS
import xmlgenerator as XMLG

def apply_syntax_highlighting():
    code_editor.tag_remove("instruction", "1.0", tk.END)
    code_editor.tag_remove("register", "1.0", tk.END)
    code_editor.tag_remove("comment", "1.0", tk.END)
    code_editor.tag_remove("alt_comment", "1.0", tk.END)

    code = code_editor.get("1.0", tk.END)
    lines = code.split("\n")

    for line_num, line in enumerate(lines, start=1):
        for instr in ["ADD", "SUB", "XOR", "AND", "OR", "NAD", "NOR", "BSL", "BSR", "SET", "MOV", "JMP", "BRH", "HLT"]:
            start_idx = f"{line_num}.0"
            while True:
                start_idx = code_editor.search(instr, start_idx, stopindex=f"{line_num}.end", nocase=False)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(instr)}c"
                code_editor.tag_add("instruction", start_idx, end_idx)
                start_idx = end_idx

        for reg in ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"]:
            start_idx = f"{line_num}.0"
            while True:
                start_idx = code_editor.search(reg, start_idx, stopindex=f"{line_num}.end", nocase=False)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(reg)}c"
                code_editor.tag_add("register", start_idx, end_idx)
                start_idx = end_idx

        if ";" in line:
            comment_start = line.index(";")
            start_idx = f"{line_num}.{comment_start}"
            end_idx = f"{line_num}.end"
            code_editor.tag_add("comment", start_idx, end_idx)

        if line.startswith("#"):
            code_editor.tag_add("alt_comment", f"{line_num}.0", f"{line_num}.end")

def open_file():
    filepath = filedialog.askopenfilename(filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")])
    if filepath:
        with open(filepath, "r") as file:
            code_editor.delete("1.0", tk.END)
            code_editor.insert("1.0", file.read())
        root.title(f"Custom CPU IDE - {filepath}")
        apply_syntax_highlighting()

def save_file():
    if current_filepath:
        with open(current_filepath, "w") as file:
            file.write(code_editor.get("1.0", tk.END))
        root.title(f"Custom CPU IDE - {current_filepath}")
    else:
        save_file_as()

def save_file_as():
    filepath = filedialog.asksaveasfilename(defaultextension=".asm", filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")])
    if filepath:
        with open(filepath, "w") as file:
            file.write(code_editor.get("1.0", tk.END))
        root.title(f"Custom CPU IDE - {filepath}")
        global current_filepath
        current_filepath = filepath

def new_file():
    response = messagebox.askyesno("New File", "Do you want to save changes to the current file?")
    if response:
        save_file()
    code_editor.delete("1.0", tk.END)
    root.title("Custom CPU IDE")

def generate_output():
    try:
        assembly_code = code_editor.get("1.0", tk.END).strip()
        if not assembly_code:
            raise ValueError("The code editor is empty.")

        binary_program = AS.assemble_program(assembly_code.split("\n"))
        xml_output = XMLG.generate_circuit_xml(binary_program)

        binary_output_text.delete("1.0", tk.END)
        binary_output_text.insert("1.0", "\n".join(binary_program))

        xml_output_text.delete("1.0", tk.END)
        xml_output_text.insert("1.0", xml_output)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate output: {str(e)}")

def export_to_format(format_type):
    file_type_map = {
        "gcg": ("GCG Files", "*.gcg"),
        "bin": ("Binary Files", "*.bin"),
        "xml": ("XML Files", "*.xml"),
        "ic": ("IC Files", "*.ic"),
    }
    if format_type not in file_type_map:
        messagebox.showerror("Export Error", "Unsupported export format.")
        return

    file_type_label, file_extension = file_type_map[format_type]
    filepath = filedialog.asksaveasfilename(defaultextension=file_extension,
                                            filetypes=[(file_type_label, file_extension)])
    if not filepath:
        return
    assembly_code = code_editor.get("1.0", tk.END).strip()

    try:
        binary_program = AS.assemble_program(assembly_code.split("\n"))
        if format_type == "bin":
            with open(filepath, "w") as file:
                file.write("\n".join(binary_program))
        elif format_type == "xml":
            xml_output = XMLG.generate_circuit_xml(binary_program)
            with open(filepath, "w") as file:
                file.write(xml_output)
        elif format_type == "ic":
            xml_output = XMLG.generate_circuit_xml(binary_program)
            ic_output = xml_output.replace(".xml", ".ic")
            with open(filepath, "w") as file:
                file.write(ic_output)
        elif format_type == "gcg":
            XMLG.generate_gcg("template.xml", binary_program, filepath)

        messagebox.showinfo("Export Successful", f"File exported as {filepath}")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export {format_type.upper()} file: {str(e)}")


def update_line_numbers(event=None):
    total_lines = int(code_editor.index("end-1c").split('.')[0])
    cursor_line = int(code_editor.index(tk.INSERT).split('.')[0])
    line_number = 0
    for i in range(1, cursor_line + 1):
        line_content = code_editor.get(f"{i}.0", f"{i}.end").strip()
        if not line_content.startswith(";") and line_content != "":
            line_number += 1
    cursor_line = line_number

    lines = []
    code_line_count = 0
    display_line_count = 0
    
    for line_num in range(1, total_lines + 1):
        line_text = code_editor.get(f"{line_num}.0", f"{line_num}.end").strip()

        if line_text.startswith(";"):
            lines.append(f"    | {line_num:3}")
            continue
        
        code_line_count += 1
        if code_line_count == cursor_line:
            display_line_count = 0
        else:
            display_line_count = code_line_count - cursor_line
        lines.append(f"{display_line_count:3} | {line_num:3}")

    line_number_display.config(state="normal")
    line_number_display.delete(1.0, tk.END)
    for line in lines:
        line_number_display.insert(tk.END, line + "\n")
    line_number_display.config(state="disabled")

def apply_dark_theme():
    root.config(bg="#2e2e2e")
    menu_bar.config(bg="#1c1c1c", fg="#ffffff")
    file_menu.config(bg="#2e2e2e", fg="#ffffff")
    theme_menu.config(bg="#2e2e2e", fg="#ffffff")
    code_editor.config(bg="#1c1c1c", fg="#ffffff", insertbackground="white")
    line_number_display.config(bg="#2e2e2e", fg="#ffffff")
    line_number_frame.config(bg="#2e2e2e")
    button_frame.config(bg="#2e2e2e")
    generate_button.config(bg="#3c3f41", fg="#ffffff")
    binary_label.config(bg="#2e2e2e", fg="#ffffff")
    xml_label.config(bg="#2e2e2e", fg="#ffffff")
    binary_output_text.config(bg="#1c1c1c", fg="#ffffff")
    xml_output_text.config(bg="#1c1c1c", fg="#ffffff")
    code_editor.tag_configure("instruction", foreground="#d5a6bd", font=("Courier", 12, "bold"))
    code_editor.tag_configure("register", foreground="orange")
    code_editor.tag_configure("comment", foreground="yellow", font=("Courier", 12, "italic"))
    code_editor.tag_configure("alt_comment", foreground="lightgreen", font=("Courier", 12, "italic"))

def apply_light_theme():
    root.config(bg="#ffffff")
    menu_bar.config(bg="#f0f0f0", fg="#000000")
    file_menu.config(bg="#ffffff", fg="#000000")
    theme_menu.config(bg="#ffffff", fg="#000000")
    code_editor.config(bg="#ffffff", fg="#000000", insertbackground="black")
    line_number_display.config(bg="#f0f0f0", fg="#000000")
    line_number_frame.config(bg="#f0f0f0")
    button_frame.config(bg="#ffffff")
    generate_button.config(bg="#e0e0e0", fg="#000000")
    binary_label.config(bg="#ffffff", fg="#000000")
    xml_label.config(bg="#ffffff", fg="#000000")
    binary_output_text.config(bg="#ffffff", fg="#000000")
    xml_output_text.config(bg="#ffffff", fg="#000000")
    code_editor.tag_configure("instruction", foreground="blue", font=("Courier", 12, "bold"))
    code_editor.tag_configure("register", foreground="darkgreen")
    code_editor.tag_configure("comment", foreground="gray", font=("Courier", 12, "italic"))
    code_editor.tag_configure("alt_comment", foreground="green", font=("Courier", 12, "italic"))

def set_theme_light():
    apply_light_theme()

def set_theme_dark():
    apply_dark_theme()

root = tk.Tk()
root.title("Custom CPU IDE")
root.geometry("800x600")

current_filepath = None

menu_bar = tk.Menu(root, bg="#1c1c1c", fg="#ffffff")
# Updated File Menu
file_menu = tk.Menu(menu_bar, tearoff=0, bg="#2e2e2e", fg="#ffffff")
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_file_as)
file_menu.add_separator()

# Add Export Submenu
export_menu = tk.Menu(file_menu, tearoff=0, bg="#2e2e2e", fg="#ffffff")
export_menu.add_command(label="Export as GCG", command=lambda: export_to_format("gcg"))
export_menu.add_command(label="Export as BIN", command=lambda: export_to_format("bin"))
export_menu.add_command(label="Export as XML", command=lambda: export_to_format("xml"))
export_menu.add_command(label="Export as IC", command=lambda: export_to_format("ic"))
file_menu.add_cascade(label="Export", menu=export_menu)

file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

theme_menu = tk.Menu(menu_bar, tearoff=0, bg="#2e2e2e", fg="#ffffff")
theme_menu.add_command(label="Light Mode", command=set_theme_light)
theme_menu.add_command(label="Dark Mode", command=set_theme_dark)
menu_bar.add_cascade(label="Theme", menu=theme_menu)

root.config(menu=menu_bar)

code_editor_frame = tk.Frame(root, bg="#2e2e2e")
code_editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

line_number_frame = tk.Frame(code_editor_frame, width=50, bg="#2e2e2e")
line_number_frame.pack(side=tk.LEFT, fill=tk.Y)
line_number_display = tk.Text(line_number_frame, width=4, wrap="none", font=("Courier", 12), state="disabled", bg="#2e2e2e", fg="#ffffff")
line_number_display.pack(side=tk.LEFT, fill=tk.Y)

code_editor = tk.Text(code_editor_frame, wrap="none", undo=True, font=("Courier", 12), bg="#1c1c1c", fg="#ffffff", insertbackground="white")
code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

code_editor.bind("<KeyRelease>", lambda event: [apply_syntax_highlighting(), update_line_numbers(event)])
code_editor.bind("<ButtonRelease-1>", update_line_numbers)

button_frame = tk.Frame(root, bg="#2e2e2e")
button_frame.pack(fill=tk.X)

generate_button = tk.Button(button_frame, text="Generate", command=generate_output, bg="#3c3f41", fg="#ffffff")
generate_button.pack(side=tk.LEFT, padx=5, pady=5)

binary_label = tk.Label(root, text="Binary Output:", bg="#2e2e2e", fg="#ffffff")
binary_label.pack()

binary_output_text = tk.Text(root, wrap="none", height=10, font=("Courier", 12), bg="#1c1c1c", fg="#ffffff")
binary_output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

xml_label = tk.Label(root, text="XML Output:", bg="#2e2e2e", fg="#ffffff")
xml_label.pack()

xml_output_text = tk.Text(root, wrap="none", height=10, font=("Courier", 12), bg="#1c1c1c", fg="#ffffff")
xml_output_text.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

apply_dark_theme()  # Set initial theme to dark

root.mainloop()