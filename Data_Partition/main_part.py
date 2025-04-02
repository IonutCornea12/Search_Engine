from directory_picker import DirectoryPicker
from manager import Manager

def main():
    num_workers = 5
    picker = DirectoryPicker()

    print("\nSelect the root directory containing subfolders to search:")
    root_dir = picker.pick_root_directory()
    if not root_dir:
        print("No directory selected. Exiting.")
        return

    subdirs = picker.get_subdirectories(root_dir)
    if not subdirs:
        print("No subdirectories found in the selected folder.")
        return

    print(f"\nFound {len(subdirs)} subdirectories. Assigning to {num_workers} workers.")
    worker_dirs = picker.assign_subdirs_to_workers(subdirs, num_workers)

    #each worker will search a list of directories
    manager = Manager(worker_dirs)

    try:
        while True:
            query = input("\nEnter search query (or 'quit' to exit): ").strip()
            if query.lower() in ["quit", "exit"]:
                break
            if not query:
                continue

            results = manager.search(query)
            if results:
                print(f"\n[Manager] Found {len(results)} result(s):")
                for path in results:
                    print(f"  {path}")
            else:
                print("\n[Manager] No matches found.")

    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        manager.shutdown()

if __name__ == "__main__":
    main()