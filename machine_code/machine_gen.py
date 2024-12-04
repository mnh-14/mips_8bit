import tkinter as tk
from tkinter import filedialog
import os


SRC = "source.txt"
DEST = "instruction"
I_TYPE = "i"
J_TYPE = "j"
M_TYPE = "m"
R_TYPE = "r"
# OP = "op"
# OP_TYPE = "op-type"
# HANDLER = "handler"


encodings = {
    "op":{
        "add": 0xf,
        "srl": 0x0,
        "sub": 0x1,
        "beq": 0x2,
        "j":0x3,
        "sw":0x4,
        "lw":0x5,
        "addi":0x6,
        "sll":0x7,
        "bneq":0x8,
        "and":0x9,
        "andi":0xa,
        "nor":0xb,
        "subi":0xc,
        "ori":0xd,
        "or":0xe,
    },
    "op-type":{
        "add": "r",
        "srl": "i",
        "sub": "r",
        "beq": "i",
        "j":"j",
        "sw":"m",
        "lw":"m",
        "addi":"i",
        "sll":"i",
        "bneq":"i",
        "and":"r",
        "andi":"i",
        "nor":"r",
        "subi":"i",
        "ori":"i",
        "or":"r",
    },
    "handler":{
        "i": None,
        "j": None,
        "r": None,
        "m": None,
    },
    "padding": {
        "op" : 0x10000,
        "rs" : 0x1000,
        "rt" : 0x100,
        "rd" : 0x10,
        "imj": 0x100,
        "im" : 0x1
    },
    "register": {
        "$zero": 0x0,
        "$t0": 0x1,
        "$t1": 0x2,
        "$t2": 0x3,
        "$t3": 0x4,
        "$t4": 0x5,
        "$sp": 0x6,
        "$gp": 0x7,
    }
}


def parser(line:str):
    ll = line.replace(",", " ")
    return ll.split()


def modify_constant(constant: str):
    c = int(constant)
    if c > 0xff:
        raise Exception("Max integer capacity overflowed")
    if c >= 0:
        return c
    c = 0xff + c + 1
    return c


def handle_jtype(keywords: list[str]):
    op, addr = keywords
    code = 0x0
    code += encodings["op"][op] * encodings["padding"]["op"]
    code += encodings["padding"]["imj"] * modify_constant(addr)
    return hex(code)[2:]


def handle_rtype(keywords: list[str]):
    op, rd, rs, rt = keywords
    code = 0x0
    code += encodings["op"][op] * encodings["padding"]["op"]
    code += encodings["register"][rd] * encodings["padding"]['rd']
    code += encodings["register"][rt] * encodings["padding"]['rt']
    code += encodings["register"][rs] * encodings["padding"]['rs']
    
    return hex(code)[2:]
    # return bin(code)[2:0]
    

def handle_itype(keywords: list[str]):
    op, rt, rs, im = keywords
    code = 0x0
    code += encodings["op"][op] * encodings["padding"]["op"]
    code += encodings["register"][rt] * encodings["padding"]['rt']
    code += encodings["register"][rs] * encodings["padding"]['rs']
    # code += hex(int(im)) * encodings["padding"]['im']
    code += modify_constant(im) * encodings["padding"]['im']
    
    return hex(code)[2:]
    # return bin(code)[2:]


def handle_mtype(keywords: list[str]):
    op, rt, shifted = keywords
    code = 0x0
    code += encodings["op"][op] * encodings["padding"]["op"]
    code += encodings["register"][rt] * encodings["padding"]['rt']
    im, rs = shifted.replace("(", " ").replace(")", " ").split()

    code += encodings["register"][rs] * encodings["padding"]['rs']
    # code += hex(int(im)) * encodings["padding"]['im']
    code += modify_constant(im) * encodings["padding"]['im']

    return hex(code)[2:]
    # return bin(code)[2:]


encodings["handler"]['i'] = handle_itype
encodings["handler"]['j'] = handle_jtype
encodings["handler"]['r'] = handle_rtype
encodings["handler"]['m'] = handle_mtype



def get_code():
    lines = [
        "addi $sp, $zero, 255",
        "addi $gp, $zero, 0",
    ]
    
    more_lines = open_file_and_read_lines()

    if more_lines is not None:
        return lines + more_lines

    with open(SRC, 'r') as src:
        lines += src.readlines()
    
    return lines



def save_code(instruction: str):
    instruction = "v2.0 raw\n"+instruction
    
    saved = save_processed_data(instruction)
    
    if saved:
        return

    with open(DEST, 'w') as destination:
        # destination.write("v2.0 raw\n")
        destination.write(instruction)
    
    print("File saved")


def open_file_and_read_lines():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title="Open File", initialdir=os.getcwd())
    if not file_path:
        return None

    with open(file_path, 'r') as file:
        lines = file.readlines()

    return lines


    

def save_processed_data(processed_data):
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.asksaveasfilename(title="Save File", 
                                            #  defaultextension=".txt", 
                                             filetypes=[("Text Files", "*.txt"), 
                                                        ("All Files", "*.*")])
    if not file_path:
        return False

    with open(file_path, 'w') as file:
        file.write(processed_data)

    return True




def main():
    inputs = []
    code_lines = get_code()
    for line in code_lines:
        words = parser(line.strip())
        if len(words) == 0:
            continue
        
        code = encodings["handler"][encodings["op-type"][words[0]]](words)
        inputs.append(code)
        print(line.strip(), " ==>> ", code)
    
    final_code = " ".join(inputs)
    
    save_code(final_code)

    
    




if __name__=="__main__":
    main()