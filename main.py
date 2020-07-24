import time
from process_list import ProcessList
from buffer_cache import BufferCache
from buffer import Buffer
from threading import Thread
import random
from clr import Clr     # this if for color


# function to handles the delayed blocks using threading
def handle_delayed():
    global bfr_ch
    global prcs_lst
    global halt
    global _delayed_handler_lock
    while not halt:
        if bfr_ch.is_buffer_in_delayed_write_list():
            _delayed_handler_lock = True
            bfr = bfr_ch.get_delayed_write_element()
            print(f"{clr.BLUE}[KERNEL]{clr.END} Writing `delayed write` buffer (Buffer No : " +
                  str(bfr.get_buf_num()) + ") to disk")
            time.sleep(5)
            bfr.set_old(True)           # mark the buffer as `old`
            bfr_ch.brelse(bfr)          # call brelse for this buffer after it has been written to the disk
            # bfr.set_buffer_delayed(False)
            # bfr_ch.hash_queue.add_to_free_list_beg(bfr)
            print(f"{clr.BLUE}[KERNEL]{clr.END} `delayed write` of Buffer No. : " +
                  str(bfr.get_buf_num()) + " is complete!")
            _delayed_handler_lock = False
        time.sleep(0.5)
    # testing
    print(f"{clr.RED}Delay Handler is Exiting!{clr.END}")


# function which acts as a scheduler (handles all the wakeup events)
def scheduler():
    global bfr_ch
    global prcs_lst
    global halt
    global any_buffer_list
    global particular_buffer_map
    global _scheduler_lock
    while not halt:

        process_name = None
        was_awaited = False
        rest_of_processes = 0
        if bfr_ch.is_any_buffer_required():     # when any buffer gets free
            _scheduler_lock = True
            random.shuffle(any_buffer_list)
            process_name = any_buffer_list.pop()
            bfr_ch.set_any_buffer_required()
            bfr_ch.set_any_awaited_count(False)
            print(f"{clr.BLUE}[KERNEL]{clr.END} Waking up all the processes which were sleeping"
                  f" on `any buffer` gets free...")
            rest_of_processes = len(any_buffer_list)

        particular_buf_num = bfr_ch.is_this_buffer_required()
        if particular_buf_num >= 0:             # when a particular buffer gets free which was awaited
            if process_name is not None:
                ch = random.getrandbits(1)
                if ch == 0:
                    # this case shows the race condition
                    # processes wait for
                    _scheduler_lock = True
                    any_buffer_list.append(process_name)
                    random.shuffle(particular_buffer_map[particular_buf_num])
                    process_name = particular_buffer_map[particular_buf_num].pop()
                    bfr_ch.set_this_buffer_required()
                    was_awaited = True
                    rest_of_processes += len(particular_buffer_map[particular_buf_num])
                    print(f"{clr.BLUE}[KERNEL]{clr.END} Waking up all the processes which were"
                          f" sleeping on either `Buffer :" + str(particular_buf_num) +
                          "` gets free or `any buffer` gets free...")

            else:
                _scheduler_lock = True
                random.shuffle(particular_buffer_map[particular_buf_num])
                process_name = particular_buffer_map[particular_buf_num].pop()
                bfr_ch.set_this_buffer_required()
                was_awaited = True
                rest_of_processes = len(particular_buffer_map[particular_buf_num])
                print(f"{clr.BLUE}[KERNEL]{clr.END} Waking up all the processes which were sleeping on `Buffer :" +
                      str(particular_buf_num) + "` gets free...")

        if process_name is not None:
            # now go to the `process_name` and wake it up and do required work
            time.sleep(0.5)
            print(f"{clr.BLUE}[KERNEL]{clr.END} Scheduler chose Process: `" + str(process_name) + "` to be woken.")
            if rest_of_processes:
                time.sleep(0.5)
                print(f"{clr.BLUE}[KERNEL]{clr.END} All " + str(rest_of_processes) +
                      " other processes are going to sleep again...")
            block_no = prcs_lst.get_block_requested(process_name)
            process_request_type = prcs_lst.get_waiting_type(process_name)
            assign_buffer_to_process(block_no, process_name, process_request_type, was_awaited, is_repeat_req=True)
            _scheduler_lock = False
        time.sleep(0.5)
    # testing
    print(f"{clr.RED}Scheduler is Exiting!{clr.END}")


