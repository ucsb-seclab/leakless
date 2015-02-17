// Don't include unistd.h otherwise a secure version of read will be used
// #include <unistd.h>

// #include <alloca.h>
#include <stdlib.h>
#include <stdio.h>

#if !defined(__x86_64__) && !defined(__i386__)
#  error "Unsupported architecture"
#endif


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
#if defined(__x86_64__)
  __asm__("pop rax; pop rbx; pop rcx; mov rax,QWORD PTR [rax]; mov QWORD PTR [rax+rcx*1],rbx; ret;");
#elif defined(__i386__)
  __asm__("pop eax; pop ebx; pop ecx; mov eax,DWORD PTR [eax]; mov DWORD PTR [eax+ecx*1],ebx; ret;");
#endif
}

void deref_with_offset_and_save() {
#if defined(__x86_64__)
  __asm__("pop rax; pop rbx; pop rcx; mov rax, [rax]; mov rax,QWORD PTR [rax+rbx]; mov QWORD PTR [rcx],rax; ret;");
#elif defined(__i386__)
  __asm__("pop eax; pop ebx; pop ecx; mov eax, [eax]; mov eax,DWORD PTR [eax+ebx]; mov DWORD PTR [ecx],eax; ret;");
#endif
}

void copy_to_stack() {
#if defined(__x86_64__)
  __asm__("pop rbx; pop rcx; mov rbx, QWORD PTR [rbx]; mov QWORD PTR [rsp+rcx*1],rbx; ret;");
#elif defined(__i386__)
  __asm__("pop ebx; pop ecx; mov ebx, DWORD PTR [ebx]; mov DWORD PTR [esp+ecx*1],ebx; ret;");
#endif
}

int main() {
  do_read();
}
