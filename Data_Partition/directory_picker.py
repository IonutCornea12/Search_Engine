import tkinter as tk
from tkinter import filedialog
import os

class DirectoryPicker:
    def pick_root_directory(self):
        root = tk.Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title="Select root directory for search")
        root.destroy()
        return folder

    def get_subdirectories(self, root_directory):
        # Recursively gets all immediate subdirectories of the root.
        return [os.path.join(root_directory, d) for d in os.listdir(root_directory)
                if os.path.isdir(os.path.join(root_directory, d))]

    def assign_subdirs_to_workers(self, subdirs, num_workers):

       # Partitions the list of subdirs into num_workers groups
        partitions = [[] for _ in range(num_workers)]
        for i, subdir in enumerate(subdirs):
            partitions[i % num_workers].append(subdir)
        return partitions