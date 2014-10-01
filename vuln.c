// Don't include unistd.h otherwise a secure version of read will be used
// #include <unistd.h>

#include <alloca.h>
#include <stdlib.h>
#include <stdio.h>

char put_me_in_bss[1024] = {0};

int play_with_stack(int i) {
  int *local = alloca(10);
  local[0] = 123;
  return local[i];
}

void add(int *a, int b) {
  *a += b;
}

void mem_to_mem(int *dst, int *src) {
  *dst = *src;
}

void writemem(void **in, void *val) {
  *in = val;
}

int do_read() {
  char buffer[100];
  read(0, buffer, 10000);
}

void deref_and_write_with_offset() {
  asm("pop eax; pop ebx; pop ecx; mov eax,DWORD PTR [eax]; mov DWORD PTR [eax+ecx*1],ebx; ret;");
}

int main() {
  do_read();
}
