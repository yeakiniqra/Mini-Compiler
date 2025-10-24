import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from lexer import TokenScanner
from parser import SyntaxProcessor
from code_generator import AssemblyTranslator
import os
import re


class SyntaxHighlighter:
    """Syntax highlighting for code editor"""
    def __init__(self, text_widget):
        self.text = text_widget
        
        # Define color scheme (VS Code Dark+)
        self.tags = {
            'keyword': {'foreground': '#C586C0'},
            'type': {'foreground': '#4EC9B0'},
            'number': {'foreground': '#B5CEA8'},
            'string': {'foreground': '#CE9178'},
            'comment': {'foreground': '#6A9955'},
            'operator': {'foreground': '#D4D4D4'},
            'function': {'foreground': '#DCDCAA'},
            'variable': {'foreground': '#9CDCFE'},
        }
        
        for tag, style in self.tags.items():
            self.text.tag_config(tag, **style)
    
    def highlight(self, event=None):
        """Apply syntax highlighting"""
        self.text.mark_set("range_start", "1.0")
        content = self.text.get("1.0", "end-1c")
        
        # Remove all tags
        for tag in self.tags.keys():
            self.text.tag_remove(tag, "1.0", "end")
        
        # Keywords
        keywords = r'\b(int|if|else|while|print|return|void|char|float|double)\b'
        for match in re.finditer(keywords, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add('keyword', start, end)
        
        # Numbers
        numbers = r'\b\d+\b'
        for match in re.finditer(numbers, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add('number', start, end)
        
        # Single line comments
        comments = r'//.*?$'
        for match in re.finditer(comments, content, re.MULTILINE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add('comment', start, end)
        
        # Multi-line comments
        ml_comments = r'/\*.*?\*/'
        for match in re.finditer(ml_comments, content, re.DOTALL):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add('comment', start, end)
        
        # Operators
        operators = r'[+\-*/%=<>!&|]+'
        for match in re.finditer(operators, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add('operator', start, end)
        
        # Function calls
        functions = r'\b(\w+)\s*\('
        for match in re.finditer(functions, content):
            start = f"1.0+{match.start(1)}c"
            end = f"1.0+{match.end(1)}c"
            self.text.tag_add('function', start, end)


class OutputHighlighter:
    """Syntax highlighting for output tabs"""
    def __init__(self, text_widget, style='default'):
        self.text = text_widget
        self.style = style
        self.setup_tags()
    
    def setup_tags(self):
        """Setup color tags for output"""
        # Token view colors
        self.text.tag_config('header', foreground='#569CD6', font=('Consolas', 9, 'bold'))
        self.text.tag_config('separator', foreground='#404040')
        self.text.tag_config('keyword_token', foreground='#C586C0')
        self.text.tag_config('number_token', foreground='#B5CEA8')
        self.text.tag_config('identifier_token', foreground='#9CDCFE')
        self.text.tag_config('operator_token', foreground='#D4D4D4')
        self.text.tag_config('line_num', foreground='#858585')
        
        # Symbol table colors
        self.text.tag_config('type_name', foreground='#4EC9B0')
        self.text.tag_config('value', foreground='#B5CEA8')
        self.text.tag_config('scope', foreground='#CE9178')
        
        # IR Code colors
        self.text.tag_config('ir_label', foreground='#DCDCAA', font=('Consolas', 9, 'bold'))
        self.text.tag_config('ir_op', foreground='#C586C0')
        self.text.tag_config('ir_var', foreground='#9CDCFE')
        self.text.tag_config('ir_num', foreground='#B5CEA8')
        self.text.tag_config('ir_index', foreground='#858585')
        
        # Assembly colors
        self.text.tag_config('asm_instruction', foreground='#569CD6', font=('Consolas', 9, 'bold'))
        self.text.tag_config('asm_register', foreground='#CE9178')
        self.text.tag_config('asm_label', foreground='#DCDCAA')
        self.text.tag_config('asm_comment', foreground='#6A9955')
        
        # Error colors
        self.text.tag_config('error_icon', foreground='#F14C4C', font=('Consolas', 9, 'bold'))
        self.text.tag_config('success_icon', foreground='#89D185', font=('Consolas', 9, 'bold'))
        self.text.tag_config('error_text', foreground='#F48771')


class VSCodeButton(tk.Canvas):
    """VS Code style button with smooth hover animation"""
    def __init__(self, parent, text, command, icon="", bg_color="#0E639C", **kwargs):
        super().__init__(parent, height=28, highlightthickness=0, bg=bg_color, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.text = text
        self.icon = icon
        self.hover_alpha = 0
        self.animation_id = None
        
        width = kwargs.get('width', 100)
        self.rect = self.create_rectangle(0, 0, width, 28, fill=bg_color, outline="", width=0)
        
        display_text = f"{icon}  {text}" if icon else text
        self.text_item = self.create_text(width//2, 14, text=display_text, 
                                         fill="white", font=('Segoe UI', 9))
        
        self.bind("<Button-1>", lambda e: command())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_enter(self, e):
        self.animate_hover(True)
        
    def on_leave(self, e):
        self.animate_hover(False)
        
    def animate_hover(self, entering):
        if self.animation_id:
            self.after_cancel(self.animation_id)
        
        target = 30 if entering else 0
        if self.hover_alpha < target:
            self.hover_alpha = min(self.hover_alpha + 5, target)
            self.update_color()
            self.animation_id = self.after(16, lambda: self.animate_hover(entering))
        elif self.hover_alpha > target:
            self.hover_alpha = max(self.hover_alpha - 5, target)
            self.update_color()
            self.animation_id = self.after(16, lambda: self.animate_hover(entering))
    
    def update_color(self):
        base = self.bg_color.lstrip('#')
        r, g, b = int(base[0:2], 16), int(base[2:4], 16), int(base[4:6], 16)
        factor = 1 + (self.hover_alpha / 100)
        r, g, b = min(int(r * factor), 255), min(int(g * factor), 255), min(int(b * factor), 255)
        new_color = f'#{r:02x}{g:02x}{b:02x}'
        self.itemconfig(self.rect, fill=new_color)


class CompilerInterface:
    """VS Code styled compiler interface"""
    
    def __init__(self, window):
        self.window = window
        self.window.title("Mini Compiler by Yeakin Iqra")
        self.window.geometry("1400x800")
        
        self.current_file = None
        self.file_modified = False
        
        self.colors = {
            'bg': '#1E1E1E',
            'sidebar': '#252526',
            'editor': '#1E1E1E',
            'panel': '#252526',
            'border': '#2D2D30',
            'accent': '#0E639C',
            'text': '#CCCCCC',
            'text_dim': '#858585',
            'selection': '#264F78',
            'active_tab': '#1E1E1E',
            'inactive_tab': '#2D2D30',
            'statusbar': '#007ACC'
        }
        
        self.window.configure(bg=self.colors['bg'])
        
        self.scanner = TokenScanner()
        self.scanner.initialize()
        self.processor = SyntaxProcessor()
        self.processor.initialize()
        self.translator = AssemblyTranslator()
        
        self.build_interface()
        
    def build_interface(self):
        self.create_activity_bar()
        self.create_editor_area()
        self.create_status_bar()
        
    def create_activity_bar(self):
        activity_bar = tk.Frame(self.window, bg=self.colors['sidebar'], width=48)
        activity_bar.pack(side=tk.LEFT, fill=tk.Y)
        activity_bar.pack_propagate(False)
        
        logo = tk.Label(activity_bar, text="⚡", font=('Segoe UI', 20), 
                       bg=self.colors['sidebar'], fg=self.colors['accent'])
        logo.pack(pady=(10, 20))
        
        icons = [
            ("📄", "Explorer", self.open_file),
            ("💾", "Save", self.save_file),
            ("⚙️", "Settings", None)
        ]
        
        for icon, tooltip, cmd in icons:
            btn = tk.Label(activity_bar, text=icon, font=('Segoe UI', 16),
                          bg=self.colors['sidebar'], fg=self.colors['text_dim'],
                          cursor="hand2")
            btn.pack(pady=10)
            if cmd:
                btn.bind("<Button-1>", lambda e, command=cmd: command())
            
    def create_editor_area(self):
        main_area = tk.Frame(self.window, bg=self.colors['bg'])
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_toolbar(main_area)
        
        content = tk.PanedWindow(main_area, orient=tk.HORIZONTAL, 
                                bg=self.colors['bg'], sashwidth=4,
                                sashrelief=tk.FLAT, bd=0)
        content.pack(fill=tk.BOTH, expand=True)
        
        editor_frame = tk.Frame(content, bg=self.colors['editor'])
        content.add(editor_frame, width=700)
        self.create_editor(editor_frame)
        
        output_frame = tk.Frame(content, bg=self.colors['panel'])
        content.add(output_frame, width=700)
        self.create_output_tabs(output_frame)
        
    def create_toolbar(self, parent):
        toolbar = tk.Frame(parent, bg=self.colors['sidebar'], height=35)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        left_frame = tk.Frame(toolbar, bg=self.colors['sidebar'])
        left_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(left_frame, text="📁", font=('Segoe UI', 10),
                bg=self.colors['sidebar'], fg=self.colors['text_dim']).pack(side=tk.LEFT, padx=5)
        
        self.file_label = tk.Label(left_frame, text="Untitled", font=('Segoe UI', 9),
                                   bg=self.colors['sidebar'], fg=self.colors['text'])
        self.file_label.pack(side=tk.LEFT)
        
        right_frame = tk.Frame(toolbar, bg=self.colors['sidebar'])
        right_frame.pack(side=tk.RIGHT, padx=10)
        
        VSCodeButton(right_frame, "Open", self.open_file, 
                    icon="📂", bg_color="#3C3C3C", width=80).pack(side=tk.LEFT, padx=5)
        
        VSCodeButton(right_frame, "Save", self.save_file,
                    icon="💾", bg_color="#3C3C3C", width=80).pack(side=tk.LEFT, padx=5)
        
        VSCodeButton(right_frame, "Run", self.run_compilation, 
                    icon="▶", bg_color="#0E639C", width=80).pack(side=tk.LEFT, padx=5)
        
        VSCodeButton(right_frame, "Clear", self.reset_all,
                    icon="↻", bg_color="#3C3C3C", width=80).pack(side=tk.LEFT, padx=5)
        
    def create_editor(self, parent):
        tab_bar = tk.Frame(parent, bg=self.colors['sidebar'], height=35)
        tab_bar.pack(fill=tk.X)
        tab_bar.pack_propagate(False)
        
        tab = tk.Frame(tab_bar, bg=self.colors['active_tab'])
        tab.pack(side=tk.LEFT)
        
        tk.Label(tab, text="📄", font=('Segoe UI', 9),
                bg=self.colors['active_tab'], fg=self.colors['text_dim']).pack(side=tk.LEFT, padx=(10, 5))
        
        self.tab_label = tk.Label(tab, text="Untitled", font=('Segoe UI', 9),
                                 bg=self.colors['active_tab'], fg=self.colors['text'])
        self.tab_label.pack(side=tk.LEFT, padx=(0, 10))
        
        editor_container = tk.Frame(parent, bg=self.colors['editor'])
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        self.line_numbers = tk.Text(editor_container, width=4, 
                                    bg=self.colors['editor'], fg=self.colors['text_dim'],
                                    font=('Consolas', 10), state='disabled',
                                    relief='flat', bd=0, padx=10, pady=10)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        sep = tk.Frame(editor_container, bg=self.colors['border'], width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y)
        
        self.code_input = scrolledtext.ScrolledText(editor_container,
                                                    font=('Consolas', 10),
                                                    bg=self.colors['editor'],
                                                    fg=self.colors['text'],
                                                    insertbackground='white',
                                                    selectbackground=self.colors['selection'],
                                                    relief='flat', bd=0,
                                                    padx=15, pady=10,
                                                    undo=True)
        self.code_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Initialize syntax highlighter
        self.highlighter = SyntaxHighlighter(self.code_input)
        
        self.code_input.bind('<KeyRelease>', self.on_key_release)
        self.code_input.bind('<<Modified>>', self.on_text_modified)
        self.code_input.bind('<Control-s>', lambda e: self.save_file())
        self.code_input.bind('<Control-o>', lambda e: self.open_file())
        
        example = """int x;
int y;
x = 10;
y = 20;

/* Calculate sum */
int sum;
sum = x + y;
print(sum);

// Conditional statement
if (x < y) {
    int diff;
    diff = y - x;
    print(diff);
}

// Loop example
int counter;
counter = 0;
while (counter < 5) {
    int temp;
    temp = counter * 2;
    print(temp);
    counter = counter + 1;
}"""
        self.code_input.insert('1.0', example)
        self.highlighter.highlight()
        self.update_line_numbers()
        self.file_modified = False
    
    def on_key_release(self, event=None):
        """Handle key release for highlighting and line numbers"""
        self.update_line_numbers()
        self.highlighter.highlight()
        
    def create_output_tabs(self, parent):
        tab_bar = tk.Frame(parent, bg=self.colors['sidebar'], height=35)
        tab_bar.pack(fill=tk.X)
        tab_bar.pack_propagate(False)
        
        tk.Label(tab_bar, text="OUTPUT", font=('Segoe UI', 9, 'bold'),
                bg=self.colors['sidebar'], fg=self.colors['text_dim']).pack(side=tk.LEFT, padx=15, pady=8)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('VSCode.TNotebook', background=self.colors['panel'], 
                       borderwidth=0, tabmargins=[0, 0, 0, 0])
        style.configure('VSCode.TNotebook.Tab',
                       background=self.colors['inactive_tab'],
                       foreground=self.colors['text'],
                       padding=[12, 6], borderwidth=0,
                       font=('Segoe UI', 9))
        style.map('VSCode.TNotebook.Tab',
                 background=[('selected', self.colors['active_tab'])],
                 foreground=[('selected', self.colors['text'])])
        
        self.output_tabs = ttk.Notebook(parent, style='VSCode.TNotebook')
        self.output_tabs.pack(fill=tk.BOTH, expand=True)
        
        tabs = [
            ("Tokens", "tok_view"),
            ("Symbols", "var_view"),
            ("IR Code", "ir_view"),
            ("Assembly", "asm_view"),
            ("Problems", "err_view")
        ]
        
        for label, attr in tabs:
            frame = tk.Frame(self.output_tabs, bg=self.colors['editor'])
            self.output_tabs.add(frame, text=label)
            
            view = scrolledtext.ScrolledText(frame,
                                            font=('Consolas', 9),
                                            bg=self.colors['editor'],
                                            fg=self.colors['text'],
                                            insertbackground='white',
                                            selectbackground=self.colors['selection'],
                                            relief='flat', bd=0,
                                            padx=15, pady=10)
            view.pack(fill=tk.BOTH, expand=True)
            setattr(self, attr, view)
            
            # Setup highlighter for each view
            setattr(self, f"{attr}_highlighter", OutputHighlighter(view))
            
    def create_status_bar(self):
        status = tk.Frame(self.window, bg=self.colors['statusbar'], height=22)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        status.pack_propagate(False)
        
        left_frame = tk.Frame(status, bg=self.colors['statusbar'])
        left_frame.pack(side=tk.LEFT)
        
        tk.Label(left_frame, text="⚡", font=('Segoe UI', 9),
                bg=self.colors['statusbar'], fg='white').pack(side=tk.LEFT, padx=(10, 5))
        
        self.status_label = tk.Label(left_frame, text="Ready",
                                     font=('Segoe UI', 9),
                                     bg=self.colors['statusbar'],
                                     fg='white')
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        right_frame = tk.Frame(status, bg=self.colors['statusbar'])
        right_frame.pack(side=tk.RIGHT)
        
        tk.Label(right_frame, text="Iqra", font=('Segoe UI', 9),
                bg=self.colors['statusbar'], fg='white').pack(side=tk.LEFT, padx=10)
        
    def update_line_numbers(self, event=None):
        line_count = self.code_input.get('1.0', 'end-1c').count('\n') + 1
        line_numbers_string = '\n'.join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
        
    def on_text_modified(self, event=None):
        if self.code_input.edit_modified():
            self.file_modified = True
            self.update_title()
            self.code_input.edit_modified(False)
    
    def update_title(self):
        filename = os.path.basename(self.current_file) if self.current_file else "Untitled"
        modified_indicator = "●" if self.file_modified else ""
        
        self.file_label.config(text=f"{filename} {modified_indicator}".strip())
        self.tab_label.config(text=f"{filename} {modified_indicator}".strip())
        self.window.title(f"Mini Compiler by Yeakin Iqra - {filename} {modified_indicator}".strip())
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open Source File",
            filetypes=[("C Source Files", "*.c"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir=os.getcwd()
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.code_input.delete('1.0', tk.END)
                self.code_input.insert('1.0', content)
                self.highlighter.highlight()
                self.current_file = file_path
                self.file_modified = False
                self.update_title()
                self.update_line_numbers()
                self.status_label.config(text=f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
    
    def save_file(self):
        if not self.current_file:
            self.save_file_as()
        else:
            try:
                content = self.code_input.get('1.0', 'end-1c')
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                self.file_modified = False
                self.update_title()
                self.status_label.config(text=f"Saved: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
    
    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Source File As",
            defaultextension=".c",
            filetypes=[("C Source Files", "*.c"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir=os.getcwd()
        )
        
        if file_path:
            try:
                content = self.code_input.get('1.0', 'end-1c')
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                self.current_file = file_path
                self.file_modified = False
                self.update_title()
                self.status_label.config(text=f"Saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
        
    def run_compilation(self):
        self.status_label.config(text="⏳ Compiling...")
        self.window.update()
        
        src = self.code_input.get('1.0', tk.END)
        
        for view in ['tok_view', 'var_view', 'ir_view', 'asm_view', 'err_view']:
            getattr(self, view).delete('1.0', tk.END)
        
        self.processor.registry.clear()
        
        # Tokens with colors
        tokens, lex_errs = self.scanner.scan(src)
        
        self.tok_view.insert('1.0', f"{'TYPE':<18} {'VALUE':<18} {'LINE':<8}\n", 'header')
        self.tok_view.insert('end', "─" * 50 + "\n", 'separator')
        
        for tok in tokens:
            kind = tok['kind']
            val = str(tok['val'])
            ln = str(tok['ln'])
            
            # Apply colors based on token type
            if kind in ['KEYWORD', 'IF', 'ELSE', 'WHILE', 'INT']:
                self.tok_view.insert('end', f"{kind:<18} ", 'keyword_token')
            elif kind in ['NUMBER', 'NUM']:
                self.tok_view.insert('end', f"{kind:<18} ", 'number_token')
            elif kind == 'ID':
                self.tok_view.insert('end', f"{kind:<18} ", 'identifier_token')
            elif kind in ['OP', 'ASSIGN', 'RELOP']:
                self.tok_view.insert('end', f"{kind:<18} ", 'operator_token')
            else:
                self.tok_view.insert('end', f"{kind:<18} ")
            
            self.tok_view.insert('end', f"{val:<18} ")
            self.tok_view.insert('end', f"{ln:<8}\n", 'line_num')
        
        # Symbols with colors
        self.processor.process(src)
        
        self.var_view.insert('1.0', f"{'IDENTIFIER':<18} {'TYPE':<10} {'VALUE':<10} {'SCOPE':<18} {'LEVEL':<8}\n", 'header')
        self.var_view.insert('end', "─" * 70 + "\n", 'separator')
        
        for entry in self.processor.registry.all_entries():
            val_str = str(entry['val']) if entry['val'] is not None else 'None'
            
            self.var_view.insert('end', f"{entry['id']:<18} ", 'identifier_token')
            self.var_view.insert('end', f"{entry['dtype']:<10} ", 'type_name')
            self.var_view.insert('end', f"{val_str:<10} ", 'value')
            self.var_view.insert('end', f"{entry['scope']:<18} ", 'scope')
            self.var_view.insert('end', f"{entry['scope_level']:<8}\n", 'line_num')
        
        # IR Code with colors
        for idx, instr in enumerate(self.processor.ir_instructions):
            op = instr['op']
            s1 = instr['src1']
            s2 = instr['src2']
            d = instr['dst']
            
            self.ir_view.insert('end', f"{idx:3}: ", 'ir_index')
            
            if op == 'assign':
                self.ir_view.insert('end', f" {d} ", 'ir_var')
                self.ir_view.insert('end', "= ", 'ir_op')
                if str(s1).isdigit():
                    self.ir_view.insert('end', f"{s1}\n", 'ir_num')
                else:
                    self.ir_view.insert('end', f"{s1}\n", 'ir_var')
            elif op in ['+', '-', '*', '/', '%']:
                self.ir_view.insert('end', f" {d} ", 'ir_var')
                self.ir_view.insert('end', "= ", 'ir_op')
                self.ir_view.insert('end', f"{s1} ", 'ir_var')
                self.ir_view.insert('end', f"{op} ", 'ir_op')
                self.ir_view.insert('end', f"{s2}\n", 'ir_var')
            elif op in ['<', '<=', '>', '>=', '==', '!=']:
                self.ir_view.insert('end', f" {d} ", 'ir_var')
                self.ir_view.insert('end', "= ", 'ir_op')
                self.ir_view.insert('end', f"{s1} ", 'ir_var')
                self.ir_view.insert('end', f"{op} ", 'ir_op')
                self.ir_view.insert('end', f"{s2}\n", 'ir_var')
            elif op == 'mark':
                self.ir_view.insert('end', f"\n{s1}:\n", 'ir_label')
            elif op == 'jump':
                self.ir_view.insert('end', " goto ", 'ir_op')
                self.ir_view.insert('end', f"{s1}\n", 'ir_label')
            elif op == 'jump_if_false':
                self.ir_view.insert('end', " if !", 'ir_op')
                self.ir_view.insert('end', f"{s1} ", 'ir_var')
                self.ir_view.insert('end', "goto ", 'ir_op')
                self.ir_view.insert('end', f"{s2}\n", 'ir_label')
            elif op == 'output':
                self.ir_view.insert('end', " print ", 'ir_op')
                self.ir_view.insert('end', f"{s1}\n", 'ir_var')
        
        # Assembly with colors
        asm = self.translator.translate(self.processor.ir_instructions)
        for line in asm:
            line = line.strip()
            if not line:
                self.asm_view.insert('end', "\n")
            elif line.endswith(':'):
                # Label
                self.asm_view.insert('end', f"{line}\n", 'asm_label')
            elif line.startswith(';'):
                # Comment
                self.asm_view.insert('end', f"{line}\n", 'asm_comment')
            else:
                # Instruction
                parts = line.split(None, 1)
                if parts:
                    self.asm_view.insert('end', f"    {parts[0]}", 'asm_instruction')
                    if len(parts) > 1:
                        # Highlight registers
                        operands = parts[1]
                        for token in re.split(r'([,\s\[\]]+)', operands):
                            if token.startswith('R') or token in ['EAX', 'EBX', 'ECX', 'EDX']:
                                self.asm_view.insert('end', token, 'asm_register')
                            elif token.isdigit():
                                self.asm_view.insert('end', token, 'ir_num')
                            else:
                                self.asm_view.insert('end', token)
                    self.asm_view.insert('end', "\n")
        
        # Errors with colors
        all_errs = lex_errs + self.processor.issues
        if all_errs:
            for idx, err in enumerate(all_errs, 1):
                self.err_view.insert('end', "❌ ", 'error_icon')
                self.err_view.insert('end', f"{err}\n\n", 'error_text')
            self.status_label.config(text=f"❌ {len(all_errs)} problem(s)")
        else:
            self.err_view.insert('end', "✓ ", 'success_icon')
            self.err_view.insert('end', "No problems detected")
            self.status_label.config(text="✓ Build successful")
        
    def reset_all(self):
        if self.file_modified:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Do you want to save changes before clearing?"
            )
            if response is True:
                self.save_file()
            elif response is None:
                return
        
        self.code_input.delete('1.0', tk.END)
        for view in ['tok_view', 'var_view', 'ir_view', 'asm_view', 'err_view']:
            getattr(self, view).delete('1.0', tk.END)
        
        self.processor.registry.clear()
        self.current_file = None
        self.file_modified = False
        self.update_title()
        self.status_label.config(text="Ready")
        self.update_line_numbers()


if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerInterface(root)
    root.mainloop()
