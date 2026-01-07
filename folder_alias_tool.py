import os
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

#Windows API：用来设置文件/文件夹属性
GetFileAttributesW = ctypes.windll.kernel32.GetFileAttributesW
GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
GetFileAttributesW.restype = wintypes.DWORD

SetFileAttributesW = ctypes.windll.kernel32.SetFileAttributesW
SetFileAttributesW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD]
SetFileAttributesW.restype = wintypes.BOOL

#文件属性常量
FILE_ATTRIBUTE_READONLY = 0x00000001
FILE_ATTRIBUTE_HIDDEN = 0x00000002
FILE_ATTRIBUTE_SYSTEM = 0x00000004


def add_file_attributes(path: str, flags: int):
#文件属性常量给文件/文件夹增加指定属性（不覆盖原有属性，只是OR一下）。等价于 attrib +s / +h / +r 之类，但不用调用 cmd。
    path_w = os.path.abspath(path)
    attrs = GetFileAttributesW(path_w)
    if attrs == 0xFFFFFFFF:  # INVALID_FILE_ATTRIBUTES
        return False, f"无法获取属性：{path_w}"

    new_attrs = attrs | flags
    if not SetFileAttributesW(path_w, new_attrs):
        return False, f"无法设置属性：{path_w}"

    return True, "OK"


def set_folder_alias(folder_path: str, alias: str):
#在指定folder_path下创建/覆盖desktop.ini，设置LocalizedResourceName=alias，并给文件夹加SYSTEM属性，desktop.ini加SYSTEM+HIDDEN。
    alias = alias.strip()
    if not alias:
        return False, "别名为空，已跳过"

    if not os.path.isdir(folder_path):
        return False, f"路径不是文件夹：{folder_path}"

    desktop_ini = os.path.join(folder_path, "desktop.ini")

    try:
        #使用Windows风格换行，并使用系统默认编码
        content = "[.ShellClassInfo]\r\nLocalizedResourceName=" + alias + "\r\n"

        # 不指定encoding，让它用系统默认编码（中文系统通常是 ANSI/GBK）
        with open(desktop_ini, "w") as f:
            f.write(content)

        # 1)文件夹：增加SYSTEM属性（等价于attrib +s "文件夹"）
        ok1, msg1 = add_file_attributes(folder_path, FILE_ATTRIBUTE_SYSTEM)
        if not ok1:
            return False, msg1

        # 2)desktop.ini：增加SYSTEM+HIDDEN（等价于attrib +s +h "...\desktop.ini"）
        ok2, msg2 = add_file_attributes(
            desktop_ini,
            FILE_ATTRIBUTE_SYSTEM | FILE_ATTRIBUTE_HIDDEN
        )
        if not ok2:
            return False, msg2

        return True, "成功"
    except Exception as e:
        return False, f"错误：{e}"


class ScrollableFrame(ttk.Frame):
 #简单的可滚动 Frame，用于批量模式下显示很多子文件夹行。
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        self._window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        #让内容宽度随窗口变化
        def _on_frame_configure(event):
            canvas.itemconfig(self._window, width=event.width)

        self.bind("<Configure>", _on_frame_configure)


class FolderAliasTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("文件夹别名工具")
        self.geometry("900x650")

        #批量别名上一次快照，用于撤销
        self.last_alias_snapshot = None

        #主Notebook
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        #单个模式Tab
        self.single_tab = ttk.Frame(notebook)
        #批量模式Tab
        self.batch_tab = ttk.Frame(notebook)

        notebook.add(self.single_tab, text="单个设置")
        notebook.add(self.batch_tab, text="批量设置")

        self.create_single_tab()
        self.create_batch_tab()

    #单个设置
    def create_single_tab(self):
        frame = self.single_tab

        #选择文件夹
        path_label = ttk.Label(frame, text="目标文件夹：")
        path_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.single_path_var = tk.StringVar()
        path_entry = ttk.Entry(frame, textvariable=self.single_path_var, width=60)
        path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        browse_btn = ttk.Button(frame, text="浏览...", command=self.browse_single_folder)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)

        #设置别名
        alias_label = ttk.Label(frame, text="显示别名（中文）：")
        alias_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.single_alias_var = tk.StringVar()
        alias_entry = ttk.Entry(frame, textvariable=self.single_alias_var, width=40)
        alias_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        #提示
        hint = ttk.Label(
            frame,
            text="说明：仅改变资源管理器显示名称，实际路径仍保持原英文目录名。",
            foreground="gray"
        )
        hint.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        #应用按钮
        apply_btn = ttk.Button(frame, text="应用别名", command=self.apply_single_alias)
        apply_btn.grid(row=3, column=1, padx=5, pady=20, sticky="w")

    def browse_single_folder(self):
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            self.single_path_var.set(folder)
            #默认把别名设为当前文件夹名，方便修改
            self.single_alias_var.set(os.path.basename(folder))

    def apply_single_alias(self):
        folder = self.single_path_var.get().strip()
        alias = self.single_alias_var.get().strip()

        if not folder:
            messagebox.showwarning("提示", "请先选择一个文件夹。")
            return
        if not os.path.isdir(folder):
            messagebox.showerror("错误", f"路径不存在或不是文件夹：\n{folder}")
            return
        if not alias:
            messagebox.showwarning("提示", "别名不能为空。")
            return

        ok, msg = set_folder_alias(folder, alias)
        if ok:
            messagebox.showinfo(
                "完成",
                f"设置成功：\n{folder}\n显示为：{alias}\n\n提示：请回到该文件夹的上一级目录查看显示名称，如未生效可尝试关闭并重新打开资源管理器。"
            )
        else:
            messagebox.showerror("失败", f"设置失败：{msg}")

    #批量设置
    def create_batch_tab(self):
        frame = self.batch_tab

        #上方：选择根目录、是否递归
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(top_frame, text="根目录：").grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.batch_root_var = tk.StringVar()
        root_entry = ttk.Entry(top_frame, textvariable=self.batch_root_var, width=60)
        root_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        browse_root_btn = ttk.Button(top_frame, text="浏览...", command=self.browse_batch_root)
        browse_root_btn.grid(row=0, column=2, padx=5, pady=5)

        self.recursive_var = tk.BooleanVar(value=False)
        recursive_check = ttk.Checkbutton(
            top_frame,
            text="递归扫描所有子文件夹（不勾选则只扫描第一层）",
            variable=self.recursive_var
        )
        recursive_check.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        scan_btn = ttk.Button(top_frame, text="扫描子文件夹", command=self.scan_subfolders)
        scan_btn.grid(row=1, column=2, padx=5, pady=5)

        #中间：前缀/后缀设置
        mid_frame = ttk.LabelFrame(frame, text="前缀/后缀批量设置")
        mid_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(mid_frame, text="前缀：").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.prefix_var = tk.StringVar()
        prefix_entry = ttk.Entry(mid_frame, textvariable=self.prefix_var, width=20)
        prefix_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(mid_frame, text="后缀：").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.suffix_var = tk.StringVar()
        suffix_entry = ttk.Entry(mid_frame, textvariable=self.suffix_var, width=20)
        suffix_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        apply_prefix_suffix_btn = ttk.Button(
            mid_frame,
            text="将前缀/后缀应用到下方别名列表",
            command=self.apply_prefix_suffix_to_list
        )
        apply_prefix_suffix_btn.grid(row=0, column=4, padx=5, pady=5)

        clear_alias_btn = ttk.Button(
            mid_frame,
            text="清空别名",
            command=self.clear_alias_list
        )
        clear_alias_btn.grid(row=0, column=5, padx=5, pady=5)

        undo_btn = ttk.Button(
            mid_frame,
            text="撤销上次更改",
            command=self.undo_alias_changes
        )
        undo_btn.grid(row=0, column=6, padx=5, pady=5)

        #下方：可滚动的子文件夹列表
        list_frame = ttk.LabelFrame(frame, text="子文件夹列表（可逐个修改别名）")
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.scrollable = ScrollableFrame(list_frame)
        self.scrollable.pack(fill="both", expand=True)

        #表头
        header = ttk.Frame(self.scrollable.scrollable_frame)
        header.pack(fill="x", pady=(0, 5))

        ttk.Label(header, text="原文件夹名", width=30).pack(side="left", padx=5)
        ttk.Label(header, text="显示别名（可修改）", width=30).pack(side="left", padx=5)
        ttk.Label(header, text="完整路径", width=60).pack(side="left", padx=5)

        self.batch_rows = []  # 每行：{"path", "name_label", "alias_entry", "path_label", "row_frame"}

        #底部：应用按钮
        bottom_frame = ttk.Frame(frame)
        bottom_frame.pack(fill="x", padx=5, pady=5)

        apply_batch_btn = ttk.Button(bottom_frame, text="批量应用别名", command=self.apply_batch_aliases)
        apply_batch_btn.pack(side="right", padx=5)

        note = ttk.Label(
            bottom_frame,
            text="提示：回到上一级目录查看文件夹显示名称，必要时重启资源管理器。",
            foreground="gray"
        )
        note.pack(side="left", padx=5)

    def browse_batch_root(self):
        folder = filedialog.askdirectory(title="选择根目录")
        if folder:
            self.batch_root_var.set(folder)

    def clear_batch_rows(self):
        for row in self.batch_rows:
            row["row_frame"].destroy()
        self.batch_rows.clear()
        self.last_alias_snapshot = None

    def scan_subfolders(self):
        root = self.batch_root_var.get().strip()
        if not root:
            messagebox.showwarning("提示","请先选择根目录。")
            return
        if not os.path.isdir(root):
            messagebox.showerror("错误",f"路径不存在或不是文件夹：\n{root}")
            return

        self.clear_batch_rows()

        subfolders = []
        if self.recursive_var.get():
            # 递归扫描
            for dirpath, dirnames, _ in os.walk(root):
                for d in dirnames:
                    full_path = os.path.join(dirpath, d)
                    subfolders.append(full_path)
        else:
            # 只扫描第一层
            for name in os.listdir(root):
                full_path = os.path.join(root, name)
                if os.path.isdir(full_path):
                    subfolders.append(full_path)

        if not subfolders:
            messagebox.showinfo("提示","未找到任何子文件夹。")
            return

        subfolders.sort()

        for path in subfolders:
            folder_name = os.path.basename(path)

            row_frame = ttk.Frame(self.scrollable.scrollable_frame)
            row_frame.pack(fill="x", padx=5, pady=2)

            name_label = ttk.Label(row_frame, text=folder_name, width=30)
            name_label.pack(side="left", padx=5)

            alias_var = tk.StringVar(value=folder_name)
            alias_entry = ttk.Entry(row_frame, textvariable=alias_var, width=30)
            alias_entry.pack(side="left", padx=5)
            alias_entry.configure(foreground="black")

            path_label = ttk.Label(row_frame, text=path, width=60)
            path_label.pack(side="left", padx=5)

            self.batch_rows.append({
                "path": path,
                "name_label": name_label,
                "alias_entry": alias_entry,
                "path_label": path_label,
                "row_frame": row_frame,
            })

        #扫描后清空撤销快照
        self.last_alias_snapshot = None

    #新增：清空&撤销-
    def snapshot_aliases(self):
        #保存当前别名列表，用于撤销
        self.last_alias_snapshot = [
            row["alias_entry"].get() for row in self.batch_rows
        ]

    def clear_alias_list(self):
        #清空别名（先做快照，便于撤销）
        if not self.batch_rows:
            messagebox.showwarning("提示", "没有子文件夹记录，请先扫描。")
            return

        self.snapshot_aliases()

        for row in self.batch_rows:
            entry: ttk.Entry = row["alias_entry"]
            entry.delete(0, tk.END)

        messagebox.showinfo("完成", "已清空别名，如需恢复请点击“撤销上次更改”。")

    def undo_alias_changes(self):
        #撤销上一次apply_prefix_suffix/clear操作。
        if not self.batch_rows or not self.last_alias_snapshot:
            messagebox.showwarning("提示", "当前没有可撤销的更改。")
            return

        #为防万一，按最短长度恢复
        n = min(len(self.batch_rows), len(self.last_alias_snapshot))
        for i in range(n):
            entry: ttk.Entry = self.batch_rows[i]["alias_entry"]
            entry.delete(0, tk.END)
            entry.insert(0, self.last_alias_snapshot[i])

        messagebox.showinfo("完成", "已撤销上次更改。")

    #批量应用前缀/后缀&写desktop.ini
    def apply_prefix_suffix_to_list(self):
        prefix = self.prefix_var.get()
        suffix = self.suffix_var.get()

        if not self.batch_rows:
            messagebox.showwarning("提示", "没有子文件夹记录，请先扫描。")
            return

        #应用前先保存一个快照，便于撤销
        self.snapshot_aliases()

        for row in self.batch_rows:
            entry: ttk.Entry = row["alias_entry"]
            current = entry.get().strip()
            if not current:
                #如果当前为空，就用原名字
                current = row["name_label"].cget("text")
            new_alias = f"{prefix}{current}{suffix}"
            entry.delete(0, tk.END)
            entry.insert(0, new_alias)

        messagebox.showinfo("完成", "前缀/后缀已应用到别名列表，可以继续手动微调或使用“撤销上次更改”。")

    def apply_batch_aliases(self):
        if not self.batch_rows:
            messagebox.showwarning("提示", "没有子文件夹记录，请先扫描。")
            return

        success_count = 0
        fail_count = 0
        fail_messages = []

        for row in self.batch_rows:
            path = row["path"]
            alias = row["alias_entry"].get().strip()
            if not alias:
                continue

            ok, msg = set_folder_alias(path, alias)
            if ok:
                success_count += 1
            else:
                fail_count += 1
                fail_messages.append(f"{path} -> {msg}")

        summary = f"批量设置完成。\n成功：{success_count} 个\n失败：{fail_count} 个"
        if fail_messages:
            summary += "\n\n失败详情：\n" + "\n".join(fail_messages[:10])
            if len(fail_messages) > 10:
                summary += f"\n……共 {len(fail_messages)} 条失败记录，仅显示前 10 条。"

        messagebox.showinfo("完成", summary)


if __name__ == "__main__":
    app = FolderAliasTool()
    app.mainloop()
