import sys,os
import time
########################################
# Make sure you install the python3 version tkinter package on Ubuntu
# Don't do the regular version, it will break the entire thing, if you use Qt

import tkinter as tk
from tkinter import ttk

########################################

import threading


# Instruction Set
########################################
# opr1 to opr3 refers to  These represent operands for the instruction. 
# The use of three separate operand attributes implies that the instruction 
# can have up to three operands, which covers most instruction formats.
# name is simply the name of the instruction

########################################
class instruction:
    def __init__(self,name,opr1='None',opr2='None',opr3='None'):
        self.name=name
        self.opr1=opr1
        self.opr2=opr2
        self.opr3=opr3
        self.started=False
        self.executed=False
        self.written=False
    

# Instruction status properties
########################################
# number: the sequence number or identifier of the instruction
# op: represents the operation type or instruction type (e.g., 'ADD', 'LOAD')
# start_time: the cycle or time at which the instruction starts its execution
# execute_time: the execution duration or the specific cycle when the instruction is being executed
# started: a boolean flag indicating whether the instruction has been issued or started in the pipeline
# executed: a boolean flag showing whether the instruction has reached the execution stage
class ins_condition:
    def __init__(self,number,op,execute_time,start_time=0):
        self.number=number
        self.op=op
        self.start_time=start_time
        self.execute_time=execute_time
        self.started=False
        self.executed=False
        self.ex_number='None'
        self.written=False
    
# Reservation Station Class
########################################
# op: the type of operation that the reservation station can perform
# curr_op: current operation being executed by this reservation station
# number: the unique identifier or sequence number for the reservation station
# qj and qk: the identifiers for the reservation stations that will produce the source operands
# vj and vk: the actual values of the source operands
# busy: a boolean flag indicating whether the reservation station is currently busy
# A: a boolean flag indicating whether the reservation station is currently busy
class reservation_station:
    def __init__(self,Op,number,curr_op='None',Qj='None',Qk='None',Vj='None',Vk='None',Busy=False,A='None'):
        self.Op=Op
        self.curr_op=curr_op
        self.number=number
        self.Qj=Qj
        self.Qk=Qk
        self.Vj=Vj
        self.Vk=Vk
        self.Busy=Busy
        self.A=A
        self.started_time='None'
        self.result='None'
    def finish_end(self):
        self.Busy=False
        self.curr_op='None'
        self.Qj='None'
        self.Qk='None'
        self.Vj='None'
        self.Vk='None'
        self.A='None'
        self.started_time='None'
        self.result='None'
class register:
    def __init__(self,name,val=0):
        self.name=name
        self.val=val

# Find Available Reservation Station
########################################
# This is designed to determine the availability of reservation stations
# If an available reservation station is found, the function returns its index.
# If no available reservation station is found for the given operation type, 
# the function returns -1.
def avai_res_station(op):
    if op=='L.D':
        for i in range(1,3):
            if not Reservation_station_state[i].Busy:
                return i
    elif op=='ADD.D' or op=='SUB.D':
        for i in range(3,7):
            if not Reservation_station_state[i].Busy:
                return i
    elif op=='DIV.D' or op=='MUL.D':
        for i in range(7,9):
            if not Reservation_station_state[i].Busy:
                return i
    else:
        return -1

# Register mapping
########################################
# This maps the names of registers to their corresponding numerical identifiers
Regs={'F0':0,'F2':2,'F4':4,'F6':6,'F8':8,'F10':10,'R2':11,'R3':12,}


## TO-DO:
########################################
# This part can be changed based on user inputs
# We should give user the way how to define the delays they desired
# This part maps different instruction types to their corresponding delay times (or execution latencies)
delay_cycles={'L.D':2,'ADD.D':3,'SUB.D':3,'DIV.D':40,'MUL.D':10,}

# Load Instructions
########################################
try: 
    ins=open('instructions.txt')
except BaseException:
    print('сука блять, cannot find the set of instructions！')
    os._exit(0)

ins=ins.readlines()

# Count how many instructions are given in the file
########################################
# This could be used later, just in case
num_of_instructions=len(ins)

