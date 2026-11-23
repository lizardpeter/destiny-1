
void FUN_002affe0(void)

{
  long lVar1;
  
  FUN_002b0090();
  lVar1 = DAT_0265b4a8;
  if (DAT_0265b4a8 != 0) {
    FUN_0009de90(DAT_0265b4a8);
    thunk_FUN_012aaa46(lVar1);
  }
  DAT_0265b4a8 = 0;
  if (DAT_0265b50e != -1) {
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
    FUN_000af8f0(DAT_0265b50e);
    DAT_0265b50e = -1;
    DAT_0265b4e0 = 0;
  }
  DAT_0265b50c = 0;
  return;
}

