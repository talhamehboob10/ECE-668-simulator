import sys
import os
import time
import tkinter as tk
from tkinter import ttk
import threading

class instruction:
    def __init__(self, name, opr1='None', opr2='None', opr3='None'):
        self.name = name
        self.opr1 = opr1
        self.opr2 = opr2
        self.opr3 = opr3
        self.started = False
        self.executed = False
        self.written = False

class ins_condition:
    def __init__(self, number, op, execute_time, start_time=0):
        self.number = number
        self.op = op
        self.start_time = start_time
        self.execute_time = execute_time
        self.started = False
        self.executed = False
        self.ex_number = 'None'
        self.written = False

class reservation_station:
    def __init__(self, Op, number, curr_op='None', Qj='None', Qk='None', Vj='None', Vk='None', Busy=False, A='None'):
        self.Op = Op
        self.curr_op = curr_op
        self.number = number
        self.Qj = Qj
        self.Qk = Qk
        self.Vj = Vj
        self.Vk = Vk
        self.Busy = Busy
        self.A = A
        self.started_time = 'None'
        self.result = 'None'

    def finish_end(self):
        self.Busy = False
        self.curr_op = 'None'
        self.Qj = 'None'
        self.Qk = 'None'
        self.Vj = 'None'
        self.Vk = 'None'
        self.A = 'None'
        self.started_time = 'None'
        self.result = 'None'

class register:
    def __init__(self, name, val=0):
        self.name = name
        self.val = val

def avai_res_station(op):
    if op == 'L.D':
        for i in range(1, 3):
            if not Reservation_station_state[i].Busy:
                return i
    elif op in ['ADD.D', 'SUB.D']:
        for i in range(3, 6):
            if not Reservation_station_state[i].Busy:
                return i
    elif op == 'DIV.D':
        for i in range(6, 8):
            if not Reservation_station_state[i].Busy:
                return i
    elif op == 'MUL.D':
        for i in range(8, 10):
            if not Reservation_station_state[i].Busy:
                return i
    else:
        return -1


# This maps the names of registers to their corresponding numerical identifiers

delay_cycles = {'L.D': 2, 'ADD.D': 3, 'SUB.D': 3, 'DIV.D': 40, 'MUL.D': 10}

# Load Instructions
try:
    ins = open('instructions.txt')
except BaseException:
    print('Cannot find the set of instructions!')
    os._exit(0)

ins = ins.readlines()
num_of_instructions = len(ins)
instructions = []

for x in ins:
    x = x.replace('\t', '')
    x = x.replace(' ', '')

    i = 0
    while not (x[i - 1] == '.' and x[i] == 'D'):
        i += 1
    i += 1
    op = str(x[1:i])

    j = i + 1
    while x[j] != ',':
        j += 1
    op1 = str(x[i:j])
    j += 1

    if x[j] <= '9' and x[j] >= '0':
        i = j
        j = i + 1
        while x[j] != '(':
            j += 1
        op3 = str(x[i:j])

        i = j + 1
        j = i + 1
        while x[j] != ')':
            j += 1
        op2 = str(x[i:j])
        temp = op1
        op1 = op2
        op2 = temp
    else:
        i = j
        j = i + 1
        while x[j] != ',':
            j += 1
        op2 = str(x[i:j])
        j += 1
        i = j
        while x[j] != '\n':
            j += 1
        op3 = str(x[i:j])

    instructions.append(instruction(op, op1, op2, op3))

Regs = {'F0': 0, 'F2': 2, 'F4': 4, 'F6': 6, 'F8': 8, 'F10': 10, 'R2': 11, 'R3': 12}


Qi = {'F0': 0, 'F2': 0, 'F4': 0, 'F6': 0, 'F8': 0, 'F10': 0, 'R2': 0, 'R3': 0}

Instruction_state = [
    ins_condition(
        i,
        instructions[i].name,
        delay_cycles[instructions[i].name]
    )
    for i in range(8)
]

Reservation_station_state = ['']

for i in range(1, 3):
    Reservation_station_state.append(reservation_station('L.D', i))

for i in range(3, 6):
    Reservation_station_state.append(reservation_station('ADD.D', i))

for i in range(6, 8):
    Reservation_station_state.append(reservation_station('DIV.D', i))

for i in range(8, 10):
    Reservation_station_state.append(reservation_station('MUL.D', i))

basic_time = 0
cur_started_instructions = 0
