from hash_queue import HashQueue
from clr import Clr


# class bufferCache: This class will handle all the functions of the buffer cache like it does in the operating system.
# hash_queues (default 4): specified no. of slots to create for hash_queue. 4 is easy to visualize
# max_buffers (default 10): specifies how many buffers are there in the simulation
# in the beginning buffers are added to the hash_queue randomly (i.e. random blocks from the secondary memory)
# this is done to bootstrap the process of simulation.

class BufferCache:
    def __init__(self, no=4, max_buffers=3, block_range=20, shuffle=False):
        self.hash_queue = HashQueue(no, max_buffers, block_range, shuffle)
        self.delayed_write_list = []
        self.any_buffer_required = False
        self.this_buffer_required = False
        # buffer id, will be used by the scheduler to wake up processes waiting on a particular buffer number
        self.this_buffer_required_num = None
        self.any_awaited_count = 0
        self.clr = Clr()

    # function to print the buffer cache
    def __str__(self):
        res = str(self.hash_queue)

        return res

    # function to set this_buffer_required
    def set_this_buffer_required(self, val=False):
        self.this_buffer_required = val
        self.this_buffer_required_num = None

    # function to set any_buffer_required
    def set_any_buffer_required(self, val=False):
        self.any_buffer_required = val

    # function to get any_awaited_count
    def get_any_awaited_count(self):
        return self.any_awaited_count

    # function to set any_awaited_count
    def set_any_awaited_count(self, val=True):
        if val:
            self.any_awaited_count += 1
        elif self.any_awaited_count != 0:
            self.any_awaited_count -= 1

        self.any_awaited_count = val

    # function for scheduler to check if any buffer gets free
    def is_any_buffer_required(self):
        return self.any_buffer_required

    # function for scheduler to check if this buffer gets free
    # RETURN::
    #   -1 : no buffer freed which has some process sleeping on it
    #   self.this_buffer_required_num : return buffer no, if it got freed and have process sleeping on it
    def is_this_buffer_required(self):
        if not self.this_buffer_required:
            return -1
        return self.this_buffer_required_num

    def get_delayed_write_element(self):
        bfr = self.delayed_write_list[0]
        del self.delayed_write_list[0]
        return bfr

    def is_buffer_in_delayed_write_list(self):
        if len(self.delayed_write_list) > 0:
            return True
        else:
            return False

    # function to check whether a block number is valid or not.
    def is_block_no_valid(self, blk_no):
        if self.hash_queue.block_range > blk_no >= 0:
            return True
        else:
            return False

    # getblk algorithm
    # INPUT::
    #   blk_no : block number to search in the cache
    # RETURN:
    #   temp_bfr : locked buffer which is present in HQ and not busy
    #   False : When there is an error
    #   'buffer_busy' : if buffer is present in HQ but is being used by someone else
    #   'free_list_empty' : if free list is empty
    #   temp_free_bfr : buffer which is
    def getblk(self, blk_no):
        while True:                             # while buffer not found
            temp_bfr = self.hash_queue.search_block_in_hq(blk_no)
            if temp_bfr:        # if block is present in the hash queue
                if temp_bfr.is_locked():                # SCENARIO 5
                    temp_bfr.set_awaited()
                    return "buffer_busy"                # if buffer is locked put the current process to sleep
                temp_bfr.set_locked()                   # SCENARIO 1
                if self.hash_queue.rem_buffer_from_free_list(temp_bfr):
                    return temp_bfr                     # buffer returned
                return False        # ERROR

            else:               # block not in hash queue
                if self.hash_queue.is_free_list_empty():        # SCENARIO 4 (free list empty)
                    self.set_any_awaited_count()
                    return "free_list_empty"            # put process to sleep on any buffer free event

                temp_free_bfr = self.hash_queue.rem_buffer_from_free_list()

                if temp_free_bfr.is_delayed_write():             # SCENARIO 3 (buffer marked delayed write)
                    # INCOMPLETE // can add the feature to write actual data to disk for better visualization

                    self.delayed_write_list.append(temp_free_bfr)
                    str_res = f"{self.clr.CYAN}[GETBLK]{self.clr.END} Buffer " + str(temp_free_bfr.get_buf_num())
                    str_res += " (contains Block " + str(temp_free_bfr.get_block_number())
                    str_res += ") is marked as delayed write.\n"
                    str_res += f"{self.clr.BLUE}[KERNEL]{self.clr.END} Starting ASYNC WRITE TO DISK"
                    print(str_res)
                    continue                # back to while loop for searching for new free block

                # SCENARIO 2 (Found a free buffer in free list)
                self.hash_queue.rem_buffer_from_hash_queue(temp_free_bfr)    # remove from old hash queue
                temp_free_bfr.set_status(True, False, False)
                temp_free_bfr.set_block_number(blk_no)
                temp_free_bfr.set_locked()
                self.hash_queue.add_at_end_hq(blk_no, temp_free_bfr)
                return temp_free_bfr

    # brelse algorithm
    # INPUT::
    #   bfr : locked buffer
    # RETURN::
    #   None
    def brelse(self, bfr):
        # wake up all processes waiting on this buffer
        if bfr.get_awaited():
            self.this_buffer_required_num = bfr.get_buf_num()
            self.this_buffer_required = True
            pass
        # wake up all processes waiting on any
        if self.any_awaited_count:
            self.any_buffer_required = True

        if bfr.is_old():            # if buffer is old (i.e. after performing async write on disk`)
            self.hash_queue.add_to_free_list_beg(bfr)
        else:
            self.hash_queue.add_to_free_list_end(bfr)
