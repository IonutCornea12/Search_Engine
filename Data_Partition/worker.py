import json
from search_service import SearchService

class Worker:
    def __init__(self, worker_id, directories, connection, search_service=None):
        self.worker_id = worker_id
        self.directories = directories
        self.conn = connection
        self.search_service = search_service or SearchService()

    def run(self):
        print(f"[Worker {self.worker_id}] Started. Assigned {len(self.directories)} directories.")

        while True:
            msg_str = self.conn.recv()
            data = json.loads(msg_str)
            command = data.get("command", "")

            if command == "search":
                query = data.get("query", "")
                results = []
                for directory in self.directories:
                    results.extend(self.search_service.search_files_in_directory(directory, query))
                response = json.dumps({
                    "command": "result",
                    "worker_id": self.worker_id,
                    "results": results
                })
                self.conn.send(response)

            elif command == "exit":
                print(f"[Worker {self.worker_id}] Exiting...")
                break

            else:
                print(f"[Worker {self.worker_id}] Unknown command: {command}")

        self.conn.close()

def worker_process_entry(worker_id, directories, connection):
    worker = Worker(worker_id, directories, connection)
    worker.run()