# Split instructions from the .txt
instructions=[]
# Iterate over each instruction string in the list of instructions
for x in ins:
    # remove tabs from the imported text line
    x=x.replace('\t','')
    x=x.replace(' ','')

    # Find the end of the operation type in the instruction
    i=0
    while not(x[i-1]=='.'and x[i]=='D'):
        i+=1
    i+=1
    op=str(x[1:i]) # Extract the operation type (e.g., 'L.D', 'ADD.D')

    # Find the end of the first operand
    j=i+1
    while x[j]!=',':
        j+=1
    op1=str(x[i:j]) # Extract the first operand
    j+=1

    # Check if the next character is a digit, indicating a load instruction
    if x[j]<='9' and x[j]>='0':
        # Parse load instruction
        i=j
        j=i+1
        while x[j]!='(':
            j+=1
        op3=str(x[i:j]) # Extract the immediate value (for load instruction)

        # Find the register operand for load instruction
        i=j+1
        j=i+1
        while x[j]!=')':
            j+=1
        op2=str(x[i:j])
        temp=op1
        op1=op2
        op2=temp
    else:
        # Parse ALU instruction (like 'ADD.D', 'SUB.D')
        i=j
        j=i+1
        while x[j]!=',':
            j+=1
        op2=str(x[i:j])
        j+=1
        i=j
        while x[j]!='\n':
            j+=1
        op3=str(x[i:j])
    # Create an instruction object with the parsed data and add it to the list
    instructions.append(instruction(op,op1,op2,op3))

# Registers mapping
registers={'F0':'F0','F2':'F2','F4':'F4','F6':'F6','F8':'F8','F10':'F10','R2':'R2','R3':'R3',}

# Qi is a dictionary representing the register status indication table.
# It indicates whether the value of each register is available for direct use
# or if it needs to wait for a write-in from a reservation station.
# Initially, all values are set to 0, indicating that all registers are available for use.
Qi = {
    'F0': 0,   # Status of register F0. 0 indicates it's available.
    'F2': 0,   # Status of register F2. 0 indicates it's available.
    'F4': 0,   # Status of register F4. 0 indicates it's available.
    'F6': 0,   # Status of register F6. 0 indicates it's available.
    'F8': 0,   # Status of register F8. 0 indicates it's available.
    'F10': 0,  # Status of register F10. 0 indicates it's available.
    'R2': 0,   # Status of register R2. 0 indicates it's available.
    'R3': 0,   # Status of register R3. 0 indicates it's available.
}

# Instruction_state is a list that acts as an instruction state table.
# It stores the state of each instruction in the form of `ins_condition` objects.

Instruction_state = [
    # Create an `ins_condition` object for each instruction.
    # `i` is the instruction number/index.
    # `instructions[i].name` fetches the name (type) of the instruction at index `i`.
    # `delay_cycles[instructions[i].name]` gets the number of delay cycles for the instruction
    # from the `delay_cycles` dictionary, using the instruction's name as the key.
    ins_condition(
        i,  # Instruction number/index.
        instructions[i].name,  # Name/type of the instruction.
        delay_cycles[instructions[i].name]  # Delay cycles for the instruction.
    ) 
    for i in range(6)  # Iterate over the first six instructions.
]



# Reservation_station_state is a list that represents the state of reservation stations.
# Reservation stations are used to hold instructions before they are executed.

# The first element is initialized as an empty string.
Reservation_station_state = ['']

# Create reservation stations for load operations.
# Reservation stations 1 to 2 are designated for 'L.D' (load double) operations.
for i in range(1, 3):
    Reservation_station_state.append(reservation_station('L.D', i))

# Create reservation stations for addition and subtraction operations.
# Reservation stations 3 to 5 are for 'ADD.D' (add double) operations.
for i in range(3, 7):
    Reservation_station_state.append(reservation_station('ADD.D', i))

# Create reservation stations for multiplication and division operations.
# Reservation stations 6 to 7 are for 'DIV.D' (divide double) operations.
for i in range(7, 9):
    Reservation_station_state.append(reservation_station('DIV.D', i))

# Initialize basic_time as a counter for the simulation's current time/cycle.
basic_time = 0

# Initialize cur_started_instructions to track the number of instructions that have started execution.
cur_started_instructions = 0



