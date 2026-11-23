
/* WARNING: Removing unreachable block (ram,0x00948ee8) */
/* WARNING: Removing unreachable block (ram,0x00948ad8) */

void FUN_009489d0(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,
                 undefined8 param_5,undefined8 param_6,undefined8 param_7,undefined8 param_8,
                 uint param_9,long param_10,undefined8 param_11,undefined8 param_12,
                 undefined8 param_13,undefined8 param_14)

{
  char in_AL;
  char cVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  undefined *puVar5;
  undefined **ppuVar6;
  long lVar7;
  wchar16 *pwVar8;
  undefined1 local_9858 [16];
  undefined8 local_9848;
  undefined8 local_9840;
  undefined8 local_9838;
  undefined8 local_9830;
  undefined8 local_9828;
  undefined8 local_9818;
  undefined8 local_9808;
  undefined8 local_97f8;
  undefined8 local_97e8;
  undefined8 local_97d8;
  undefined8 local_97c8;
  undefined8 local_97b8;
  undefined1 local_979c [4];
  undefined4 local_9798;
  undefined4 local_9794;
  undefined1 *local_9790;
  undefined1 *local_9788;
  undefined **local_9778;
  undefined1 local_9770;
  undefined8 local_9758;
  undefined8 local_9750;
  undefined1 local_9748;
  undefined1 local_9740;
  undefined1 local_973f;
  undefined4 local_9538;
  undefined4 local_9534;
  undefined4 local_9530;
  undefined4 local_8928;
  undefined4 local_8924;
  undefined4 local_8920;
  undefined1 local_7ea0 [288];
  undefined1 local_7d80 [1024];
  undefined4 local_7980;
  undefined4 local_797c;
  undefined1 local_7970 [512];
  undefined1 local_7770 [8];
  undefined1 *local_7768;
  undefined1 local_7660;
  undefined4 local_edc;
  undefined1 local_ed8 [264];
  undefined1 local_dd0 [264];
  undefined1 local_cc8 [3216];
  long local_38;
  
  if (in_AL != '\0') {
    local_9828 = param_1;
    local_9818 = param_2;
    local_9808 = param_3;
    local_97f8 = param_4;
    local_97e8 = param_5;
    local_97d8 = param_6;
    local_97c8 = param_7;
    local_97b8 = param_8;
  }
  local_38 = *DAT_01a1f100;
  local_9848 = param_11;
  local_9840 = param_12;
  local_9838 = param_13;
  local_9830 = param_14;
  iVar3 = FUN_000f7c30();
  iVar4 = -1;
  LOCK();
  if (DAT_02744128 != -1) {
    iVar4 = DAT_02744128;
    iVar3 = DAT_02744128;
  }
  DAT_02744128 = iVar3;
  UNLOCK();
  iVar3 = FUN_000f7c30();
  if ((iVar4 == iVar3) || (cVar1 = FUN_000be570(), cVar1 != '\0')) {
    s__libexec_ld_elf_so_1_00000000[1] = '*';
    s__libexec_ld_elf_so_1_00000000[2] = '\0';
    s__libexec_ld_elf_so_1_00000000[3] = '\0';
    s__libexec_ld_elf_so_1_00000000[4] = '\0';
    goto LAB_00948a8c;
  }
  cVar1 = FUN_000014d0();
  if (iVar4 != -1) {
    while (cVar1 == '\0') {
      FUN_000f7690(0x1e);
      cVar1 = FUN_000014d0();
    }
    goto LAB_00948a8c;
  }
  if (cVar1 != '\0') {
    LOCK();
    DAT_02744128 = -1;
    UNLOCK();
    goto LAB_00948a8c;
  }
  FUN_000f7690(0xfa);
  if (param_9 == 1) {
    FUN_00084300(4);
  }
  local_7660 = 0;
  lVar7 = 0x324;
  do {
    FUN_00087ad0((long)&local_7980 + lVar7);
    lVar7 = lVar7 + 0x114;
  } while (lVar7 != 0x6aa4);
  local_edc = 0;
  FUN_00087ad0(local_ed8);
  FUN_00087ad0(local_dd0);
  FUN_00087ad0(local_cc8);
  local_9778 = &PTR_FUN_01904930;
  local_9770 = 0;
  local_9740 = 0;
  local_973f = 0;
  local_9748 = 0;
  local_9750 = 0;
  local_9758 = 0;
  local_9538 = 0x14;
  local_9534 = 0;
  local_9530 = 0;
  local_8928 = 0x14;
  local_8924 = 0;
  local_8920 = 0;
  FUN_0008a7e0(local_7ea0);
  cVar1 = FUN_007ea2c0();
  if (param_10 == 0) {
    FUN_00065030(&DAT_0274412c,s_Unknown_release_vhalt_0166d090,0x400);
  }
  else {
    local_9788 = local_9858;
    local_9790 = &stack0x00000008;
    local_9794 = 0x30;
    local_9798 = 0x10;
    FUN_000653b0(&DAT_0274412c,0x400,param_10,&local_9798);
  }
  if (param_9 != 4) {
    FUN_000c1f10(&local_7980);
    local_7980 = 4;
    local_797c = 1;
    thunk_FUN_0005d260(0,0,0x40,local_7970,local_7770);
    FUN_010081b0(local_7d80,s_halt__RELEASE_VHALT_0166d0a6);
    FUN_01009650(local_7d80,s_halt_information___s_01614143,&DAT_0274412c);
    local_7768 = local_7d80;
    FUN_0005ad70(&local_9778,local_7d80,0);
    FUN_000c2330(&local_7980,&local_9778);
    FUN_000c27e0(&local_7980,&local_9778);
    FUN_0005ae70(&local_9778,0,1);
  }
  iVar4 = 0;
  puVar5 = (undefined *)0x0;
  if ((cVar1 != '\0') && ((&DAT_015db820)[(ulong)param_9 * 4] != '\0')) {
    FUN_007e6750();
    lVar7 = FUN_001de430();
    if ((lVar7 == 0) || (cVar2 = FUN_001dc240(lVar7), cVar2 == '\0')) {
      iVar4 = FUN_002918f0();
    }
    else {
      iVar4 = FUN_001dd9b0(lVar7);
    }
    if (param_9 == 1) {
      if (iVar4 - 1U < 10) {
        ppuVar6 = &PTR_DAT_0194c8d0;
LAB_00948de1:
        pwVar8 = (wchar16 *)ppuVar6[iVar4 + -1];
      }
      else {
        pwVar8 = u_Problem_reading_game_content__Pl_015dbca0;
      }
LAB_00948df7:
      puVar5 = &DAT_0274452c;
      FUN_00066250(pwVar8,&DAT_0274452c,0x200,local_979c);
    }
    else if (param_9 == 4) {
      puVar5 = (undefined *)FUN_00001df0(iVar4);
    }
    else {
      puVar5 = (undefined *)0x0;
      if (param_9 == 3) {
        if (iVar4 - 1U < 10) {
          ppuVar6 = &PTR_DAT_0194c880;
          goto LAB_00948de1;
        }
        pwVar8 = u_Problem_reading_game_content__To_015dc3f0;
        goto LAB_00948df7;
      }
    }
  }
  if (param_9 != 4) {
    FUN_000c2480(&local_7980,&local_9778);
    FUN_000c3b80(&local_7980,&local_9778);
    FUN_000c3f60(&local_7980,&local_9778);
  }
  if (puVar5 != (undefined *)0x0) {
    FUN_00b40660(puVar5,param_9 != 1,iVar4);
  }
  if (param_9 != 4) {
    FUN_0005b0d0(&local_9778,6);
    iVar4 = 0x1e;
    do {
      FUN_0005b0e0(&local_9778,100,0);
      FUN_000f7690(0x42);
      iVar4 = iVar4 + -1;
    } while (iVar4 != 0);
    FUN_0005b020(&local_9778);
    FUN_000c2020(&local_7980);
  }
  if (puVar5 != (undefined *)0x0) {
    do {
      cVar2 = FUN_00b40770();
      FUN_000f7690(0x1e);
    } while (cVar2 == '\0');
  }
  FUN_00b407a0();
  LOCK();
  DAT_02744128 = -1;
  UNLOCK();
  if ((cVar1 != '\0') && ((&DAT_015db820)[(ulong)param_9 * 4] != '\0')) {
    FUN_007e6670();
  }
  local_9778 = &PTR_FUN_01904930;
  thunk_FUN_0008aa70(local_7ea0);
LAB_00948a8c:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

