class Buffer:
    def __init__(self, block_number=None):
        # self.deviceNumber = None  # isn't required in the simulation
        self.buffer_num = None
        self.block_number = block_number  # to uniquely identify the block from the secondary storage
        self.data = None        # data contained in the buffer
        self.hash_next = None   # pointer to the next buffer in the hash queue
        self.hash_prev = None   # pointer to the previous buffer in the hash queue
        self.free_next = None   # pointer to the next buffer in the free list of buffers
        self.free_prev = None   # pointer to the previous buffer in the free list of buffers
        self.status = {
            "locked": False,
            # valid/invalid flag isn't required because no I/O is taking place in simulation
            # "valid": False,
            "delayed": False,
            # kernel R/W isn't required because in simulation
            # "kernel_read_write": False,
            "awaited": False,
            "awaited_count": 0,
            # when a buffer is marked old, it'll mean that async delayed write is complete and
            # current buffer is needed to be added at the beginning of the free list
            "old": False
        }     # status of the buffer

    # function to set a buffer status as awaited
    def set_awaited(self, _await=True):
        if _await:
            self.status["awaited_count"] += 1
        elif self.status["awaited_count"] != 0:
            self.status["awaited_count"] -= 1
        if self.status["awaited_count"] == 0:
            self.status["awaited"] = False
        else:
            self.status["awaited"] = True

    # getter function for old
    def is_old(self):
        return self.status["old"]

    # setter function for old
    def set_old(self, is_old=True):
        self.status["old"] = is_old

    # function to get a buffer await status
    def get_awaited(self):
        return self.status["awaited"]

    # function to set buffer number
    def set_buf_num(self, num):
        self.buffer_num = num

    # function to get buffer number
    def get_buf_num(self):
        return self.buffer_num

    # function to get the status of the buffer
    def get_status(self):
        return self.status

    # function to check whether buffer is locked/busy
    def is_locked(self):
        return self.status['locked']

    # function to set buffer as locked/busy
    def set_locked(self, lock=True):
        self.status['locked'] = lock

    # function to set the status of the buffer
    # def set_status(self, locked=False, delayed=False, awaited=False, old=False)
    def set_status(self, locked=False, delayed=False, awaited=False, old=False):
        self.status["locked"] = locked
        self.status["delayed"] = delayed
        self.status["awaited"] = awaited
        self.status["old"] = old

    # function to return status of delayed write of a buffer
    def is_delayed_write(self):
        return self.status["delayed"]

    # function to set status of delayed write of a buffer
    def set_buffer_delayed(self, delay=True):
        self.status['delayed'] = delay

    # function to get the block_number
    def get_block_number(self):
        return self.block_number

    # function to set the block_number
    def set_block_number(self, blk_num=None):
        self.block_number = blk_num

    # function to get the next buffer in hash queue
    def get_hash_next(self):
        return self.hash_next

    # function to get the previous buffer in hash queue
    def get_hash_prev(self):
        return self.hash_prev

    # function to set the next buffer in hash queue
    def set_hash_next(self, bfr=None):
        self.hash_next = bfr

    # function to set the previous buffer in hash queue
    def set_hash_prev(self, bfr=None):
        self.hash_prev = bfr

    # function to get the next buffer in free list
    def get_free_next(self):
        return self.free_next

    # function to get the previous buffer in free list
    def get_free_prev(self):
        return self.free_prev

    # function to set the next buffer in free list
    def set_free_next(self, bfr=None):
        self.free_next = bfr

    # function to set the previous buffer in free list
    def set_free_prev(self, bfr=None):
        self.free_prev = bfr
