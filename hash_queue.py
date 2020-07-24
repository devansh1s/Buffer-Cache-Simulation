from buffer import Buffer
import random


# function to centre align strings to display output neatly
def centre_align(width, str1, str2):
    len1 = len(str1)
    len2 = len(str2)
    sm = len1 + len2
    diff = width - sm - 1
    buf = 0
    if diff % 2 != 0:
        buf = 1
    diff /= 2
    diff = int(diff)
    str1 += " " * diff + str2 + " " * (diff + buf) + "|"
    return str1


# function to add `|` at the end of the strings to display output neatly
def add_str_end(width, str1):
    len1 = len(str1)
    diff = width - len1 - 1
    str1 += " " * diff + "|"
    return str1


# function to tell whether a buffer is free or not
def is_buffer_free(bfr):
    status = bfr.get_status()
    if status["locked"]:  # if True -> locked
        return False
    else:
        return True


# function to tell whether a buffer is free or not
def is_buffer_valid(bfr):
    status = bfr.get_status()
    if status["valid"]:  # if True -> valid
        return True
    else:
        return False


# class HashQueue: implements the Hash queue for Buffer Cache
class HashQueue:
    # INPUT::
    #   no : no. of hash queues
    #   no_buffers: max number of buffers in the simulation
    def __init__(self, no=4, no_buffers=None, block_range=20, shuffle=False):
        self.no_of_hash_queues = no
        self.hash_queues = {}
        self._generate_hq(no)
        self.free_list_header = None
        self.no_free_buffers = 0
        self.block_range = block_range
        self.no_of_buffers = no_buffers
        if no_buffers is not None:
            self._generate_buffers(no_buffers, block_range, shuffle)

    # convenience function to print the hash queue
    def __str__(self):
        # making hash queue
        line_width = 140
        line = "-" * line_width
        res = line
        str1 = "| Hash Queue Header |"
        str2 = "Buffers in hash Queue with block number"
        res += "\n" + centre_align(line_width, str1, str2) + "\n" + line
        width = len("| Hash Queue Header |")
        str1 = "|"
        # value is of type buffer
        for key, value in self.hash_queues.items():

            str2 = str(key)
            new_line = centre_align(width, str1, str2)
            width = len(new_line)
            forward = "    "
            if value is None:  # when a hash queue is empty/ handling error
                forward += "EMPTY"
            else:
                if value.is_delayed_write():
                    forward += str(value.get_block_number()) + "(D) -->   "
                else:
                    forward += str(value.get_block_number()) + "   -->   "
                curr = value.get_hash_next()
                while curr != value:
                    if curr.is_delayed_write():
                        forward += str(curr.get_block_number()) + "(D) -->   "
                    else:
                        forward += str(curr.get_block_number()) + "   -->   "
                    curr = curr.get_hash_next()
            new_line += forward
            new_line = add_str_end(line_width, new_line)
            res += "\n" + new_line
        res += "\n" + line + "\n\n"

        # making free list
        res2 = line
        new_line = "| Free List Header  |"
        forward = "    "
        if self.free_list_header is not None:
            if self.free_list_header.is_delayed_write():
                forward += str(self.free_list_header.get_block_number()) + "(D) -->   "
            else:
                forward += str(self.free_list_header.get_block_number()) + "   -->   "
            curr = self.free_list_header.get_free_next()
            while curr != self.free_list_header:
                if curr.is_delayed_write():
                    forward += str(curr.get_block_number()) + "(D) -->   "
                else:
                    forward += str(curr.get_block_number()) + "   -->   "
                curr = curr.get_free_next()

        new_line += forward
        new_line = add_str_end(line_width, new_line)
        res2 += "\n" + new_line + "\n" + line + "\n\n"

        res += res2

        return res

    # function to generate buffers
    # INPUT::
    #   no: no. of buffers to generate
    def _generate_buffers(self, no, rng, shuffle):
        choices = list(range(rng))
        # testing / uncomment the following line after done testing
        if shuffle:
            random.shuffle(choices)
        for i in range(no):
            num = choices.pop()
            self.add_to_hq(num, i)

    # function to get buffer number from block number
    def get_buf_num_from_blk_num(self, blk_num):
        if 0 <= blk_num < self.block_range:
            temp_blk = self.search_block_in_hq(blk_num)
            buf_num = temp_blk.get_buf_num()
            return buf_num
        else:
            return False

    # function to check whether buffer is in free list or not
    # INPUT::
    #   bfr : buffer which is to be searched in the free list
    # RETURN::
    #   True : if buffer is present in the free list
    #   False : if buffer is not present in the free list
    def is_buffer_in_free_list(self, bfr):
        if self.free_list_header is not None:
            curr_buf = self.free_list_header
            if curr_buf == bfr:
                return True

            while curr_buf.get_free_next() != self.free_list_header:
                curr_buf = curr_buf.get_free_next()
                if curr_buf == bfr:
                    return True
            return False

    # function to remove buffer from free list
    # INPUT::
    #   bfr : buffer which is to be removed from free list
    # RETURN::
    #   True : if `bfr` is in free list it is removed from free list and True is returned
    #   free_bfr : if `bfr` is not in the free list i
    def rem_buffer_from_free_list(self, bfr=None):
        if bfr is not None:
            if self.is_buffer_in_free_list(bfr):
                curr_buf = self.free_list_header
                if curr_buf == bfr:
                    if self.no_free_buffers == 1:
                        self.free_list_header = None
                    else:
                        nxt = curr_buf.get_free_next()
                        prv = curr_buf.get_free_prev()
                        prv.set_free_next(nxt)
                        nxt.set_free_prev(prv)
                        self.free_list_header = nxt

                    curr_buf.set_free_next()  # remove links of current buffer
                    curr_buf.set_free_prev()  # remove links of current buffer
                    self.no_free_buffers -= 1
                    return True  # success

                while curr_buf.get_free_next() != self.free_list_header:
                    curr_buf = curr_buf.get_free_next()
                    if curr_buf == bfr:
                        nxt = curr_buf.get_free_next()
                        prv = curr_buf.get_free_prev()
                        prv.set_free_next(nxt)
                        nxt.set_free_prev(prv)
                        curr_buf.set_free_next()  # remove links of current buffer
                        curr_buf.set_free_prev()  # remove links of current buffer
                        self.no_free_buffers -= 1
                        return True
            return False

        else:  # case 2 : when `bfr` is not in free list
            curr_buf = self.free_list_header

            if curr_buf is None:
                return False        # ERROR

            if curr_buf.get_free_next() == curr_buf:  # only 1 element in free list
                self.free_list_header = None

            else:
                self.free_list_header = curr_buf.get_free_next()
                nxt = curr_buf.get_free_next()
                prv = curr_buf.get_free_prev()
                nxt.set_free_prev(prv)
                prv.set_free_next(nxt)

            curr_buf.set_free_prev()  # remove links of current buffer
            curr_buf.set_free_next()  # remove links of current buffer
            self.no_free_buffers -= 1
            return curr_buf

    # function to check if free list is empty
    # RETURN::
    #   True : free list is empty
    #   False: free list is not empty
    def is_free_list_empty(self):
        if self.free_list_header is None:
            return True
        return False

    # function to initialize the hash queue with the given no. of slots
    def _generate_hq(self, no):
        for i in range(no):
            self.hash_queues[i] = None

    # function to add a buffer to the free list's end
    def add_to_free_list_end(self, bfr):
        self.no_free_buffers += 1
        bfr.set_locked(False)           # unlock the buffer when it is being added to the free list
        if self.free_list_header is None:
            bfr.set_free_next(bfr)
            bfr.set_free_prev(bfr)
            self.free_list_header = bfr

        else:
            end = self.free_list_header.get_free_prev()
            bfr.set_free_next(self.free_list_header)
            bfr.set_free_prev(end)
            end.set_free_next(bfr)
            self.free_list_header.set_free_prev(bfr)

    # function to add a buffer to the free list's beginning
    def add_to_free_list_beg(self, bfr):
        self.no_free_buffers += 1
        bfr.set_locked(False)
        bfr.set_old(False)                      # remove `old` status
        bfr.set_buffer_delayed(False)           # remove `delayed write` status
        if self.free_list_header is None:
            bfr.set_free_next(bfr)
            bfr.set_free_prev(bfr)
            self.free_list_header = bfr

        else:
            first = self.free_list_header
            last = first.get_free_prev()
            bfr.set_free_next(first)
            bfr.set_free_prev(first.get_free_prev())
            first.set_free_prev(bfr)
            last.set_free_next(bfr)
            self.free_list_header = bfr

    # function to find if a given block number exists in the hash queue
    # INPUT::
    #   block_no: block no to be searched in the hash queue
    # RETURN::
    #   curr: buffer which contains the required block
    #   False: if block_no is not found in hash queue
    def search_block_in_hq(self, block_no):
        hash_no = block_no % self.no_of_hash_queues
        if self.hash_queues[hash_no] is not None:
            curr = self.hash_queues[hash_no]
            if curr.get_block_number() == block_no:
                return curr
            curr = curr.get_hash_next()
            while curr is not None and curr != self.hash_queues[hash_no]:
                if curr.get_block_number() == block_no:
                    return curr
                curr = curr.get_hash_next()

        return False  # block_no not found

    # function to add a given buffer at the end of hash queue
    def add_at_end_hq(self, block_no, temp_buffer):
        hash_no = block_no % self.no_of_hash_queues
        if self.hash_queues[hash_no] is None:
            temp_buffer.set_hash_next(temp_buffer)
            temp_buffer.set_hash_prev(temp_buffer)
            self.hash_queues[hash_no] = temp_buffer

        else:
            end = self.hash_queues[hash_no].get_hash_prev()
            temp_buffer.set_hash_prev(end)
            temp_buffer.set_hash_next(self.hash_queues[hash_no])
            end.set_hash_next(temp_buffer)
            self.hash_queues[hash_no].set_hash_prev(temp_buffer)

    # function to add a buffer to hash_queue
    # Incomplete (maybe)
    # can further implement to read files from disk using file names and add them to buffers
    # for simulation purpose we are simply assuming that a range of block numbers exists. eg. 0-100
    def add_to_hq(self, block_no, buf_num):
        if not self.search_block_in_hq(block_no):  # Buffer not present in the hash queue
            # call getblk algorithm to read the block_no into buffer and put it into hash queue & free list

            temp_buffer = Buffer(block_number=block_no)
            temp_buffer.set_buf_num(buf_num)
            temp_buffer.set_status(False, False, False)
            self.add_at_end_hq(block_no, temp_buffer)
            self.add_to_free_list_end(temp_buffer)

    # remove buffer from hash queue
    # INPUT::
    #   bfr : buffer which is to be removed from the hash queue
    # RETURN::
    #   True : successfully removed
    #   False : ERROR
    def rem_buffer_from_hash_queue(self, bfr):
        blk_num = bfr.get_block_number()
        hash_num = blk_num % self.no_of_hash_queues

        if self.hash_queues[hash_num] is None:  # ERROR
            return False

        # there is only 1 buffer in this hash queue then we'd empty this hash queue
        if bfr.get_hash_next() == bfr and bfr.get_hash_prev() == bfr:
            self.hash_queues[hash_num] = None
            bfr.set_hash_next()
            bfr.set_hash_prev()
            bfr.set_block_number()
            return True

        # if more than 1 buffers in the current hash queue, we'd simply remove it from this hash queue
        elif self.hash_queues[hash_num] == bfr:
            self.hash_queues[hash_num] = bfr.get_hash_next()
            bfr.get_hash_prev().set_hash_next(bfr.get_hash_next())
            bfr.get_hash_next().set_hash_prev(bfr.get_hash_prev())
            bfr.set_hash_next()
            bfr.set_hash_prev()
            bfr.set_block_number()
            return True

        else:
            return False

    # function to get buffer from buffer number
    # INPUT::
    #   bfr_num : buffer number whose buffer is to be fetched from the buffer list
    # RETURN::
    #   False: If buffer number is not present in the list / bfr_num is invalid
    def get_bfr_from_bfr_num(self, bfr_num):
        if bfr_num < 0:
            return False
        if bfr_num >= self.no_of_buffers:
            return False
        for i in range(self.no_of_hash_queues):
            curr = self.hash_queues[i]
            if curr is not None:
                if curr.get_buf_num() == bfr_num:
                    return curr
                curr = curr.get_hash_next()
                while curr != self.hash_queues[i]:
                    if curr.get_buf_num() == bfr_num:
                        return curr
                    curr = curr.get_hash_next()
            else:
                continue
