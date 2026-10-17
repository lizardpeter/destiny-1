
void FUN_002afe70(void)

{
  if (DAT_0265b50e != -1) {
    if (DAT_01a231f0 == (code *)0x0) {
      FUN_0005c750(s_content_manifest_container_alloc_01624cb2);
      s__libexec_ld_elf_so_1_00000000[1] = '*';
      s__libexec_ld_elf_so_1_00000000[2] = '\0';
      s__libexec_ld_elf_so_1_00000000[3] = '\0';
      s__libexec_ld_elf_so_1_00000000[4] = '\0';
    }
    else {
      (*DAT_01a231f0)(0,s_content_manifest_container_alloc_01624cb2);
    }
  }
  if (DAT_0265b4e0 != 0) {
    if (DAT_01a231f0 != (code *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x002afeda. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (*DAT_01a231f0)(0,s_content_manifest_buffer_allocate_01624cd7);
      return;
    }
    FUN_0005c750(s_content_manifest_buffer_allocate_01624cd7);
    s__libexec_ld_elf_so_1_00000000[1] = '*';
    s__libexec_ld_elf_so_1_00000000[2] = '\0';
    s__libexec_ld_elf_so_1_00000000[3] = '\0';
    s__libexec_ld_elf_so_1_00000000[4] = '\0';
  }
  return;
}

