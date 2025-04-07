import json
from multiprocessing import Process, Pipe
from worker import worker_process_entry

class Manager:
    def __init__(self, directories_per_worker):
        """
        directories_per_worker: list of lists, each sublist = directories for one worker
        """
        self.manager_conns = []#to talk with workers
        self.processes = [] #stores processes
        self.cache = {} #previous query results

        for i, dir_list in enumerate(directories_per_worker, start=1):
            parent_conn, child_conn = Pipe()
            #child_conn passed to worker to recieve results
            #parent_conn used by manager to talk to worker
            p = Process(target=worker_process_entry, args=(i, dir_list, child_conn))
            p.start()
            self.manager_conns.append(parent_conn)
            self.processes.append(p)
        print("[Manager] All workers spawned.")

    def search(self, query):
        if query in self.cache:
            print("[Manager] Cache hit! Returning cached results.") #for 
            return self.cache[query]


        request_msg = json.dumps({"command": "search", "query": query})
        print(f"[Manager] Sending request to workers: {request_msg}")

        for conn in self.manager_conns:
            conn.send(request_msg)

        aggregated_results = []
        for conn in self.manager_conns:
            response_str = conn.recv()
            response = json.loads(response_str)
            if response.get("command") == "result":
                aggregated_results.extend(response.get("results", []))

        ranked = sorted(aggregated_results, key=lambda path: path.lower())
        self.cache[query] = ranked
        return ranked

    def shutdown(self):
        exit_msg = json.dumps({"command": "exit"})
        for conn in self.manager_conns:
            conn.send(exit_msg)

        for p in self.processes:
            p.join()

        print("[Manager] All workers shut down cleanly.")