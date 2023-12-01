class ReservationStation:
    def __init__(self, name, busy, op, vj, vk, qj, qk, remaining_cycles):
        self.name = name
        self.busy = busy
        self.op = op
        self.vj = vj
        self.vk = vk
        self.qj = qj
        self.qk = qk
        self.remaining_cycles = remaining_cycles


class FunctionalUnit:
    def __init__(self, name, busy, remaining_cycles):
        self.name = name
        self.busy = busy
        self.remaining_cycles = remaining_cycles


class TomasuloProcessor:
    def __init__(self):
        # Functional Units
        self.add_rs1 = ReservationStation("ADD1", False, None, None, None, None, None, 0)
        self.add_rs2 = ReservationStation("ADD2", False, None, None, None, None, None, 0)
        self.mul_rs1 = ReservationStation("MUL1", False, None, None, None, None, None, 0)
        self.mul_rs2 = ReservationStation("MUL2", False, None, None, None, None, None, 0)
        self.int_rs = ReservationStation("INT", False, None, None, None, None, None, 0)

        self.add_fu1 = FunctionalUnit("ADD", False, 0)
        self.add_fu2 = FunctionalUnit("ADD", False, 0)
        self.mul_fu1 = FunctionalUnit("MUL", False, 0)
        self.mul_fu2 = FunctionalUnit("MUL", False, 0)
        self.int_fu = FunctionalUnit("INT", False, 0)

        self.execution_list = []
        self.common_data_bus_value = 0

    # Returns the name of the reservation station handling the calculation
    # Example: ADD R1, R2, R3
    def issue(self, op, vj, vk):
        # Check for available reservation stations and issue instruction accordingly
        if op == "ADD":
            if not self.add_rs1.busy:
                self.add_rs1.busy = True
                self.add_rs1.op = op
                self.add_rs1.vj = vj
                self.add_rs1.vk = vk
                return self.add_rs1.name
            elif not self.add_rs2.busy:
                self.add_rs2.busy = True
                self.add_rs2.op = op
                self.add_rs2.vj = vj
                self.add_rs2.vk = vk
                return self.add_rs2.name
        elif op == "MUL":
            if not self.mul_rs1.busy:
                self.mul_rs1.busy = True
                self.mul_rs1.op = op
                self.mul_rs1.vj = vj
                self.mul_rs1.vk = vk
                return self.mul_rs1.name
            elif not self.mul_rs2.busy:
                self.mul_rs2.busy = True
                self.mul_rs2.op = op
                self.mul_rs2.vj = vj
                self.mul_rs2.vk = vk
                return self.mul_rs2.name
        elif op == "INT":
            if not self.int_rs.busy:
                self.int_rs.busy = True
                self.int_rs.op = op
                self.int_rs.vj = vj
                self.int_rs.vk = vk
                return self.int_rs.name

        return None

    def execute(self):
        # Check for available functional units and execute accordingly
        if not self.add_fu1.busy:
            # Execute ADD operation using Functional Unit 1
            self.add_fu1.busy = True
            self.add_fu1.remaining_cycles = 4  # 4 cycles for ADD
            self.execution_list.append(self.add_rs1.name)
            return "ADD1"
        elif not self.add_fu2.busy:
            # Execute ADD operation using Functional Unit 2
            self.add_fu2.busy = True
            self.add_fu2.remaining_cycles = 4  # 4 cycles for ADD
            self.execution_list.append(self.add_rs2.name)
            return "ADD2"
        elif not self.mul_fu1.busy:
            # Execute MUL operation using Functional Unit 1
            self.mul_fu1.busy = True
            self.mul_fu1.remaining_cycles = 8  # 8 cycles for MUL
            self.execution_list.append(self.mul_rs1.name)
            return "MUL1"
        elif not self.mul_fu2.busy:
            # Execute MUL operation using Functional Unit 2
            self.mul_fu2.busy = True
            self.mul_fu2.remaining_cycles = 8  # 8 cycles for MUL
            self.execution_list.append(self.mul_rs2.name)
            return "MUL2"
        elif not self.int_fu.busy:
            # Execute INT operation using Integer Functional Unit
            self.int_fu.busy = True
            self.int_fu.remaining_cycles = 1  # 1 cycle for INT
            self.execution_list.append(self.int_rs.name)
            return "INT"
        else:
            return None

    def write_result(self, result):
        # Clear busy flags and update common data bus value after execution
        if self.add_rs1.busy and self.add_fu1.busy:
            self.add_rs1.busy = False
            self.add_fu1.busy = False
            self.common_data_bus_value = result
        elif self.add_rs2.busy and self.add_fu2.busy:
            self.add_rs2.busy = False
            self.add_fu2.busy = False
            self.common_data_bus_value = result
        elif self.mul_rs1.busy and self.mul_fu1.busy:
            self.mul_rs1.busy = False
            self.mul_fu1.busy = False
            self.common_data_bus_value = result
        elif self.mul_rs2.busy and self.mul_fu2.busy:
            self.mul_rs2.busy = False
            self.mul_fu2.busy = False
            self.common_data_bus_value = result
        elif self.int_rs.busy and self.int_fu.busy:
            self.int_rs.busy = False
            self.int_fu.busy = False
            self.common_data_bus_value = result
