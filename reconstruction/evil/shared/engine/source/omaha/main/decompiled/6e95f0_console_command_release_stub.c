
void FUN_006e95f0(void)

{
  if (DAT_01a231f0 != (code *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x006e960f. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*DAT_01a231f0)(0,s_console_execute_commands_from_bu_016472e9);
    return;
  }
  FUN_0005c750(s_console_execute_commands_from_bu_016472e9);
  s__libexec_ld_elf_so_1_00000000[1] = '*';
  s__libexec_ld_elf_so_1_00000000[2] = '\0';
  s__libexec_ld_elf_so_1_00000000[3] = '\0';
  s__libexec_ld_elf_so_1_00000000[4] = '\0';
  return;
}