# function to assign buffer to process
def assign_buffer_to_process(block_no, process_name, request_type, was_awaited=False, is_repeat_req=False):
    res = bfr_ch.getblk(block_no)
    if not res:  # ERROR
        print(f"{clr.RED}There was some error!{clr.END}")
    else:
        if res == "buffer_busy":
            status, bfr = get_status(res, typ=request_type, block_num=block_no)
        else:
            status, bfr = get_status(res, typ=request_type)
        if status == -1 and bfr == -1:
            print(f"\n{clr.BLUE}[KERNEL]{clr.END} There was some error!!")
        else:
            if request_type == "read" and status == 1:
                print(f"{clr.CYAN}[GETBLK]{clr.END} Buffer : `" + str(bfr) + "` is assigned to Process : `" +
                      str(process_name) + "` for reading.")

            if request_type == "write" and status == 3:
                res.set_buffer_delayed()
                print(f"{clr.CYAN}[GETBLK]{clr.END} Buffer : `" + str(bfr) + "` is assigned to Process : `" +
                      str(process_name) + "` for writing.")
            waiting_type = None
            if status == 4:
                waiting_type = request_type
                if bfr is None:
                    if is_repeat_req:
                        time.sleep(0.5)
                        print(f"{clr.BLUE}[KERNEL]{clr.END} Freed buffer was marked as `delayed write`"
                              f" and Free list is now EMPTY!")
                        time.sleep(0.5)
                        print(f"{clr.BLUE}[KERNEL]{clr.END} Process : `" + str(process_name) +
                              "` is again going to sleep...")
                    else:
                        print(f"{clr.BLUE}[KERNEL]{clr.END} Free list is EMPTY.\n{clr.BLUE}[KERNEL]{clr.END}"
                              f" Process : `" + str(process_name) + "` is going to sleep...")
                    any_buffer_list.append(process_name)
                else:
                    print(f"{clr.CYAN}[GETBLK]{clr.END} Buffer : `" + str(bfr) + "` is locked." +
                          f"\n{clr.BLUE}[KERNEL]{clr.END} Process `" + str(process_name) + "` is going to sleep...")
                    particular_buffer_map[bfr].append(process_name)
            prcs_lst.all_processes[process_name].set_status(status, bfr, block_no, waiting_type)

    # this is to handle the case where this fn is called by a process which was previously asleep and just woke up
    # the following process had already incremented the wait counter of the awaited buffer and it again got incremented
    # so we have to decrement it to keep the awaited_count consistent with the no. of processes waiting on it
    if was_awaited:
        temp_bfr = bfr_ch.hash_queue.search_block_in_hq(block_no)
        temp_bfr.set_awaited(False)


# release buffer from process
def release_buffer_from_process(name):
    time.sleep(0.5)
    buf_num, status = prcs_lst.release_buffer(name)

    if 0 > status or status > 4:
        return
    if buf_num is not None:
        temp_buf = bfr_ch.hash_queue.get_bfr_from_bfr_num(buf_num)
    if not status == 4:
        bfr_ch.brelse(temp_buf)  # release buffer in buffer cache

    if status == 1:
        print(f"{clr.GREEN}(RELEASED){clr.END} Process " + str(name) + " finished reading and has released buffer " +
              str(buf_num) + ".")

    elif status == 2:
        print(f"{clr.GREEN}(RELEASED){clr.END} Process " + str(name) + " finished writing and has released buffer " +
              str(buf_num) + ".")

    elif status == 3:
        print(f"{clr.GREEN}(RELEASED){clr.END} Process " + str(name) + " finished writing and has released buffer " +
              str(buf_num) + ".")

    elif status == 4:
        if buf_num is None:
            print(f"{clr.BLUE}(CANCELLED){clr.END} Process " + str(name) +
                  " is no longer waiting for any buffer to become free.")
        else:
            temp_buf.set_awaited(False)
            print(f"{clr.BLUE}(CANCELLED){clr.END} Process " + str(name) + " is no longer waiting for buffer" +
                  str(buf_num) + " to become free.")


