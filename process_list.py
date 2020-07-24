from process import Process
from clr import Clr


# processList class manages the list of the processes
class ProcessList:

    # constructor of the processList
    # gen (optional) : no of initial processes (default is 4)
    def __init__(self, gen=4):
        self.all_processes = {}
        self.no_of_active_processes = 0
        self.clr = Clr()
        if gen:
            self._generate_processes(gen)

    # __str__(self): convenience function for printing the processList
    def __str__(self):
        res = [f"{self.clr.BLUE}PROCESS LIST{self.clr.END}\n"]
        for _, value in self.all_processes.items():
            res.append(str(value))
        if len(res) == 0:
            res = ["Process list is EMPTY!! Try adding some processes from the Menu"]

        return '\n'.join(res)

    # function to get the block_requested by the process
    # INPUT::
    #   name : name of the process requesting the block
    # RETURN::
    #   block_num : block number requested by the process
    def get_block_requested(self, name):
        return self.all_processes[name].block_requested

    # function to get the waiting type of the process
    # INPUT::
    #   name : name of the process
    # RETURN::
    #   waiting_type
    #   False : if not waiting
    def get_waiting_type(self, name):
        typ = self.all_processes[name].waiting_type
        if typ is not None:
            return self.all_processes[name].waiting_type
        return False

    # print_process_list(self): Function to print the entire processList
    def print_process_list(self):
        res = f"{self.clr.BLUE}\tPROCESS LIST{self.clr.END}\n"
        for _, value in self.all_processes.items():
            res += str(value)
        if len(res) == 0:
            res = "Process list is EMPTY!! Try adding some processes from the Menu"
        print(res)

    # _get_unused_process_name(self): Function which returns an unused name for creating a new process
    # by searching through the list of all_processes
    # RETURN::
    # string of name which can be used to create new process
    def _get_unused_process_name(self):

        if len(self.all_processes) == 0:
            return "P" + str(0)

        name_list = []
        for key, _ in self.all_processes.items():
            key = key[1:]
            key = int(key)
            name_list.append(key)

        name_list.sort()

        res = name_list[-1] + 1
        for i in range(name_list[-1]):
            if i != name_list[i]:
                res = i
                break

        return "P" + str(res)

    # _generate_processes(self, no): Function to generate random processes
    # no : no. of processes to generate
    def _generate_processes(self, no):
        for _ in range(no):
            name = self._get_unused_process_name()
            temp = Process(name)
            self.all_processes[name] = temp
            self.no_of_active_processes += 1

    # is_name_duplicate(self, name): Function which checks whether the given name of the process if a duplicate of
    # an active process already present in the all_process list
    # INPUT::
    #   name : name of the process to check for duplicate
    # RETURN::
    #   0 : success (not duplicate)
    #   1 : failure (duplicate)
    def is_name_duplicate(self, name):

        if name in self.all_processes:
            return 1  # name is duplicate

        else:
            return 0  # name is not duplicate

    # Getter Function for no. of active processes
    # RETURN::
    # no. of active processes
    def get_no_of_active_processes(self):
        return self.no_of_active_processes

    # add_process(name): Function to add a new process
    # name (optional): name of the new process
    # RETURN::
    # 0 : success
    # 1 : error
    def add_process(self, name=None):
        if name is None:
            name = self._get_unused_process_name()

        else:
            if self.is_name_duplicate(name):
                return 1  # 1 : ERROR (name is duplicate)

        temp = Process(name)
        self.all_processes[name] = temp
        self.no_of_active_processes += 1

        return 0  # 0 : successful

    # del_process(name): Function to delete an existing process from the all_processes list
    # INPUT::
    #   name : name of the process to delete
    # RETURN::
    # 0 : success
    # 1 : error / invalid name entered
    def del_process(self, name):

        if self.is_name_duplicate(name):  # if name is present in the list
            del self.all_processes[name]
            return 0  # success

        else:
            return 1  # failure / error / name not present

    # function to check wheter there is any buffer assigned to the process
    # INPUT::
    #   name : name of process
    # RETURN::
    #   True: there is some buffer assigned
    #   False : no buffer assigned
    def is_any_buffer_assigned(self, name):
        if self.is_name_duplicate(name):  # process exists
            if self.all_processes[name].get_status() == 0:  # no buffer occupied
                return False
            return True

    # release_buffer(self, name): Function to release the buffer currently occupied by the given process
    # INPUT::
    #   name : name of the process occupying the buffer
    # RETURN::
    #   (-1,-1): no buffer occupied by the process
    #   (-2,-2) : process doesn't exist
    #   (buf_name, status) : success. name of the buffer released, status of process before buffer release
    def release_buffer(self, name):

        if self.is_name_duplicate(name):  # process exists
            if self.all_processes[name].get_status() == 0:  # no buffer occupied
                return -1, -1  # error / no buffer occupied

            else:
                status = self.all_processes[name].get_status()
                buf_name = self.all_processes[name].buffer_assigned

                self.all_processes[name].set_status(0)
                return buf_name, status  # successfully released the occupied buffer

        else:
            return -2, -2  # process doesn't exist / ERROR


# for testing only
if __name__ == "__main__":
    pl = ProcessList()
    pl.all_processes["P1"].set_status(4, None, "blk1")
    print(pl.get_no_of_active_processes())