def single_step():
    global tree_ins_state
    global tree_Qi
    global tree_r_s_state
    global basic_time
    global cur_started_instructions
    global Reservation_station_state
    global Instruction_state
    global instructions
    global Qi
    global timer
    text_1.set('unrefreshed')
    # Timer jump
    basic_time+=1
    var.set(basic_time)
    # If not issued, then go sequentially to the next
    if cur_started_instructions<len(Instruction_state):
        op=Instruction_state[cur_started_instructions].op
        res=avai_res_station(op)
        if res>0:
            # get the current instruction
            cur_instuction=instructions[cur_started_instructions]
            # Update the researvation station
            Reservation_station_state[res].Busy=True
            Reservation_station_state[res].curr_op=op
            Reservation_station_state[res].started_time=basic_time
            # The first instruction
            if Qi[cur_instuction.opr1]==0:
                Reservation_station_state[res].Vj=registers[cur_instuction.opr1]
                Reservation_station_state[res].Qj=0  
            else:
                Reservation_station_state[res].Qj=Qi[cur_instuction.opr1]
            # Whether load or not
            if op=='L.D':
                Reservation_station_state[res].A=cur_instuction.opr3
                Qi[cur_instuction.opr2]=res
            else:
                if Qi[cur_instuction.opr2]==0:
                    Reservation_station_state[res].Vk=registers[cur_instuction.opr2]
                    Reservation_station_state[res].Qk=0
                else:
                    Reservation_station_state[res].Qk=Qi[cur_instuction.opr2]
                Qi[cur_instuction.opr3]=res
        # Update the instruction table once issued
        Instruction_state[cur_started_instructions].start_time=basic_time
        Instruction_state[cur_started_instructions].started=True
        Instruction_state[cur_started_instructions].ex_number=res
        # Shift to the next issued instruction
        cur_started_instructions+=1
        


    # Execusion
    # Check researvation station
    for i in range(1,9):
        if Reservation_station_state[i].Busy==True:
            # Shift from Issue to Execution
            if Reservation_station_state[i].started_time==basic_time-1:
                for j in range(6):
                     if Instruction_state[j].ex_number==i:
                         Instruction_state[j].executed=True
                         break
                # Load the instruction
                if Reservation_station_state[i].Op=='L.D' and Reservation_station_state[i].Qj==0:
                    # Calculate the correct destination
                    Reservation_station_state[i].A=str(Reservation_station_state[i].Vj)+'+'+str(Reservation_station_state[i].A)
                    # Get the data into result
                    Reservation_station_state[i].result='Mem'+'['+Reservation_station_state[i].A+']'
                # ALU operations
                elif Reservation_station_state[i].Qj==0 and Reservation_station_state[i].Qk==0:
                    if Reservation_station_state[i].curr_op=='ADD.D':
                        Reservation_station_state[i].result=str(Reservation_station_state[i].Vj)+'+'+str(Reservation_station_state[i].Vk)
                    if Reservation_station_state[i].curr_op=='SUB.D':
                        Reservation_station_state[i].result=str(Reservation_station_state[i].Vj)+'-'+str(Reservation_station_state[i].Vk)
                    if Reservation_station_state[i].curr_op=='MUL.D':
                        Reservation_station_state[i].result=str(Reservation_station_state[i].Vj)+'*'+str(Reservation_station_state[i].Vk)
                    if Reservation_station_state[i].curr_op=='DIV.D':
                        Reservation_station_state[i].result=str(Reservation_station_state[i].Vj)+'/'+str(Reservation_station_state[i].Vk)
            # Execution -> Write Back
            elif Reservation_station_state[i].started_time==basic_time-delay_cycles[Reservation_station_state[i].curr_op]:
                for j in range(6):
                     if Instruction_state[j].ex_number==i:
                         Instruction_state[j].written=True
                         break
                for x in Qi:
                    # If waiting for the results
                    if Qi[x]==i:
                        registers[x]=Reservation_station_state[i].result
                        # Make Qi available again
                        Qi[x]=0
                for j in range(1,9):
                    if Reservation_station_state[j].Qj==i and Reservation_station_state[j].Vj=='None':
                        Reservation_station_state[j].Vj=Reservation_station_state[i].result
                        Reservation_station_state[j].Qj=0
                    if Reservation_station_state[j].Qk==i and Reservation_station_state[j].Vk=='None':
                        Reservation_station_state[j].Vk=Reservation_station_state[i].result
                        Reservation_station_state[j].Qk=0
                Reservation_station_state[i].finish_end()
    items=tree_ins_state.get_children()
    for item in items:
        tree_ins_state.delete(item)
    for i in range(6):
        x=Instruction_state[i]
        tree_ins_state.insert('',x.number,text='Instr'+str(x.number),values=(x.op,x.start_time,x.execute_time,x.started,x.executed,x.ex_number,x.written))
    items=tree_r_s_state.get_children()
    for item in items:
        tree_r_s_state.delete(item)
    for i in range(1,len(Reservation_station_state)):
        x=Reservation_station_state[i]
        tree_r_s_state.insert('',i,text='Res Station'+str(i),values=(x.Op,x.curr_op,x.number,x.Qj,x.Qk,x.Vj,x.Vk,x.Busy,x.A,x.started_time,x.result))
    items=tree_Qi.get_children()
    for item in items:
        tree_Qi.delete(item)
    p=[]
    for x in Qi:
        p.append(Qi[x])
    tree_Qi.insert('',1,values=tuple(p))
