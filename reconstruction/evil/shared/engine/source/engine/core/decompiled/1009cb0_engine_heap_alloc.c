
long FUN_01009cb0(long param_1,undefined8 param_2,uint param_3,char param_4)

{
  long lVar1;
  long lVar2;
  long *plVar3;
  char cVar4;
  long lVar5;
  long lVar6;
  ulong uVar7;
  ulong uVar8;
  
  lVar1 = param_1 + 8;
  cVar4 = FUN_000b4f80(lVar1);
  if (cVar4 == '\0') {
    if (DAT_01a231f0 == (code *)0x0) {
      FUN_0005c750(s_allocate_block_on_invalid_heap_01613a75);
      s__libexec_ld_elf_so_1_00000000[1] = '*';
      s__libexec_ld_elf_so_1_00000000[2] = '\0';
      s__libexec_ld_elf_so_1_00000000[3] = '\0';
      s__libexec_ld_elf_so_1_00000000[4] = '\0';
    }
    else {
      (*DAT_01a231f0)(0,s_allocate_block_on_invalid_heap_01613a75);
    }
    lVar5 = 0;
  }
  else {
    lVar2 = param_1 + 0x1c8;
    thunk_FUN_012ab116(lVar2);
    lVar5 = FUN_000b4fc0(lVar1,param_2);
    if (lVar5 == 0) {
      thunk_FUN_012ab126(lVar2);
      lVar5 = 0;
      if (param_4 != '\0') {
        FUN_000c22b0(1);
        if (DAT_01a231f0 == (code *)0x0) {
          FUN_0005c750(s_cortex__ENGINE_OOM__Allocating___016139dc,param_2,param_3);
          s__libexec_ld_elf_so_1_00000000[1] = '*';
          s__libexec_ld_elf_so_1_00000000[2] = '\0';
          s__libexec_ld_elf_so_1_00000000[3] = '\0';
          s__libexec_ld_elf_so_1_00000000[4] = '\0';
          lVar5 = 0;
        }
        else {
          (*DAT_01a231f0)(0,s_cortex__ENGINE_OOM__Allocating___016139dc,param_2,param_3);
        }
      }
    }
    else {
      lVar6 = thunk_FUN_000b6f60(lVar5);
      plVar3 = (long *)(param_1 + 0x20 + (ulong)param_3 * 8);
      *plVar3 = *plVar3 + lVar6;
      lVar6 = thunk_FUN_000b6f30(lVar5);
      *(short *)(lVar6 + 0x1a) = (short)param_3;
      uVar7 = FUN_000b4f90(lVar1);
      uVar8 = *(ulong *)(param_1 + 0x18);
      if (*(ulong *)(param_1 + 0x18) < uVar7) {
        uVar8 = uVar7;
      }
      *(ulong *)(param_1 + 0x18) = uVar8;
      thunk_FUN_012ab126(lVar2);
    }
  }
  return lVar5;
}

