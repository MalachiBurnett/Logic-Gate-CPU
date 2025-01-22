import xml.etree.ElementTree as ET

def generate_circuit_xml(instructions):
    num_select_lines = 8
    num_output_bits = 16

    circuit_group = ET.Element("CircuitGroup", {"Version": "1.2"})
    circuit = ET.SubElement(circuit_group, "Circuit", {"Name": "InstructionMemory"})

    gates = ET.SubElement(circuit, "Gates")
    wires = ET.SubElement(circuit, "Wires")

    gate_id = 1

    user_output_gates = []
    for i in range(num_output_bits):
        output_gate = ET.SubElement(gates, "Gate", {"Type": "UserOutput", "Name": f"UserOutput{i}", "ID": str(gate_id)})
        ET.SubElement(output_gate, "Point", {"X": "832", "Y": str(90 + i * 10), "Angle": "0"})
        user_output_gates.append(gate_id)
        gate_id += 1

    select_ids = []
    not_select_ids = []

    for i in range(num_select_lines):
        user_input_gate = ET.SubElement(gates, "Gate", {"Type": "UserInput", "Name": f"Select{i}", "ID": str(gate_id)})
        ET.SubElement(user_input_gate, "Point", {"X": "100", "Y": str(100 + i * 10), "Angle": "0"})
        select_ids.append(gate_id)
        gate_id += 1

        not_gate = ET.SubElement(gates, "Gate", {"Type": "Not", "Name": f"Not_Select{i}", "ID": str(gate_id)})
        ET.SubElement(not_gate, "Point", {"X": "550", "Y": str(100 + i * 30), "Angle": "0"})
        not_select_ids.append(gate_id)
        gate_id += 1

        wire = ET.SubElement(wires, "Wire")
        ET.SubElement(wire, "From", {"ID": str(select_ids[-1]), "Port": "0"})
        ET.SubElement(wire, "To", {"ID": str(not_select_ids[-1]), "Port": "0"})

    for bit in range(num_output_bits):
        or_gate = ET.SubElement(gates, "Gate", {"Type": "Or", "Name": f"Or_out{bit}", "ID": str(gate_id), "NumInputs": str(len(instructions))})
        ET.SubElement(or_gate, "Point", {"X": "700", "Y": str(100 + bit * 30), "Angle": "0"})
        or_gate_id = gate_id
        gate_id += 1

        for i, instruction in enumerate(instructions):
            if instruction[bit] == "1":
                and_gate = ET.SubElement(gates, "Gate", {"Type": "And", "Name": f"And_{i}_out{bit}", "ID": str(gate_id), "NumInputs": str(num_select_lines)})
                ET.SubElement(and_gate, "Point", {"X": "500", "Y": str(100 + bit * 30 + i * 15), "Angle": "0"})
                and_gate_id = gate_id
                gate_id += 1

                for j in range(num_select_lines):
                    if i & (1 << (num_select_lines - j - 1)):  # Select line is ON
                        wire = ET.SubElement(wires, "Wire")
                        ET.SubElement(wire, "From", {"ID": str(select_ids[j]), "Port": "0"})
                        ET.SubElement(wire, "To", {"ID": str(and_gate_id), "Port": str(j)})
                    else:  # Select line is OFF (use NOT gate)
                        wire = ET.SubElement(wires, "Wire")
                        ET.SubElement(wire, "From", {"ID": str(not_select_ids[j]), "Port": "0"})
                        ET.SubElement(wire, "To", {"ID": str(and_gate_id), "Port": str(j)})

                wire = ET.SubElement(wires, "Wire")
                ET.SubElement(wire, "From", {"ID": str(and_gate_id), "Port": "0"})
                ET.SubElement(wire, "To", {"ID": str(or_gate_id), "Port": str(i)})

        wire = ET.SubElement(wires, "Wire")
        ET.SubElement(wire, "From", {"ID": str(or_gate_id), "Port": "0"})
        ET.SubElement(wire, "To", {"ID": str(user_output_gates[bit]), "Port": "0"})

    return ET.tostring(circuit_group, encoding="utf-8", xml_declaration=True).decode("utf-8")

def generate_gcg(template_path, instructions, output_path):
    # Read the template XML from the file
    tree = ET.parse(template_path)
    root = tree.getroot()
    
    # Generate the updated circuit XML based on the instructions
    new_circuit_xml = generate_circuit_xml(instructions)
    new_circuit_root = ET.fromstring(new_circuit_xml)

    # Find the "InstructionMemory" circuit in the template
    for index, circuit in enumerate(root.findall(".//Circuit")):
        if circuit.attrib.get("Name") == "InstructionMemory":
            # Remove the old "InstructionMemory" circuit
            root.remove(circuit)
            
            # Find the updated "InstructionMemory" circuit in the generated XML
            new_instruction_memory_circuit = new_circuit_root.find(".//Circuit[@Name='InstructionMemory']")
            
            if new_instruction_memory_circuit is not None:
                # Insert the updated circuit at the same position
                root.insert(index, new_instruction_memory_circuit)
            break

    # Write the updated XML back to the specified file
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