def refresh():
    global tree_ins_state
    global tree_Qi
    global tree_r_s_state
    global Instruction_state
    global basic_time
    global cur_started_instructions
    global Reservation_station_state
    global Qi
    text_1.set('refreshed')
    # global variable
    basic_time=0
    var.set(0)
    cur_started_instructions=0
    Instruction_state=[ins_condition(i,instructions[i].name,delay_cycles[instructions[i].name]) for i in range(6)]
    for i in range(1,len(Reservation_station_state)):
        Reservation_station_state[i].finish_end()
    for x in Qi:
        Qi[x]=0
    items=tree_ins_state.get_children()
    for item in items:
        tree_ins_state.delete(item)
    for i in range(6):
        x=Instruction_state[i]
        tree_ins_state.insert('',x.number,text='Inst'+str(x.number),values=(x.op,x.start_time,x.execute_time,x.started,x.executed,x.ex_number,x.written))
    items=tree_r_s_state.get_children()
    for item in items:
        tree_r_s_state.delete(item)
    for i in range(1,len(Reservation_station_state)):
        x=Reservation_station_state[i]
        tree_r_s_state.insert('',i,text='Res Station'+str(i),values=(x.Op,x.curr_op,x.number,x.Qj,x.Qk,x.Vj,x.Vk,x.Busy,x.A,x.started_time,x.result))
    items=tree_Qi.get_children()
    for item in items:
        tree_Qi.delete(item)
    p=[]
    for x in Qi:
        p.append(Qi[x])
    tree_Qi.insert('',1,values=tuple(p))




def unrefresh():
    global timer
    if text_1.get()=='unrefreshed':
        single_step()
        timer.cancel()
        timer=threading.Timer(1,unrefresh)
        timer.start()

timer=threading.Timer(1,unrefresh)

def automatic():
    global Instruction_state
    global basic_time
    global cur_started_instructions
    global Reservation_station_state
    global Qi
    global tree_ins_state
    global tree_Qi
    global tree_r_s_state
    text_1.set('unrefreshed')
    i=0
    while i<50:
        if text_1.get()=='unrefreshed':
            timer.start()
            i+=1
        else:
            break
