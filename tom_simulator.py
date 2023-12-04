import tom_architecture as ta  # Assuming the previous TomasuloProcessor code is in "tom_architecture.py"


class TomasuloSimulator:
    def __init__(self):
        self.processor = ta.TomasuloProcessor()
        self.pipeline = ta.Pipeline(self.processor)
        self.instruction_count = 0
        self.instructions = self.read_instructions("instructions.txt")
        self.global_clock_cycle = 1
        self.current_instruction_issue = 0
        self.current_instruction_execute = 0
        self.rs_name = None
        self.issue_fifo = []
        # A list of functional units and their execution completion time
        self.active_fu = []
        # A list of completed instructions
        self.completed_instructions = []

    # Outputs a list of the instructions
    def read_instructions(self, filename):
        with open(filename, 'r') as file:
            self.instructions = file.readlines()
            self.instruction_count = len(self.instructions)
        return self.instructions

    # The main Tomasulo simulator
    def run_simulation(self):
        op, vj, vk, destination, executing_fu, last_instruction = None, None, None, None, None, None
        while True:
            # Head of next log entry
            log_entry = f"#--------------------------------------------------------#\n"
            log_entry += f"Clock Cycle: {self.global_clock_cycle}\n"

            # Write back 'first' so execution can start for other instructions
            for fu in self.active_fu:
                if fu.rs.execution_done is True:
                    result = self.processor.write_back(self.processor.cdb_value, fu)
                    log_entry += f"Write Back: {result} to {fu.rs.destination}\n"

            # Parse the instruction and issue it if we have not yet done so
            if (self.current_instruction_issue < self.instruction_count) and (last_instruction != self.current_instruction_issue):
                # Get the parts of the instruction that we need
                parts = self.instructions[self.current_instruction_issue].split()
                op = parts[0].strip(',')
                destination = parts[1].strip(',')
                vj = parts[2].strip(',')
                vk = parts[3].strip(',')
                # Issue stage, get the name of the reservation station
                self.rs_name = self.processor.issue(op, vj, vk, destination)
                self.issue_fifo.append(self.rs_name)
                # Accounts for the rs having just gone through issue last cycle
                last_instruction = self.current_instruction_issue
                # Check for structural hazards
                if self.rs_name != "all_busy":
                    log_entry += f"Issued: {self.rs_name}\n"
                self.current_instruction_issue += 1

            # Execute instruction if it has been issued
            if (self.current_instruction_execute < self.instruction_count) \
                    and (getattr(self.processor, self.issue_fifo[self.current_instruction_execute]).just_issued is False) \
                    and (getattr(self.processor, self.issue_fifo[self.current_instruction_execute]).executing is False):
                # Ready to execute
                executing_fu = self.processor.execute(getattr(self.processor, self.issue_fifo[self.current_instruction_execute]).op)
                self.issue_fifo[0] = "Done"
                log_entry += f"Now Executing with FU {executing_fu.name}, instruction {executing_fu.rs.op}\n"
                # Set the execution completion time based off the FU delay and the current cycle
                executing_fu.time_to_completion = executing_fu.execution_time + self.global_clock_cycle
                # Label the instruction for later reference
                executing_fu.instruction_tag = self.current_instruction_execute
                # Add to this list of active FU
                self.active_fu.append(executing_fu)
                # Ready to look at next instruction
                self.current_instruction_execute += 1

            # Check for execution completions
            for fu in self.active_fu:
                if fu.time_to_completion == self.global_clock_cycle:
                    self.processor.cdb_value = f"{fu.rs.vj},{fu.rs.vk}"  # In the style "R1+R2"
                    log_entry += f"Execution done for {fu.name} function unit\n"
                    fu.rs.execution_done = True
                elif (fu.rs.just_start_execute is False) and (fu.rs.writing_back is False):
                    log_entry += f"Still Executing {fu.rs.op} instruction in {fu.name} FU\n"

            # Increment the clock cycle
            self.global_clock_cycle += 1

            # Write to the log
            with open("simulation_log.txt", "a") as file:
                log_entry += "\n"
                file.write(log_entry)

            # Transition stages (assuming one cycle each)
            if getattr(self.processor, self.rs_name).just_issued is True:
                getattr(self.processor, self.rs_name).just_issued = False
            for fu in self.active_fu.copy():
                if fu.rs.just_start_execute is True:
                    fu.rs.just_start_execute = False
                if fu.rs.writing_back is True:
                    # Instruction done writing back, remove from list and reset FU
                    fu.clear_functional_unit(fu.rs.name)
                    self.active_fu.remove(fu)

            # Done?
            if self.pipeline.check_empty() is True:
                with open("simulation_log.txt", "a") as file:
                    log_entry = f"#--------------------------------------------------------#\n"
                    log_entry += f"Clock Cycle: {self.global_clock_cycle}\n"
                    log_entry += "Done"
                    file.write(log_entry)
                break
