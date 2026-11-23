
void FUN_0079fe50(long param_1)

{
  long *plVar1;
  code *pcVar2;
  char cVar3;
  ushort uVar4;
  undefined8 uVar5;
  sbyte sVar6;
  undefined8 local_840;
  undefined8 local_838;
  undefined1 local_830 [1024];
  undefined1 local_430 [1024];
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  cVar3 = FUN_000014d0();
  sVar6 = (cVar3 == '\0') + 5;
  switch(*(undefined4 *)(param_1 + 0x30)) {
  case 0:
    *(undefined4 *)(param_1 + 0x30) = 1;
  case 1:
    uVar5 = FUN_00752ef0();
    local_838 = 0;
    FUN_007536f0(uVar5,&local_838);
    if ((local_838._4_2_ & ((ushort)(1 << sVar6) & 0xef | 0x10)) == 0) {
      *(undefined4 *)(param_1 + 0x30) = 2;
    }
    break;
  case 2:
    uVar5 = FUN_00752ef0();
    FUN_00752f10(uVar5,4);
    FUN_00752f10(uVar5,sVar6);
    *(undefined4 *)(param_1 + 0x30) = 3;
    break;
  case 3:
    uVar5 = FUN_00752ef0();
    local_840 = 0;
    FUN_007536f0(uVar5,&local_840);
    pcVar2 = DAT_01a231f0;
    uVar4 = (ushort)(1 << sVar6) & 0xef | 0x10;
    if ((local_840._6_2_ & uVar4) == 0) {
      if ((local_840._4_2_ & uVar4) == 0) {
        *(undefined4 *)(param_1 + 0x30) = 4;
        FUN_007539b0(param_1 + 0x34,1);
      }
    }
    else if (DAT_01a231f0 == (code *)0x0) {
      FUN_010534c0(local_830,(long)&local_840 + 6);
      FUN_0005c750(s_failed_to_load___s__0165bbb7,local_830);
      s__libexec_ld_elf_so_1_00000000[1] = '*';
      s__libexec_ld_elf_so_1_00000000[2] = '\0';
      s__libexec_ld_elf_so_1_00000000[3] = '\0';
      s__libexec_ld_elf_so_1_00000000[4] = '\0';
    }
    else {
      FUN_010534c0(local_430,(long)&local_840 + 6);
      (*pcVar2)(3,s_failed_to_load___s__0165bbb7,local_430);
    }
  }
  if (*plVar1 != local_30) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