window=tk.Tk()
window.title('Tomasulo Simulator')
window.geometry('1920x1080')
text_1=tk.StringVar()
text_1.set('unrefreshed')
label_1=tk.Label(window,text='Instr Window',bg='skyblue',font=('Arial',15),width=40,height=1)
label_1.pack()
tree_ins_state=ttk.Treeview(window)
tree_ins_state['columns']=('Instr Type','Instr Issue Time','Delay','IS_ISSUED','IS_EXEC','Curr Instr Res Station','IS_WRBACK')
tree_ins_state.column('Instr Type',width=100)
tree_ins_state.column('Instr Issue Time',width=100)
tree_ins_state.column('Delay',width=100)
tree_ins_state.column('IS_ISSUED',width=100)
tree_ins_state.column('IS_EXEC',width=100)
tree_ins_state.column('Curr Instr Res Station',width=250)
tree_ins_state.column('IS_WRBACK',width=100)
tree_ins_state.heading('Instr Type',text='Instr Type')
tree_ins_state.heading('Instr Issue Time',text='Instr Issue Time')
tree_ins_state.heading('Delay',text='Delay')
tree_ins_state.heading('IS_ISSUED',text='IS_ISSUED')
tree_ins_state.heading('IS_EXEC',text='IS_EXEC')
tree_ins_state.heading('Curr Instr Res Station',text='Curr Instr Res Station')
tree_ins_state.heading('IS_WRBACK',text='IS_WRBACK')
for i in range(6):
    x=Instruction_state[i]
    tree_ins_state.insert('',x.number,text='Instr'+str(x.number),values=(x.op,x.start_time,x.execute_time,x.started,x.executed,x.ex_number,x.written))
tree_ins_state.pack()
label_2=tk.Label(window,text='Res Station',bg='skyblue',font=('Arial',15),width=40,height=1)
label_2.pack()
tree_r_s_state=ttk.Treeview(window)
tree_r_s_state['columns']=(1,2,3,4,5,6,7,8,9,10,11)
for i in tree_r_s_state['columns']:
    tree_r_s_state.column(i,width=150)
tree_r_s_state.heading(1,text='Res Station Status')
tree_r_s_state.heading(2,text='Current Instr Type')
tree_r_s_state.heading(3,text='#')
tree_r_s_state.heading(4,text='Qj')
tree_r_s_state.heading(5,text='Qk')
tree_r_s_state.heading(6,text='Vj')
tree_r_s_state.heading(7,text='Vk')
tree_r_s_state.heading(8,text='Busy')
tree_r_s_state.heading(9,text='A')
tree_r_s_state.heading(10,text='Start Cycle')
tree_r_s_state.heading(11,text='Result')
for i in range(1,len(Reservation_station_state)):
    x=Reservation_station_state[i]
    tree_r_s_state.insert('',i,text='Res Station'+str(i),values=(x.Op,x.curr_op,x.number,x.Qj,x.Qk,x.Vj,x.Vk,x.Busy,x.A,x.started_time,x.result))
tree_r_s_state.pack()
label_3=tk.Label(window,text='Reg Status',bg='skyblue',font=('Arial',15),width=40,height=1)
label_3.pack()
tree_Qi=ttk.Treeview(window,show='headings')
tree_Qi['columns']=(1,2,3,4,5,6,7,8)
for i in tree_Qi['columns']:
    tree_Qi.column(i,width=100)
tree_Qi.heading(1,text='F0')
tree_Qi.heading(2,text='F2')
tree_Qi.heading(3,text='F4')
tree_Qi.heading(4,text='F6')
tree_Qi.heading(5,text='F8')
tree_Qi.heading(6,text='F10')
tree_Qi.heading(7,text='R2')
tree_Qi.heading(8,text='R3')
tree_Qi.insert('',1,values=(0,0,0,0,0,0,0,0))
tree_Qi.pack()
button_single_step=tk.Button(window,text='Step_By_Step',width=10,height=1,command=single_step)
button_refresh=tk.Button(window,text='Refresh',width=10,height=1,command=refresh)
button_automatic=tk.Button(window,text='AutoExe',width=10,height=1,command=automatic)
button_single_step.pack()
button_refresh.pack()
button_automatic.pack()
frame_1=tk.Frame(window)
label_0=tk.Label(frame_1,text='ECE 668',font=('Arial',16),width=15,height=2)
label_0.pack(side=tk.LEFT)
var=tk.IntVar()
var.set(basic_time)
label_01=tk.Label(frame_1,text='Curr Cycle：',font=('Arial',18),width=11,height=1)
label_02=tk.Label(frame_1,textvariable=var,fg='red',font=('Arial',25),width=11,height=1)
label_02.pack(side=tk.RIGHT)
label_01.pack(side=tk.RIGHT)
frame_1.pack(fill=tk.BOTH,expand=tk.YES)
window.mainloop()

