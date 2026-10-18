
void FUN_007db810(long param_1,undefined8 *param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5)

{
  uint uVar1;
  uint uVar2;
  undefined8 uVar3;
  
  if (*(int *)(param_1 + 0x24) == 0x40) {
    if (DAT_01a231f0 == (code *)0x0) {
      FUN_0005c750(s__Ran_out_of_command_buffer_segme_0165febb + 1);
      s__libexec_ld_elf_so_1_00000000[1] = '*';
      s__libexec_ld_elf_so_1_00000000[2] = '\0';
      s__libexec_ld_elf_so_1_00000000[3] = '\0';
      s__libexec_ld_elf_so_1_00000000[4] = '\0';
    }
    else {
      (*DAT_01a231f0)(0,s__Ran_out_of_command_buffer_segme_0165febb + 1);
    }
  }
  uVar1 = (int)param_2[0x12] - (int)param_2[0x10];
  uVar2 = (int)param_2[2] - (int)*param_2;
  *(undefined4 *)(param_1 + 0x630 + (ulong)*(uint *)(param_1 + 0x24) * 4) = param_3;
  *(undefined4 *)(param_1 + 0x730 + (ulong)*(uint *)(param_1 + 0x24) * 4) = param_4;
  *(undefined4 *)(param_1 + 0x830 + (ulong)*(uint *)(param_1 + 0x24) * 4) = param_5;
  if (3 < (uVar1 | uVar2)) {
    *(uint *)(param_1 + 0x430 + (ulong)*(uint *)(param_1 + 0x24) * 4) = uVar2 & 0xfffffffc;
    *(undefined8 *)(param_1 + 0x30 + (ulong)*(uint *)(param_1 + 0x24) * 8) = *param_2;
    uVar3 = 0;
    *(uint *)(param_1 + 0x530 + (ulong)*(uint *)(param_1 + 0x24) * 4) = uVar1 & 0xfffffffc;
    if (*(int *)(param_1 + 0x530 + (ulong)*(uint *)(param_1 + 0x24) * 4) != 0) {
      uVar3 = param_2[0x10];
    }
    *(undefined8 *)(param_1 + 0x230 + (ulong)*(uint *)(param_1 + 0x24) * 8) = uVar3;
    *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 1;
  }
  return;
}

