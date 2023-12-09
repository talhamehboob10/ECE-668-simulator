import threading
import tkinter as tk
from tkinter import ttk


class Instruction:
    def __init__(self, name, destination='None', source1='None', source2='None'):
        self.name = name
        self.destination = destination
        self.source1 = source1
        self.source2 = source2
        self.started = False
        self.executed = False
        self.written = False


# Instruction status properties
########################################
# number: the sequence number or identifier of the instruction
# op: represents the operation type or instruction type (e.g., 'ADD', 'LOAD')
# start_time: the cycle or time at which the instruction starts its execution
# execute_time: the execution duration or the specific cycle when the instruction is being executed
# issued: a boolean flag indicating whether the instruction has been issued or issued in the pipeline
# executed: a boolean flag showing whether the instruction has reached the execution stage
class InsCondition:
    def __init__(self, number, op, execute_time, start_time=0):
        self.number = number
        self.op = op
        self.start_time = start_time
        self.execute_time = execute_time
        self.issued = False
        self.executed = False
        self.assigned_station = ''
        self.written = False


# Reservation Station Class
########################################
# op: the type of operation that the reservation station can perform
# curr_op: current operation being executed by this reservation station
# number: the unique identifier or sequence number for the reservation station
# qj and qk: the identifiers for the reservation stations that will produce the source operands
# vj and vk: the actual values of the source operands
# busy: a boolean flag indicating whether the reservation station is currently busy
# A: Address
class ReservationStation:
    def __init__(self, Op, number, curr_op='', Qj='', Qk='', Vj='', Vk='', Busy=False, A=''):
        self.Op = Op
        self.op_type = curr_op
        self.number = number
        self.qj = Qj
        self.qk = Qk
        self.vj = Vj
        self.vk = Vk
        self.busy = Busy
        self.address = A
        self.started_time = ''
        self.result = ''
        self.assigned_instruction = Instruction('None')

    def make_available(self):
        self.busy = False
        self.op_type = ''
        self.qj = ''
        self.qk = ''
        self.vj = ''
        self.vk = ''
        self.address = ''
        self.started_time = ''
        self.result = ''
        self.assigned_instruction = Instruction('None')


class Register:
    def __init__(self, name, val=0):
        self.name = name
        self.val = val


# Find Available Reservation Station
########################################
# This is designed to determine the availability of reservation stations
# If an available reservation station is found, the function returns its index.
# If no available reservation station is found for the given operation type, return 0
# If a bad operand is given, return -1.
def available_res_station(op):
    if op == 'L.D':
        for i in range(station_distribution.get("LD.D")[0], station_distribution.get("LD.D")[1] + 1):
            if not reservation_station_list[i].busy:
                return i
        return 0
    elif op == 'ADD.D':
        for i in range(station_distribution.get("ADD.D")[0], station_distribution.get("ADD.D")[1] + 1):
            if not reservation_station_list[i].busy:
                return i
        return 0
    elif op == 'SUB.D':
        for i in range(station_distribution.get("SUB.D")[0], station_distribution.get("SUB.D")[1] + 1):
            if not reservation_station_list[i].busy:
                return i
        return 0
    elif op == 'DIV.D':
        for i in range(station_distribution.get("DIV.D")[0], station_distribution.get("DIV.D")[1] + 1):
            if not reservation_station_list[i].busy:
                return i
        return 0
    elif op == 'MUL.D':
        for i in range(station_distribution.get("MUL.D")[0], station_distribution.get("MUL.D")[1] + 1):
            if not reservation_station_list[i].busy:
                return i
        return 0
    # Error case, bad op
    else:
        return -1


