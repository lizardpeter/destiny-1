
void FUN_00799a70(long param_1)

{
  long *plVar1;
  byte bVar2;
  char cVar3;
  int iVar4;
  undefined8 uVar5;
  char *pcVar6;
  ulong local_48;
  ulong local_40;
  ulong local_38;
  char cStack_2c;
  undefined8 local_30;
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  iVar4 = *(int *)(param_1 + 0x30);
  if (iVar4 == 0) {
    *(undefined4 *)(param_1 + 0x30) = 1;
    FUN_00771ac0(0xb);
    FUN_00771b10(0xc);
    iVar4 = *(int *)(param_1 + 0x30);
  }
  switch(iVar4) {
  case 1:
    uVar5 = FUN_00752ef0();
    local_30 = 0;
    FUN_007536f0(uVar5,&stack0xffffffffffffffd0);
    if (cStack_2c != '\0') goto switchD_00799acc_default;
    bVar2 = FUN_00752980();
    iVar4 = bVar2 + 2 + (uint)bVar2;
    if (*(int *)(param_1 + 0x30) == iVar4) goto switchD_00799acc_default;
    *(int *)(param_1 + 0x30) = iVar4;
    if (9 < iVar4 - 1U) goto LAB_00799e73;
    goto LAB_00799c41;
  case 2:
    uVar5 = FUN_003409a0();
    cVar3 = FUN_00340cb0(uVar5);
    if (cVar3 != '\0') {
      FUN_00752420();
    }
    if (*(int *)(param_1 + 0x30) == 3) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 3;
    goto LAB_00799c41;
  case 3:
    uVar5 = FUN_003409a0();
    cVar3 = FUN_00340cb0(uVar5);
    if ((cVar3 != '\0') || (*(int *)(param_1 + 0x30) == 4)) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 4;
    goto LAB_00799c41;
  case 4:
    FUN_007b9f20();
    FUN_009828f0(0xffffffff);
    if (*(int *)(param_1 + 0x30) == 5) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 5;
    goto LAB_00799c41;
  case 5:
    iVar4 = FUN_00982950();
    if ((iVar4 != 1) || (*(int *)(param_1 + 0x30) == 6)) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 6;
    goto LAB_00799c41;
  case 6:
    cVar3 = FUN_007ba160();
    if ((cVar3 != '\0') || (*(int *)(param_1 + 0x30) == 7)) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 7;
    goto LAB_00799c41;
  case 7:
    cVar3 = FUN_00752660();
    if ((cVar3 == '\0') || (*(int *)(param_1 + 0x30) == 8)) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 8;
    goto LAB_00799c41;
  case 8:
    cVar3 = FUN_007526d0();
    if ((cVar3 == '\0') || (*(int *)(param_1 + 0x30) == 9)) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 9;
    goto LAB_00799c41;
  case 9:
    FUN_00789ca0();
    uVar5 = FUN_00752ef0();
    FUN_007531e0(uVar5,2);
    if (*(int *)(param_1 + 0x30) == 10) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 10;
LAB_00799c41:
    FUN_00771ac0(0xb);
LAB_00799c4b:
    FUN_00771b10(0xc);
    goto switchD_00799acc_default;
  case 10:
    uVar5 = FUN_00752ef0();
    local_38 = 0;
    FUN_007536f0(uVar5,&local_38);
    if ((local_38 & 0x4000000000000) != 0) {
      if (DAT_01a231f0 == (code *)0x0) {
        pcVar6 = s_failed_to_unload_bootstrap_unpat_0165b3b7;
LAB_00799f16:
        FUN_0005c750(pcVar6);
        s__libexec_ld_elf_so_1_00000000[1] = '*';
        s__libexec_ld_elf_so_1_00000000[2] = '\0';
        s__libexec_ld_elf_so_1_00000000[3] = '\0';
        s__libexec_ld_elf_so_1_00000000[4] = '\0';
        goto switchD_00799acc_default;
      }
      pcVar6 = s_failed_to_unload_bootstrap_unpat_0165b3b7;
LAB_00799e17:
      (*DAT_01a231f0)(3,pcVar6);
      goto switchD_00799acc_default;
    }
    if ((((local_38 & 0x400000000) != 0) || (cVar3 = FUN_00789d00(), cVar3 == '\0')) ||
       (*(int *)(param_1 + 0x30) == 0xb)) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 0xb;
    break;
  case 0xb:
    uVar5 = FUN_00752ef0();
    FUN_00752f10(uVar5,3);
    if (*(int *)(param_1 + 0x30) == 0xc) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 0xc;
    break;
  case 0xc:
    uVar5 = FUN_00752ef0();
    local_40 = 0;
    FUN_007536f0(uVar5,&local_40);
    if ((local_40 & 0x8000000000000) != 0) {
      if (DAT_01a231f0 == (code *)0x0) {
        pcVar6 = s_failed_to_load_bootstrap_patchab_0165b3de;
        goto LAB_00799f16;
      }
      pcVar6 = s_failed_to_load_bootstrap_patchab_0165b3de;
      goto LAB_00799e17;
    }
    if (((local_40 & 0x800000000) != 0) || (*(int *)(param_1 + 0x30) == 0xd))
    goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 0xd;
    break;
  case 0xd:
    FUN_00766020();
    FUN_00765fb0(1);
    FUN_00982920(0xffffffff);
    if (*(int *)(param_1 + 0x30) == 0xe) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 0xe;
    break;
  case 0xe:
    iVar4 = FUN_00982950();
    if ((iVar4 != 0) || (*(int *)(param_1 + 0x30) == 0xf)) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 0xf;
    break;
  case 0xf:
    FUN_00788db0(2);
    if (*(int *)(param_1 + 0x30) == 0x10) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 0x10;
    break;
  case 0x10:
    cVar3 = FUN_00788df0();
    if ((cVar3 == '\0') || (FUN_00788e10(0x13), *(int *)(param_1 + 0x30) == 0x11))
    goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 0x11;
    break;
  case 0x11:
    uVar5 = FUN_00752ef0();
    FUN_00788db0(3);
    FUN_00752f10(uVar5,7);
    if (*(int *)(param_1 + 0x30) == 0x12) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 0x12;
    break;
  case 0x12:
    uVar5 = FUN_00752ef0();
    local_48 = 0;
    FUN_007536f0(uVar5,&local_48);
    if ((local_48 & 0x80000000000000) != 0) {
      if (DAT_01a231f0 == (code *)0x0) {
        pcVar6 = s_failed_to_load_investment_global_0165b401;
        goto LAB_00799f16;
      }
      pcVar6 = s_failed_to_load_investment_global_0165b401;
      goto LAB_00799e17;
    }
    if ((((local_48 & 0x8000000000) != 0) || (cVar3 = FUN_00788df0(), cVar3 == '\0')) ||
       (FUN_00788e10(0x13), *(int *)(param_1 + 0x30) == 0x13)) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 0x13;
    break;
  case 0x13:
    cVar3 = FUN_007525f0();
    if ((cVar3 == '\0') || (*(int *)(param_1 + 0x30) == 0x14)) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 0x14;
    break;
  case 0x14:
    cVar3 = FUN_007526d0();
    if (cVar3 == '\0') goto switchD_00799acc_default;
    uVar5 = thunk_FUN_0078f6f0();
    FUN_00754410(uVar5);
    if (*(int *)(param_1 + 0x30) == 0x15) goto switchD_00799acc_default;
    *(undefined4 *)(param_1 + 0x30) = 0x15;
LAB_00799e73:
    FUN_00771b10(0xb);
    goto LAB_00799c4b;
  default:
    goto switchD_00799acc_default;
  }
  FUN_00771b10(0xb);
  FUN_00771ac0(0xc);
switchD_00799acc_default:
  if (*plVar1 != local_28) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

