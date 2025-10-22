import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from pathlib import Path

class FileRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("文件重命名工具")
        self.root.geometry("1000x700")
        
        # 当前目录
        self.current_directory = ""
        self.files_data = []  # 存储文件信息
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 目录选择区域
        dir_frame = ttk.LabelFrame(main_frame, text="目录选择", padding="5")
        dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Button(dir_frame, text="选择目录", command=self.select_directory).grid(row=0, column=0, padx=(0, 10))
        self.dir_label = ttk.Label(dir_frame, text="未选择目录", foreground="gray")
        self.dir_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # 文件列表区域
        files_frame = ttk.LabelFrame(main_frame, text="文件列表", padding="5")
        files_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ("原文件名", "文件名部分", "新文件名", "操作")
        self.tree = ttk.Treeview(files_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            
        # 设置列宽
        self.tree.column("原文件名", width=200)
        self.tree.column("文件名部分", width=300)
        self.tree.column("新文件名", width=200)
        self.tree.column("操作", width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 绑定双击事件
        self.tree.bind("<Double-1>", self.on_item_double_click)
        
        # 操作按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="刷新文件列表", command=self.refresh_files).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="一键应用", command=self.apply_first_pattern).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="批量复制", command=self.batch_copy).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="批量移动", command=self.batch_move).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="预览更改", command=self.preview_changes).pack(side=tk.LEFT, padx=(0, 10))
        
    def select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory(title="选择要处理的目录")
        if directory:
            self.current_directory = directory
            self.dir_label.config(text=directory, foreground="black")
            self.refresh_files()
            
    def refresh_files(self):
        """刷新文件列表"""
        if not self.current_directory:
            messagebox.showwarning("警告", "请先选择目录")
            return
            
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.files_data.clear()
        
        try:
            # 获取目录中的所有文件
            for file_path in Path(self.current_directory).iterdir():
                if file_path.is_file():
                    filename = file_path.name
                    name_without_ext = file_path.stem
                    extension = file_path.suffix
                    
                    # 按下划线分割文件名
                    parts = name_without_ext.split('_')
                    parts_str = ' | '.join(parts) if len(parts) > 1 else parts[0]
                    
                    # 存储文件信息
                    file_info = {
                        'path': str(file_path),
                        'original_name': filename,
                        'name_parts': parts,
                        'extension': extension,
                        'new_name': filename  # 初始时新文件名等于原文件名
                    }
                    self.files_data.append(file_info)
                    
                    # 添加到树形视图
                    self.tree.insert("", tk.END, values=(
                        filename,
                        parts_str,
                        filename,
                        "点击编辑"
                    ))
                    
        except Exception as e:
            messagebox.showerror("错误", f"读取目录失败: {str(e)}")
            
    def on_item_double_click(self, event):
        """双击编辑文件名"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        item_index = self.tree.index(item)
        file_info = self.files_data[item_index]
        
        # 打开编辑窗口
        self.open_edit_window(file_info, item_index)
        
    def open_edit_window(self, file_info, file_index):
        """打开编辑窗口"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"编辑文件名 - {file_info['original_name']}")
        edit_window.geometry("500x600")
        edit_window.resizable(False, False)
        
        # 设置为模态窗口
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(edit_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 原文件名显示
        ttk.Label(main_frame, text="原文件名:").pack(anchor=tk.W)
        ttk.Label(main_frame, text=file_info['original_name'], font=("", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # 文件名部分选择
        ttk.Label(main_frame, text="选择要包含的文件名部分 (按选择顺序拼接):").pack(anchor=tk.W)
        
        # 创建多选框架
        checkbox_frame = ttk.Frame(main_frame)
        checkbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # 创建滚动区域
        canvas = tk.Canvas(checkbox_frame, height=200)
        scrollbar = ttk.Scrollbar(checkbox_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 存储多选框变量和顺序
        self.checkbox_vars = []
        self.checkbox_order = []
        self.selected_parts = []
        
        # 为每个部分创建多选框
        for i, part in enumerate(file_info['name_parts']):
            var = tk.BooleanVar()
            var.set(True)  # 默认全选
            self.checkbox_vars.append(var)
            
            checkbox = ttk.Checkbutton(
                scrollable_frame, 
                text=f"{i+1}. {part}", 
                variable=var,
                command=lambda idx=i: self.on_checkbox_change(idx, file_info)
            )
            checkbox.pack(anchor=tk.W, pady=2)
        
        # 初始化选中顺序
        for i in range(len(file_info['name_parts'])):
            self.checkbox_order.append(i)
            self.selected_parts.append(file_info['name_parts'][i])
        
        # 添加自定义部分的输入框
        custom_frame = ttk.Frame(main_frame)
        custom_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(custom_frame, text="添加自定义部分:").pack(anchor=tk.W)
        custom_input_frame = ttk.Frame(custom_frame)
        custom_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.custom_entry = ttk.Entry(custom_input_frame)
        self.custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(custom_input_frame, text="添加", command=lambda: self.add_custom_part(file_info)).pack(side=tk.RIGHT)
        
        # 预览区域
        ttk.Label(main_frame, text="新文件名预览:").pack(anchor=tk.W)
        self.preview_label = ttk.Label(main_frame, text="", font=("", 10, "bold"), foreground="blue")
        self.preview_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 更新预览
        self.update_checkbox_preview(file_info)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="确定", command=lambda: self.apply_checkbox_changes(file_info, file_index, edit_window)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=edit_window.destroy).pack(side=tk.RIGHT)
        
        # 存储当前编辑的文件信息
        self.current_edit_file = file_info
        
    def on_checkbox_change(self, index, file_info):
        """处理多选框状态变化"""
        if self.checkbox_vars[index].get():
            # 选中：按原始顺序添加到选中列表
            if index not in self.checkbox_order:
                # 找到正确的插入位置以保持原始顺序
                insert_pos = 0
                for i, existing_index in enumerate(self.checkbox_order):
                    if existing_index > index:
                        insert_pos = i
                        break
                    insert_pos = i + 1
                
                self.checkbox_order.insert(insert_pos, index)
                self.selected_parts.insert(insert_pos, file_info['name_parts'][index])
        else:
            # 取消选中：从选中列表中移除
            if index in self.checkbox_order:
                pos = self.checkbox_order.index(index)
                self.checkbox_order.pop(pos)
                self.selected_parts.pop(pos)
        
        self.update_checkbox_preview(file_info)
    
    def add_custom_part(self, file_info):
        """添加自定义部分"""
        custom_text = self.custom_entry.get().strip()
        if custom_text:
            self.selected_parts.append(custom_text)
            self.custom_entry.delete(0, tk.END)
            self.update_checkbox_preview(file_info)
    
    def update_checkbox_preview(self, file_info):
        """更新多选框模式的文件名预览"""
        if self.selected_parts:
            new_name = '_'.join(self.selected_parts) + file_info['extension']
        else:
            new_name = file_info['extension']
            
        self.preview_label.config(text=new_name)
        
    def apply_checkbox_changes(self, file_info, file_index, edit_window):
        """应用多选框的更改"""
        # 生成新文件名
        if self.selected_parts:
            new_name = '_'.join(self.selected_parts) + file_info['extension']
        else:
            new_name = file_info['extension']
            
        # 更新文件信息
        self.files_data[file_index]['name_parts'] = self.selected_parts.copy()
        self.files_data[file_index]['new_name'] = new_name
        
        # 更新树形视图
        item = self.tree.get_children()[file_index]
        parts_str = ' | '.join(self.selected_parts) if self.selected_parts else ""
        self.tree.item(item, values=(
            file_info['original_name'],
            parts_str,
            new_name,
            "已修改"
        ))
        
        edit_window.destroy()
        
    def apply_first_pattern(self):
        """根据第一个修改好的文件的选择规则一键应用到其他文件"""
        if not self.files_data:
            messagebox.showwarning("警告", "没有文件可以处理")
            return
            
        # 找到第一个已修改的文件作为模板
        template_file = None
        template_index = -1
        
        for i, file_info in enumerate(self.files_data):
            if file_info['original_name'] != file_info['new_name']:
                template_file = file_info
                template_index = i
                break
                
        if not template_file:
            messagebox.showinfo("提示", "请先修改至少一个文件的命名规则作为模板")
            return
            
        # 获取模板文件的选择规则
        # 从原始文件名中分离出原始部分
        original_name_without_ext = template_file['original_name'].rsplit('.', 1)[0]
        template_original_parts = original_name_without_ext.split('_')
        
        # 获取模板文件当前选择的部分
        template_selected_parts = template_file['name_parts']
        
        # 分析选择规则：哪些原始部分被选中了，以及是否有自定义部分
        selected_indices = []
        custom_parts = []
        
        for selected_part in template_selected_parts:
            if selected_part in template_original_parts:
                # 这是原始部分
                selected_indices.append(template_original_parts.index(selected_part))
            else:
                # 这是自定义部分
                custom_parts.append(selected_part)
        
        # 确认应用
        selected_original = [template_original_parts[i] for i in selected_indices]
        rule_description = "选择的原始部分: " + ", ".join(selected_original) if selected_original else "无原始部分"
        if custom_parts:
            rule_description += "\n自定义部分: " + ", ".join(custom_parts)
            
        response = messagebox.askyesno("确认应用", 
                                    f"将根据文件 '{template_file['original_name']}' 的选择规则应用到其他文件。\n\n"
                                    f"选择规则：\n{rule_description}\n\n"
                                    f"将应用到其他 {len(self.files_data)-1} 个文件，是否继续？")
        if not response:
            return
            
        applied_count = 0
        skipped_count = 0
        
        # 应用规则到其他文件
        for i, file_info in enumerate(self.files_data):
            if i == template_index:  # 跳过模板文件本身
                continue
                
            # 获取当前文件的原始部分
            current_original_name = file_info['original_name'].rsplit('.', 1)[0]
            current_original_parts = current_original_name.split('_')
            
            try:
                # 按照模板的选择规则构建新的部分列表
                new_parts = []
                
                # 添加选中的原始部分
                for index in selected_indices:
                    if index < len(current_original_parts):
                        new_parts.append(current_original_parts[index])
                    else:
                        # 如果当前文件的部分数量不够，跳过这个文件
                        raise IndexError(f"部分索引 {index} 超出当前文件的部分范围")
                
                # 添加自定义部分
                new_parts.extend(custom_parts)
                
                # 生成新文件名
                if new_parts:
                    new_filename = '_'.join(new_parts) + file_info['extension']
                else:
                    new_filename = file_info['extension']
                
                # 更新文件信息
                self.files_data[i]['name_parts'] = new_parts
                self.files_data[i]['new_name'] = new_filename
                
                # 更新树形视图
                item = self.tree.get_children()[i]
                parts_str = ' | '.join(new_parts) if new_parts else ""
                self.tree.item(item, values=(
                    file_info['original_name'],
                    parts_str,
                    new_filename,
                    "已应用"
                ))
                
                applied_count += 1
                
            except (IndexError, ValueError) as e:
                skipped_count += 1
                continue
                
        # 显示结果
        result_msg = f"应用完成！\n成功应用: {applied_count} 个文件"
        if skipped_count > 0:
            result_msg += f"\n跳过: {skipped_count} 个文件（部分索引超出范围）"
            
        messagebox.showinfo("应用结果", result_msg)
        
    def preview_changes(self):
        """预览所有更改"""
        changes = []
        for file_info in self.files_data:
            if file_info['original_name'] != file_info['new_name']:
                changes.append(f"{file_info['original_name']} → {file_info['new_name']}")
                
        if not changes:
            messagebox.showinfo("预览", "没有需要更改的文件")
            return
            
        preview_text = "\n".join(changes)
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title("更改预览")
        preview_window.geometry("600x400")
        
        text_widget = tk.Text(preview_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, preview_text)
        text_widget.config(state=tk.DISABLED)
        
    def batch_copy(self):
        """批量复制文件"""
        self._batch_operation("copy")
        
    def batch_move(self):
        """批量移动文件"""
        self._batch_operation("move")
        
    def _batch_operation(self, operation):
        """执行批量操作"""
        if not self.current_directory:
            messagebox.showwarning("警告", "请先选择目录")
            return
            
        # 检查是否有需要处理的文件
        files_to_process = [f for f in self.files_data if f['original_name'] != f['new_name']]
        
        if not files_to_process:
            messagebox.showinfo("信息", "没有需要处理的文件")
            return
            
        # 选择目标目录
        target_dir = filedialog.askdirectory(title=f"选择{'复制' if operation == 'copy' else '移动'}目标目录")
        if not target_dir:
            return
            
        success_count = 0
        error_count = 0
        errors = []
        
        for file_info in files_to_process:
            try:
                source_path = file_info['path']
                target_path = os.path.join(target_dir, file_info['new_name'])
                
                # 检查目标文件是否已存在
                if os.path.exists(target_path):
                    response = messagebox.askyesno("文件已存在", 
                                                f"目标文件 {file_info['new_name']} 已存在，是否覆盖？")
                    if not response:
                        continue
                        
                if operation == "copy":
                    shutil.copy2(source_path, target_path)
                else:  # move
                    shutil.move(source_path, target_path)
                    
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"{file_info['original_name']}: {str(e)}")
                
        # 显示结果
        result_msg = f"操作完成！\n成功: {success_count} 个文件\n失败: {error_count} 个文件"
        if errors:
            result_msg += f"\n\n错误详情:\n" + "\n".join(errors[:5])  # 只显示前5个错误
            if len(errors) > 5:
                result_msg += f"\n... 还有 {len(errors) - 5} 个错误"
                
        messagebox.showinfo("操作结果", result_msg)
        
        # 如果是移动操作，刷新文件列表
        if operation == "move" and success_count > 0:
            self.refresh_files()

# 需要导入simpledialog
import tkinter.simpledialog

def main():
    root = tk.Tk()
    app = FileRenamer(root)
    root.mainloop()

if __name__ == "__main__":
    main()