# User cycle setting
def set_cycles():
    print("Default delay for each instruction type:")
    print("L.D: 2\nADD.D: 2\nSUB.D 2\nDIV.D: 40\nMUL.D 10")
    print("For default delay values, type 'd' and hit enter")
    print("For custom delay options, type 'c' and hit enter\n")

    while True:
        user_in = input("Delay option: ")

        if user_in == 'c' or user_in == 'd':
            break
        else:
            print("Please type either 'd' for default delay or 'c' to set custom delay")

    if user_in == 'd':
        cycles = {'L.D': 2, 'ADD.D': 2, 'SUB.D': 2, 'DIV.D': 40, 'MUL.D': 10}
    else:
        options = {"LD.D": False, "ADD.D": False, "SUB.D": False, "DIV.D": False, "MUL.D": False}
        options_confirmed = options["LD.D"] & options["ADD.D"] & options["SUB.D"] & options["DIV.D"] & options["MUL.D"]
        val_input = None
        while not options_confirmed:
            for op_type in options:

                if not options[op_type]:
                    if op_type == "LD.D":
                        ld_input = input("Enter delay for LD.D: ")
                        val_input = ld_input
                    elif op_type == "ADD.D":
                        add_input = input("Enter delay for ADD.D: ")
                        val_input = add_input
                    elif op_type == "SUB.D":
                        sub_input = input("Enter delay for SUB.D: ")
                        val_input = sub_input
                    elif op_type == "DIV.D":
                        div_input = input("Enter delay for DIV.D: ")
                        val_input = div_input
                    elif op_type == "MUL.D":
                        mul_input = input("Enter delay for MUL.D: ")
                        val_input = mul_input

                    try:
                        int(val_input)
                    except ValueError:
                        print(f"Please enter postive integer value for {op_type} delay")
                        break
                    if int(val_input) < 0:
                        print(f"Please enter positive integer value for {op_type} delay")
                        break
                    elif val_input == '-0':
                        print(f"Please enter positive integer value for {op_type} delay")
                        break
                    options[op_type] = True
            options_confirmed = options["LD.D"] & options["ADD.D"] & options["SUB.D"] & options["DIV.D"] & options[
                "MUL.D"]
        cycles = {'L.D': int(ld_input), 'ADD.D': int(add_input), 'SUB.D': int(sub_input), 'DIV.D': int(div_input),
                  'MUL.D': int(mul_input)}

    return cycles


# User reservation setting
def set_reservation_count(max_stat):
    print("\nDefault distribution of Reservation Stations:")
    print("L.D: 3\nADD.D: 2\nSUB.D 1\nDIV.D: 1\nMUL.D 1")
    print("For default reservation station distribution, type 'd' and hit enter")
    print("For custom arrangement, type 'c' and hit enter\n")

    stations_left = max_stat

    while True:
        user_in = input("Configuration option: ")

        if user_in == 'c' or user_in == 'd':
            break
        else:
            print("Please type either 'd' for default distribution or 'c' to set custom configuration")

    if user_in == 'd':
        stations_dict = {"LD.D": [1, 3], "ADD.D": [4, 5],
                         "SUB.D": [6, 6], "DIV.D": [7, 7],
                         "MUL.D": [8, 8]}
        max_stat = stations_dict.get("MUL.D")[1]
    else:
        options = {"LD.D": False, "ADD.D": False, "SUB.D": False, "DIV.D": False, "MUL.D": False}
        options_confirmed = options["LD.D"] & options["ADD.D"] & options["SUB.D"] & options["DIV.D"] & options[
            "MUL.D"]
        val_input = None
        while not options_confirmed:
            for op_type in options:

                # Check the op type
                if not options[op_type]:
                    if op_type == "LD.D":
                        ld_input = input("Enter amount for LD.D: ")
                        val_input = ld_input
                    elif op_type == "ADD.D":
                        add_input = input("Enter amount for ADD.D: ")
                        val_input = add_input
                    elif op_type == "SUB.D":
                        sub_input = input("Enter amount for SUB.D: ")
                        val_input = sub_input
                    elif op_type == "DIV.D":
                        div_input = input("Enter amount for DIV.D: ")
                        val_input = div_input
                    elif op_type == "MUL.D":
                        mul_input = input("Enter amount for MUL.D: ")
                        val_input = mul_input

                    # Good value?
                    try:
                        int(val_input)
                    except ValueError:
                        print(f"Please enter positive integer value for amount of {op_type} stations")
                        break
                    if int(val_input) < 0:
                        print(f"Please enter positive integer value for amount of {op_type} stations")
                        break
                    elif val_input == '-0':
                        print(f"Please enter positive integer value for amount of {op_type} stations")
                        break

                    # Got a good value, move to next op type
                    options[op_type] = True
                    val_input = int(val_input)
                    stations_left = stations_left - val_input
                    print(f"Stations left: {stations_left}")

            # Check if we can leave the while loop
            options_confirmed = options["LD.D"] & options["ADD.D"] & options["SUB.D"] & options["DIV.D"] & options[
                "MUL.D"]

        # Finished the loop, options set
        if stations_left > 0:
            max_stat = max_stat - stations_left

        # Set to ints
        ld_input = int(ld_input)
        add_input = int(add_input)
        sub_input = int(sub_input)
        div_input = int(div_input)
        mul_input = int(mul_input)
        # Comments next to bounds shows how default is distributed
        ld_start = 1  # 1
        ld_end = ld_input  # 2
        add_start = ld_end + 1  # 3
        add_end = ld_end + add_input  # 5
        sub_start = add_end + 1  # 6
        sub_end = add_end + sub_input  # 8
        div_start = sub_end + 1  # 9
        div_end = sub_end + div_input  # 9
        mul_start = div_end + 1  # 10
        mul_end = div_end + mul_input  # 10

        stations_dict = {"LD.D": [ld_start, ld_end], "ADD.D": [add_start, add_end],
                         "SUB.D": [sub_start, sub_end], "DIV.D": [div_start, div_end],
                         "MUL.D": [mul_start, mul_end]}

    # Done, return the default amount or the custom amount
    return stations_dict, max_stat