# function which reads the status of the getblk algo and returns status to the process accordingly
# RETURN::
#   -1, -1 : There was some error
#   0, None : process is idle
#   1, bfr_num : process is reading a block from bfr_num
#   3, bfr_num : process is (delayed) writing a buffer to disk block
#   4, bfr_num : when the process will wait for a particular block to get free
#   4, None : when the free list is empty and process will have to wait for any buffer to get free
def get_status(res, typ=None, block_num=None):
    if res == "buffer_busy":
        bfr_num = bfr_ch.hash_queue.get_buf_num_from_blk_num(block_num)
        return 4, bfr_num
    elif res == "free_list_empty":
        return 4, None
    elif isinstance(res, Buffer):
        if res.is_locked():
            bfr_num = res.get_buf_num()
            if typ == "read":
                return 1, bfr_num
            elif typ == "write":
                return 3, bfr_num
            elif typ == "release":
                return 0, None
        else:
            return -1, -1    # ERROR


# show_main_menu(): Function to display the main menu
# OUTPUT::
#   1. Show Hash Queue & Free List.
#   2. Print Process List.
#   3. Create new Process.
#   4. Delete a process.
#   5. Read a Block.
#   6. Write to a Block.
#   7. Release buffer / Cancel request for a process.
#   8. Exit Simulation.
def show_main_menu():
    while True:
        if _scheduler_lock or _delayed_handler_lock:
            time.sleep(0.5)
            continue
        menu_str = f"{clr.YELLOW}~" * 140 + f"{clr.END}\n"
        menu_str += f"{clr.YELLOW}|{clr.END}" + " " * 58 + f"{clr.BOLD}Buffer Cache Simulator{clr.BOLD}" + " " * 58 + \
                    f"{clr.YELLOW}|{clr.END}\n"
        menu_str += f"{clr.YELLOW}~" * 140 + f"{clr.END}\n"
        menu_str += "1. Show Hash Queue & Free List.\n2. Print Process List.\n3. Create new Process.\n" \
                    "4. Delete a process.\n5. Read a Block.\n6. Write to a block.\n" \
                    "7. Release buffer / Cancel Request for a process.\n8. Exit Simulation."
        print("\n" + menu_str)
        ch = 0
        while True:
            try:
                ch = int(input(f"{clr.YELLOW}Enter your choice:{clr.END} "))
                break
            except ValueError:
                print(f"{clr.RED}Please enter integer value, not string!{clr.END}")
                time.sleep(0.5)
                continue

        if ch == 1:                                                             # Show Hash Queue & Free List
            # display the entire Buffer Cache here. (Hash Queue, Free List)
            print(f"\n{clr.RED}Buffers marked as (D) are delayed write{clr.END}\n")
            print(bfr_ch)

        elif ch == 2:                                                           # print Process List
            print("")
            prcs_lst.print_process_list()

        elif ch == 3:                                                           # Create new Process
            while True:
                name = input(f"{clr.YELLOW}Enter the Name of the process to create: {clr.END}")
                if prcs_lst.add_process(name):
                    print(f"{clr.BLUE}[KERNEL]{clr.END}Process name already exists. Enter new name.")
                    time.sleep(0.5)

                else:
                    print(f"{clr.BLUE}[KERNEL]{clr.END} Process created successfully.")
                    break

        elif ch == 4:                                                           # Delete a process
            while True:
                name = input(f"{clr.YELLOW}Enter the Name of the process to delete (type `back`"
                             f" to go back to previous menu): {clr.END} ")
                if name == "back":
                    break
                if not prcs_lst.is_name_duplicate(name):
                    print(f"{clr.RED}Process with this name doesnt exist. Enter correct name.{clr.END}")
                    time.sleep(0.5)
                    continue

                release_buffer_from_process(name)
                if not prcs_lst.del_process(name):  # successfully deleted
                    print(f"{clr.GREEN}Process deleted successfully.{clr.END}")
                    time.sleep(0.5)
                    break

        elif ch == 5:                                                           # Read a Block
            while True:
                name = input(f"{clr.YELLOW}Enter name of the process to read block with:{clr.END} ")
                if prcs_lst.is_name_duplicate(name):
                    while True:
                        block_no = 0
                        while True:
                            try:
                                block_no = int(input(f"{clr.YELLOW}Enter block number to read:{clr.END} "))
                                break
                            except ValueError:
                                print(f"{clr.RED}Please enter integer value, not string!{clr.END}")
                                time.sleep(0.5)
                                continue

                        if bfr_ch.is_block_no_valid(block_no):
                            release_buffer_from_process(name)
                            assign_buffer_to_process(block_no, name, "read")

                            break  # break inner while loop

                        else:
                            print(f"{clr.RED}Please enter a valid Block number.{clr.END}")
                            time.sleep(0.5)

                    break  # break outer while loop
                else:
                    print(f"{clr.RED}Please enter a valid process name.{clr.END}")
                    time.sleep(0.5)

        elif ch == 6:                                                           # Write to a block
            while True:
                name = input(f"{clr.YELLOW}Enter name of the process to use for writing to a block "
                             f"(`back` to cancel):{clr.END} ")
                if name == "back":
                    break
                if prcs_lst.is_name_duplicate(name):
                    while True:
                        block_no = 0
                        while True:
                            try:
                                block_no = int(input(f"{clr.YELLOW}Enter name of the block to write to:{clr.END} "))
                                break
                            except ValueError:
                                print(f"{clr.RED}Please enter integer value, not string!{clr.END}")
                                time.sleep(0.5)
                                continue

                        if bfr_ch.is_block_no_valid(block_no):
                            release_buffer_from_process(name)
                            assign_buffer_to_process(block_no, name, "write")

                            break  # break inner while loop

                        else:
                            print(f"{clr.RED}Please enter a valid Block number.{clr.END}")
                            time.sleep(0.5)

                    break  # break outer while loop
                else:
                    print(f"{clr.RED}Please enter a valid process name.{clr.END}")
                    time.sleep(0.5)

        elif ch == 7:                                               # Release buffer / Cancel Request for a process.
            while True:
                name = input(f"{clr.YELLOW}Enter name of the process to release buffer for:{clr.END} ")
                if prcs_lst.is_name_duplicate(name):

                    if not prcs_lst.is_any_buffer_assigned(name):
                        print(f"{clr.YELLOW}Please enter name of a process which currently have some"
                              f" buffer assigned.{clr.END}")
                        time.sleep(0.5)
                        continue

                    release_buffer_from_process(name)
                    time.sleep(0.5)
                    break

                else:
                    print(f"{clr.RED}Please enter a valid process name.{clr.END}")
                    time.sleep(0.5)

        elif ch == 8:                                                           # Exit
            print(f"{clr.RED}\nExiting the Simulation.{clr.END}")
            time.sleep(1.5)
            break

        else:
            print(f"{clr.RED}Wrong Input. Please Try again!!{clr.END}")
            time.sleep(0.5)


# main program starts here
if __name__ == "__main__":

    # initialization of buffer
    _num_of_hash_queues = 4
    _num_of_buffers = 3
    _block_range = 20
    _no_of_processes = 3
    _shuffle = False
    any_buffer_list = []
    particular_buffer_map = {}
    # this is to delay the display of menu while scheduler or delayed write is printing
    _delayed_handler_lock = False
    _scheduler_lock = False
    for i in range(_num_of_buffers):
        particular_buffer_map[i] = []
    halt = False

    clr = Clr()
    prcs_lst = ProcessList(_no_of_processes)
    bfr_ch = BufferCache(_num_of_hash_queues, _num_of_buffers, _block_range, _shuffle)

    _delay_handler = Thread(target=handle_delayed)
    _scheduler = Thread(target=scheduler)

    _delay_handler.start()
    _scheduler.start()

    show_main_menu()
    halt = True

    #  wait for other threads to finish their execution
    _delay_handler.join()
    _scheduler.join()
