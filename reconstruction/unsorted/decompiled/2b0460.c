
undefined4 FUN_002b0460(void)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (DAT_0265b504 == 2) {
    if (DAT_0265b50e == -1) {
      if (DAT_01a231f0 == (code *)0x0) {
        FUN_0005c750(s_content_manifest_container_not_a_01624cf9);
        s__libexec_ld_elf_so_1_00000000[1] = '*';
        s__libexec_ld_elf_so_1_00000000[2] = '\0';
        s__libexec_ld_elf_so_1_00000000[3] = '\0';
        s__libexec_ld_elf_so_1_00000000[4] = '\0';
      }
      else {
        (*DAT_01a231f0)(0,s_content_manifest_container_not_a_01624cf9);
      }
    }
    if (DAT_0265b4e0 == 0) {
      if (DAT_01a231f0 == (code *)0x0) {
        FUN_0005c750(s_content_manifest_buffer_not_allo_01624d22);
        s__libexec_ld_elf_so_1_00000000[1] = '*';
        s__libexec_ld_elf_so_1_00000000[2] = '\0';
        s__libexec_ld_elf_so_1_00000000[3] = '\0';
        s__libexec_ld_elf_so_1_00000000[4] = '\0';
      }
      else {
        (*DAT_01a231f0)(0,s_content_manifest_buffer_not_allo_01624d22);
      }
    }
    uVar1 = *(undefined4 *)(DAT_0265b4e0 + 0x6eab8);
  }
  return uVar1;
}