# Read the instructions file
def read_instructions(instruction_lines):
    for inst in instruction_lines:
        # remove tabs from the imported text line
        inst = inst.replace('\t', '')
        inst = inst.replace(' ', '')

        # Find the end of the operation type in the instruction
        i = 0
        while not (inst[i - 1] == '.' and inst[i] == 'D'):
            i += 1
        i += 1
        op = str(inst[1:i])  # Extract the operation type (e.g., 'L.D', 'ADD.D')

        # Find the end of the first operand
        j = i + 1
        while inst[j] != ',':
            j += 1
        op1 = str(inst[i:j])  # Extract the first operand
        j += 1

        # Check if the next character is a digit, indicating a load instruction
        if '9' >= inst[j] >= '0':
            # Parse load instruction
            i = j
            j = i + 1
            while inst[j] != '(':
                j += 1
            op3 = str(inst[i:j])  # Extract the immediate value (for load instruction)

            # Find the register operand for load instruction
            i = j + 1
            j = i + 1
            while inst[j] != ')':
                j += 1
            op2 = str(inst[i:j])
            temp = op1
            op1 = op2
            op2 = temp
        else:
            # Parse ALU instruction (like 'ADD.D', 'SUB.D')
            i = j
            j = i + 1
            while inst[j] != ',':
                j += 1
            op2 = str(inst[i:j])
            j += 1
            i = j
            while inst[j] != '\n':
                j += 1
            op3 = str(inst[i:j])
        # Create an instruction object with the parsed data and add it to the list
        instructions.append(Instruction(op, op1, op2, op3))
    # Return the list of instruction objects
    return instructions


