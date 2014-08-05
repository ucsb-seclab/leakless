#include <alloca.h>
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

#ifdef __x86_64__

void writemem(void *nope, void *nope2, void *nope3, void *nope4, void *nope5, void *nope6, void **in, void *val) {
  *in = val;
}

#elif __i386__

void writemem(void **in, void *val) {
  *in = val;
}

#else
# error Unsopported arch
#endif

int do_read() {
  char buffer[100];
  read(0, buffer, 1000);
}

int main() {
  do_read();
}
