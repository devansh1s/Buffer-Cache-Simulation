from clr import Clr

# process class simulates a process
class Process:

    def __init__(self, name):
        self.name = name
        # possible status for a process :
        # idle = 0,
        # reading = 1,
        # writing = 2,
        # writing (delayed) = 3,
        # waiting (for a particular block or any block) = 4
        self.status = 0
        # possible values for waiting_type:
        # "read" : process is waiting to read a block
        # "write" : process is waiting to write to a block
        self.waiting_type = None
        self.block_requested = None
        self.buffer_assigned = None
        self.clr = Clr()

    # convenience function for printing a process
    def __str__(self):

        res = f"{self.clr.UNDERLINE}Process " + str(self.name) + f"{self.clr.END} ::\n"
        if self.status == 0:
            res += f"\tStatus:  {self.clr.YELLOW}`idle`{self.clr.END}."
            res += "\n"
            return res

        elif self.status == 1 and self.block_requested is not None:
            res += f"\tStatus: {self.clr.GREEN}`reading`{self.clr.END} Block: " + str(self.block_requested)
            res += "\n\tBuffer Assigned: " + str(self.buffer_assigned)
            res += "\n"
            return res

        elif (self.status == 2 or self.status == 3) and self.block_requested is not None:
            res += f"\tStatus: {self.clr.GREEN}`writing`{self.clr.END} to the Block: " + str(self.block_requested)
            res += "\n\tBuffer Assigned: " + str(self.buffer_assigned)
            res += "\n"
            return res

        elif self.status == 4 and self.block_requested is not None:
            if self.buffer_assigned is None:
                res += f"\tStatus: {self.clr.RED}`waiting`{self.clr.END} for any Buffer to become free."
                res += "\n"

            else:

                res += f"\tStatus: {self.clr.RED}`waiting`{self.clr.END} for the Buffer: " +\
                       str(self.buffer_assigned) + " to become free."
                res += "\n"

            return res

        elif self.status > 4:
            return f"{self.clr.RED}ERROR in Process " + str(self.name) + ".\nStatus is undefined (" + str(
                self.status) + f").{self.clr.END}"  # 1 = error

        elif self.block_requested is None:
            return f"{self.clr.RED}ERROR in Process " + str(self.name) + ".\nNo Block assigned with status = " +\
                   str(self.status) + f".{self.clr.END}"

    # this function will return the current status of the process
    def get_status(self):
        return self.status

    # get_assigned_buffer(self):
    def get_assigned_buffer(self):
        return self.buffer_assigned

    # Function to set the status of the process INPUT:: status: [0,1,2,3,4] which implies the state of the process
    # buffer_assigned: name of the buffer assigned to the process for performing any task (read/write/delayed write)
    # block_requested: name of the block that the process has requested to read/write data from. (resides in sec.
    # memory)
    # RETURN::
    #   0 : success
    #   1 : Error
    def set_status(self, status, buffer_assigned=None, block_requested=None, waiting_type=None):

        if status == 0:  # idle state doesn't require any block/buffer
            self.status = status
            self.buffer_assigned = None
            self.block_requested = None
            self.waiting_type = None
            return 0  # 0 = successful

        elif block_requested is None or status > 4:  # will return error if no block is requested
            return 1  # 1 = error

        else:  # will assign a buffer and set status
            self.status = status
            self.block_requested = block_requested
            self.buffer_assigned = buffer_assigned
            self.waiting_type = waiting_type
            return 0  # 0 = successful


# for testing only
if __name__ == "__main__":
    p1 = Process("P1")

    if p1.set_status(0):
        print("Error encountered.")
        exit(0)
    print(p1)