# GUI Function 1: Single step
def single_step():
    global tree_ins_state
    global tree_Qi
    global tree_r_s_state
    global basic_time
    global cur_started_instructions
    global reservation_station_list
    global inst_labels
    global instructions
    global regs_in_use
    global timer
    text_1.set('unrefreshed')
    # Timer jump
    basic_time += 1
    var.set(basic_time)

    qj_ready = False
    qk_ready = False

    # If not issued, then go sequentially to the next
    if cur_started_instructions < len(inst_labels):
        # Get the name of the operation (E.G. LD, ADD, ...)
        op_name = inst_labels[cur_started_instructions].op
        # Is there a reservation station of this type available?
        res_station_id = available_res_station(op_name)

        if res_station_id > 0:
            # Yes there is a station available
            # Next, get the current instruction
            cur_instruction = instructions[cur_started_instructions]
            # Update the reservation station to indicate taken
            reservation_station_list[res_station_id].busy = True
            reservation_station_list[res_station_id].op_type = op_name
            reservation_station_list[res_station_id].started_time = basic_time
            reservation_station_list[res_station_id].assigned_instruction = cur_instruction
            inst_labels[cur_started_instructions].issued = True
            inst_labels[cur_started_instructions].assigned_station = res_station_id

            if op_name != "L.D":
                if regs_in_use[cur_instruction.source1] == 0:
                    # First source available, get the value
                    reservation_station_list[res_station_id].vj = registers[cur_instruction.destination]
                    # Set the qj back to 0 to indicate it is not waiting (signals ready for execute for this source)
                    reservation_station_list[res_station_id].qj = 0
                    qj_ready = True
                else:
                    reservation_station_list[res_station_id].qj = regs_in_use[cur_instruction.source1]

                # Check if the first source register qj is being used by another executing instruction
                if regs_in_use[cur_instruction.source2] == 0:
                    # First source available, get the value
                    reservation_station_list[res_station_id].vk = registers[cur_instruction.destination]
                    # Set the qk back to 0 to indicate it is not waiting (signals ready for execute for this source)
                    reservation_station_list[res_station_id].qk = 0
                    qk_ready = True
                else:
                    reservation_station_list[res_station_id].qk = regs_in_use[cur_instruction.source2]
                regs_in_use[
                    cur_instruction.destination] = f"{reservation_station_list[res_station_id].Op}{reservation_station_list[res_station_id].number}"

                #  L.D operations
            else:
                # Example format F6: LD2
                regs_in_use[
                    cur_instruction.source1] = f"{reservation_station_list[res_station_id].Op}{reservation_station_list[res_station_id].number}"

            cur_started_instructions += 1

    # Ready to shift to execution
    if qj_ready and qk_ready:
        inst_labels[cur_started_instructions].start_time = basic_time

    # Execution
    for res_station in range(1, max_stations + 1):

        if reservation_station_list[res_station].busy is True:

            if reservation_station_list[res_station].started_time == basic_time - 1:
                for j in range(num_of_instructions):
                    if inst_labels[j].assigned_station == res_station:
                        inst_labels[j].executed = True
                        break
                # Load the instruction
                if reservation_station_list[res_station].Op == 'L.D' and reservation_station_list[res_station].qj == 0:
                    # Calculate the correct destination
                    reservation_station_list[res_station].address = str(reservation_station_list[res_station].vj) + '+' + str(
                        reservation_station_list[res_station].address)
                    # Get the data into result
                    reservation_station_list[res_station].result = 'Mem' + '[' + reservation_station_list[res_station].address + ']'
                # ALU operations
                elif reservation_station_list[res_station].qj == 0 and reservation_station_list[res_station].qk == 0:
                    if reservation_station_list[res_station].op_type == 'ADD.D':
                        reservation_station_list[res_station].result = str(reservation_station_list[res_station].vj) + '+' + str(
                            reservation_station_list[res_station].vk)
                    if reservation_station_list[res_station].op_type == 'SUB.D':
                        reservation_station_list[res_station].result = str(reservation_station_list[res_station].vj) + '-' + str(
                            reservation_station_list[res_station].vk)
                    if reservation_station_list[res_station].op_type == 'MUL.D':
                        reservation_station_list[res_station].result = str(reservation_station_list[res_station].vj) + '*' + str(
                            reservation_station_list[res_station].vk)
                    if reservation_station_list[res_station].op_type == 'DIV.D':
                        reservation_station_list[res_station].result = str(reservation_station_list[res_station].vj) + '/' + str(
                            reservation_station_list[res_station].vk)

            # Execution -> Write Back
            elif reservation_station_list[res_station].started_time == basic_time - \
                    delay_cycles[reservation_station_list[res_station].op_type]:

                # Loop the instructions and check if they are ready to write back
                for j in range(num_of_instructions):
                    if inst_labels[j].assigned_station == res_station:
                        inst_labels[j].written = True
                        break

                # Cycle through the destination table and update the corresponding destination register
                for reg in regs_in_use:
                    # If waiting for the results
                    if regs_in_use[reg] == f"{reservation_station_list[res_station].Op}{reservation_station_list[res_station].number}":
                        registers[reg] = reservation_station_list[res_station].result
                        # Make the designation register ready to read from
                        regs_in_use[reg] = 0
                        break

                reservation_station_list[res_station].make_available()

    items = tree_ins_state.get_children()
    for item in items:
        tree_ins_state.delete(item)
    for res_station in range(num_of_instructions):
        x = inst_labels[res_station]
        tree_ins_state.insert('', x.number, text='Instr' + str(x.number), values=(
            x.op, x.start_time, x.execute_time, x.issued, x.executed, x.assigned_station, x.written))
    items = tree_r_s_state.get_children()
    for item in items:
        tree_r_s_state.delete(item)
    for res_station in range(1, len(reservation_station_list)):
        x = reservation_station_list[res_station]
        tree_r_s_state.insert('', res_station, text='Res Station' + str(res_station), values=(
            x.Op, x.op_type, x.number, x.qj, x.qk, x.vj, x.vk, x.busy, x.address, x.started_time, x.result))
    items = tree_Qi.get_children()
    for item in items:
        tree_Qi.delete(item)
    p = []
    for x in regs_in_use:
        p.append(regs_in_use[x])
    tree_Qi.insert('', 1, values=tuple(p))


