
undefined8 FUN_007a3b70(long param_1)

{
  long *plVar1;
  char cVar2;
  int iVar3;
  undefined8 uVar4;
  long lVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined4 local_50 [2];
  undefined4 local_48 [2];
  undefined4 local_40 [2];
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  uVar4 = FUN_003409a0();
  if (*(int *)(param_1 + 0x6c8) == 0x1a) {
    lVar5 = FUN_0075c6a0();
  }
  else {
    lVar5 = FUN_0075c6d0();
  }
  if (lVar5 == 0) {
    cVar2 = FUN_00752150(3);
    if (cVar2 == '\0') {
      local_40[0] = FUN_007c9830(0x13);
      FUN_007c7540(DAT_0165bc00,DAT_0165bc04,DAT_0165bc08,local_40,
                   s_Could_not_find_any_activity_to_l_0165bf25);
      uVar7 = 1;
    }
    else if (DAT_01a231f0 == (code *)0x0) {
      FUN_0005c750(s_Could_not_find_any_activity_to_l_0165becb);
      s__libexec_ld_elf_so_1_00000000[1] = '*';
      s__libexec_ld_elf_so_1_00000000[2] = '\0';
      s__libexec_ld_elf_so_1_00000000[3] = '\0';
      s__libexec_ld_elf_so_1_00000000[4] = '\0';
      uVar7 = 1;
    }
    else {
      (*DAT_01a231f0)(3,s_Could_not_find_any_activity_to_l_0165becb);
      uVar7 = 1;
    }
  }
  else if ((*(ushort *)(param_1 + 0x6ba) & 0x40) == 0) {
    cVar2 = FUN_00340cf0(uVar4);
    uVar7 = 1;
    if (cVar2 == '\0') {
      cVar2 = FUN_00340cb0(uVar4);
      if (cVar2 != '\0') {
        uVar6 = FUN_00078970(uVar4);
        iVar3 = thunk_FUN_012aa806(uVar6,lVar5);
        if (iVar3 == 0) {
          *(byte *)(param_1 + 0x6ba) = *(byte *)(param_1 + 0x6ba) | 0xc0;
          goto LAB_007a3dda;
        }
      }
      FUN_00340f30(uVar4,lVar5);
      local_48[0] = 1;
      FUN_00341050(uVar4,local_48);
      FUN_00341960(uVar4);
      *(byte *)(param_1 + 0x6ba) = *(byte *)(param_1 + 0x6ba) | 0x40;
    }
  }
  else if ((*(ushort *)(param_1 + 0x6ba) & 0x80) == 0) {
    cVar2 = FUN_00340cf0(uVar4);
    uVar7 = 1;
    if (cVar2 == '\0') {
      cVar2 = FUN_00340dc0(uVar4,lVar5,0);
      if (cVar2 == '\0') {
        cVar2 = FUN_00752150(3);
        if (cVar2 == '\0') {
          local_50[0] = FUN_007c9830(0x13);
          FUN_007c7740(DAT_0165bc00,DAT_0165bc04,DAT_0165bc08,local_50,
                       s_Failed_to_pre_load_activity___s__0165bfd3,lVar5);
        }
        else if (DAT_01a231f0 == (code *)0x0) {
          FUN_0005c750(s_Failed_to_pre_load_next_activity_0165bfac,lVar5);
          s__libexec_ld_elf_so_1_00000000[1] = '*';
          s__libexec_ld_elf_so_1_00000000[2] = '\0';
          s__libexec_ld_elf_so_1_00000000[3] = '\0';
          s__libexec_ld_elf_so_1_00000000[4] = '\0';
        }
        else {
          (*DAT_01a231f0)(3,s_Failed_to_pre_load_next_activity_0165bfac,lVar5);
        }
      }
      else {
        FUN_007521a0(lVar5);
        *(byte *)(param_1 + 0x6ba) = *(byte *)(param_1 + 0x6ba) | 0x80;
      }
    }
  }
  else {
    cVar2 = FUN_00340cb0(uVar4);
    uVar7 = 1;
    if (cVar2 != '\0') {
      *(byte *)(param_1 + 0x6ba) = *(byte *)(param_1 + 0x6ba) & 0x3f;
      uVar7 = 2;
    }
  }
LAB_007a3dda:
  if (*plVar1 == local_38) {
    return uVar7;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