# GUI function 2: Refresh
def refresh():
    global tree_ins_state
    global tree_Qi
    global tree_r_s_state
    global inst_labels
    global basic_time
    global reservation_station_list
    global regs_in_use
    text_1.set('refreshed')
    basic_time = 0
    var.set(0)
    inst_labels = [InsCondition(i, instructions[i].name, delay_cycles[instructions[i].name]) for i in
                   range(num_of_instructions)]
    for i in range(1, len(reservation_station_list)):
        reservation_station_list[i].make_available()
    for x in regs_in_use:
        regs_in_use[x] = 0
    items = tree_ins_state.get_children()
    for item in items:
        tree_ins_state.delete(item)
    for i in range(num_of_instructions):
        x = inst_labels[i]
        tree_ins_state.insert('', x.number, text='Inst' + str(x.number), values=(
            x.op, x.start_time, x.execute_time, x.issued, x.executed, x.assigned_station, x.written))
    items = tree_r_s_state.get_children()
    for item in items:
        tree_r_s_state.delete(item)
    for i in range(1, len(reservation_station_list)):
        x = reservation_station_list[i]
        tree_r_s_state.insert('', i, text='Res Station' + str(i), values=(
            x.Op, x.op_type, x.number, x.qj, x.qk, x.vj, x.vk, x.busy, x.address, x.started_time, x.result))
    items = tree_Qi.get_children()
    for item in items:
        tree_Qi.delete(item)
    p = []
    for x in regs_in_use:
        p.append(regs_in_use[x])
    tree_Qi.insert('', 1, values=tuple(p))


# ???
def unrefresh():
    global timer
    if text_1.get() == 'unrefreshed':
        single_step()
        timer.cancel()
        timer = threading.Timer(1, unrefresh)
        timer.start()


# GUI function 3: Automatic execution of the GUI (single steps by itself)
def automatic():
    text_1.set('unrefreshed')
    i = 0
    while i < 50:
        if text_1.get() == 'unrefreshed':
            timer.start()
            i += 1
        else:
            break


if __name__ == "__main__":

    # This maps the names of registers to their corresponding numerical identifiers
    Regs = {'F0': 0, 'F2': 2, 'F4': 4, 'F6': 6, 'F8': 8, 'F10': 10, 'R2': 11, 'R3': 12, }
    # User input setup before start
    delay_cycles = set_cycles()
    # Reservation Station count, to be set by the following function (set by the user or set to default)
    max_stations = 10
    station_distribution, max_stations = set_reservation_count(max_stations)
    # Some variable initialization for readability
    instructions = []
    num_of_instructions = None

    # Start simulation
    print("Running simulation, open GUI when it appears")
    # Load Instructions
    ########################################
    try:
        ins = open('instructions1.txt')
    except BaseException:
        print('Cannot find the set of instructions！')
        exit(-1)
    else:
        # Split instructions from the .txt
        ins = ins.readlines()
        num_of_instructions = len(ins)
        # Iterate over each instruction string in the list of instructions
        instructions = read_instructions(ins)

    # Registers mapping
    registers = {'F0': 'F0', 'F2': 'F2', 'F4': 'F4', 'F6': 'F6', 'F8': 'F8', 'F10': 'F10', 'R2': 'R2', 'R3': 'R3'}

    # regs_in_use is a dictionary representing the register status indication table.
    # It indicates whether the value of each register is available for direct use
    # or if it needs to wait for a write-in from a reservation station.
    # Initially, all values are set to 0, indicating that all registers are available for use.
    regs_in_use = {
        'F0': 0,  # Status of register F0. 0 indicates it's available.
        'F2': 0,  # Status of register F2. 0 indicates it's available.
        'F4': 0,  # Status of register F4. 0 indicates it's available.
        'F6': 0,  # Status of register F6. 0 indicates it's available.
        'F8': 0,  # Status of register F8. 0 indicates it's available.
        'F10': 0,  # Status of register F10. 0 indicates it's available.
        'R2': 0,  # Status of register R2. 0 indicates it's available.
        'R3': 0,  # Status of register R3. 0 indicates it's available.
    }

    # inst_labels is a list that acts as an instruction state table.
    # It stores the state of each instruction in the form of `ins_condition` objects.

    inst_labels = [
        # Create an `ins_condition` object for each instruction.
        # `i` is the instruction number/index.
        # `instructions[i].name` fetches the name (type) of the instruction at index `i`.
        # `delay_cycles[instructions[i].name]` gets the number of delay cycles for the instruction
        # from the `delay_cycles` dictionary, using the instruction's name as the key.
        InsCondition(
            ins_num,  # Instruction number/index.
            instructions[ins_num].name,  # Name/type of the instruction.
            delay_cycles[instructions[ins_num].name]  # Delay cycles for the instruction.
        )
        for ins_num in range(num_of_instructions)  # Iterate over the first six instructions.
    ]

    # The first element is initialized as an empty string.
    reservation_station_list = ['']

    # Create reservation stations for load operations.
    # Reservation stations 1 to 2 are designated for 'L.D' (load double) operations.
    for i in range(station_distribution.get("LD.D")[0], station_distribution.get("LD.D")[1] + 1):
        reservation_station_list.append(ReservationStation('L.D', i))

    # Create reservation stations for addition and subtraction operations.
    # Reservation stations 3 to 5 are for 'ADD.D' (add double) operations.
    for i in range(station_distribution.get("ADD.D")[0], station_distribution.get("ADD.D")[1] + 1):
        reservation_station_list.append(ReservationStation('ADD.D', i))

    # Create reservation stations for subtraction operations
    for i in range(station_distribution.get("SUB.D")[0], station_distribution.get("SUB.D")[1] + 1):
        reservation_station_list.append(ReservationStation('SUB.D', i))

    # Create reservation stations for multiplication and division operations.
    # Reservation stations 6 to 7 are for 'DIV.D' (divide double) operations.
    for i in range(station_distribution.get("DIV.D")[0], station_distribution.get("DIV.D")[1] + 1):
        reservation_station_list.append(ReservationStation('DIV.D', i))

    for i in range(station_distribution.get("MUL.D")[0], station_distribution.get("MUL.D")[1] + 1):
        reservation_station_list.append(ReservationStation('MUL.D', i))

    # Initialize basic_time as a counter for the simulation's current time/cycle.
    basic_time = 0
    # Initialize cur_started_instructions to track the number of instructions that have issued execution.
    cur_started_instructions = 0

    timer = threading.Timer(1, unrefresh)

    window = tk.Tk()
    window.title('Tomasulo Simulator')
    window.geometry('1920x1080')
    text_1 = tk.StringVar()
    text_1.set('unrefreshed')
    label_1 = tk.Label(window, text='Instr Window', bg='skyblue', font=('Arial', 25), width=40, height=1)
    label_1.pack()
    tree_ins_state = ttk.Treeview(window)
    style = ttk.Style(window)
    tree_ins_state['columns'] = ('Instr Type', 'Instr Issue Time', 'Delay', 'IS_ISSUED', 'IS_EXEC',
                                 'Curr Instr Res Station', 'IS_WRBACK')
    tree_ins_state.column('Instr Type', width=100)
    tree_ins_state.column('Instr Issue Time', width=100)
    tree_ins_state.column('Delay', width=100)
    tree_ins_state.column('IS_ISSUED', width=100)
    tree_ins_state.column('IS_EXEC', width=100)
    tree_ins_state.column('Curr Instr Res Station', width=250)
    tree_ins_state.column('IS_WRBACK', width=100)
    tree_ins_state.heading('Instr Type', text='Instr Type')
    tree_ins_state.heading('Instr Issue Time', text='Instr Issue Time')
    tree_ins_state.heading('Delay', text='Delay')
    tree_ins_state.heading('IS_ISSUED', text='IS_ISSUED')
    tree_ins_state.heading('IS_EXEC', text='IS_EXEC')
    tree_ins_state.heading('Curr Instr Res Station', text='Curr Instr Res Station')
    tree_ins_state.heading('IS_WRBACK', text='IS_WRBACK')

    for i in range(num_of_instructions):
        x = inst_labels[i]
        tree_ins_state.insert('', x.number, text='Instr' + str(x.number),
                              values=(
                                  x.op, x.start_time, x.execute_time, x.issued, x.executed, x.assigned_station, x.written))

    tree_ins_state.pack()
    label_2 = tk.Label(window, text='Res Station', bg='skyblue', font=('Arial', 25), width=40, height=1)
    label_2.pack()
    tree_r_s_state = ttk.Treeview(window)
    tree_r_s_state['columns'] = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)

    for i in tree_r_s_state['columns']:
        tree_r_s_state.column(i, width=150)

    tree_r_s_state.column(3, width=70)
    tree_r_s_state.column(11, width=200)

    tree_r_s_state.heading(1, text='Res Station Type')
    tree_r_s_state.heading(2, text='Current Instr Type')
    tree_r_s_state.heading(3, text='#')
    tree_r_s_state.heading(4, text='qj')
    tree_r_s_state.heading(5, text='qk')
    tree_r_s_state.heading(6, text='vj')
    tree_r_s_state.heading(7, text='vk')
    tree_r_s_state.heading(8, text='Busy')
    tree_r_s_state.heading(9, text='Offset')
    tree_r_s_state.heading(10, text='Start Cycle')
    tree_r_s_state.heading(11, text='Result')
    style.configure("Treeview", font=('Arial', 17), rowheight=30)  # Set font size to 30

    for i in range(1, len(reservation_station_list)):
        x = reservation_station_list[i]
        tree_r_s_state.insert('', i, text='Res Station' + str(i), values=(
            x.Op, x.op_type, x.number, x.qj, x.qk, x.vj, x.vk, x.busy, x.address, x.started_time, x.result))

    # Reg Status
    tree_r_s_state.pack()
    label_3 = tk.Label(window, text='Reg Status', bg='skyblue', font=('Arial', 25), width=40, height=1)
    label_3.pack()
    tree_Qi = ttk.Treeview(window, show='headings', height=1)
    tree_Qi['columns'] = (1, 2, 3, 4, 5, 6, 7, 8)

    for i in tree_Qi['columns']:
        tree_Qi.column(i, width=100)

    tree_Qi.heading(1, text='F0')
    tree_Qi.heading(2, text='F2')
    tree_Qi.heading(3, text='F4')
    tree_Qi.heading(4, text='F6')
    tree_Qi.heading(5, text='F8')
    tree_Qi.heading(6, text='F10')
    tree_Qi.heading(7, text='R2')
    tree_Qi.heading(8, text='R3')
    tree_Qi.insert('', 1, values=(0, 0, 0, 0, 0, 0, 0, 0))
    tree_Qi.pack()

    # Buttons
    button_single_step = tk.Button(window, text='Step_By_Step', width=10, height=1, command=single_step)
    button_refresh = tk.Button(window, text='Refresh', width=10, height=1, command=refresh)
    button_automatic = tk.Button(window, text='AutoExe', width=10, height=1, command=automatic)
    button_single_step.pack()
    button_refresh.pack()
    button_automatic.pack()
    frame_1 = tk.Frame(window)
    label_0 = tk.Label(frame_1, text='ECE 668', font=('Arial', 25), width=15, height=2)
    label_0.pack(side=tk.LEFT)
    var = tk.IntVar()
    var.set(basic_time)
    label_01 = tk.Label(frame_1, text='Cycle：', font=('Arial', 25), width=11, height=1)
    label_02 = tk.Label(frame_1, textvariable=var, fg='red', font=('Arial', 30), width=11, height=1)
    label_02.pack(side=tk.RIGHT)
    label_01.pack(side=tk.RIGHT)
    frame_1.pack(fill=tk.BOTH, expand=tk.YES)
    window.mainloop()
