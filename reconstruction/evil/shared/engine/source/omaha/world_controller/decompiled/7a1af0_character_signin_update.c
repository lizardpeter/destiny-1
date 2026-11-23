
void FUN_007a1af0(long param_1)

{
  long *plVar1;
  char cVar2;
  int iVar3;
  undefined8 uVar4;
  long lVar5;
  undefined4 uVar6;
  undefined4 local_48 [2];
  undefined4 local_40 [2];
  undefined4 local_38 [2];
  undefined4 local_30 [2];
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  cVar2 = FUN_00788e50();
  if ((cVar2 == '\0') || ((*(int *)(param_1 + 0x40) == 2 && (iVar3 = FUN_00982950(), iVar3 != 1))))
  goto switchD_007a1bbf_default;
  cVar2 = FUN_0078e1c0();
  if (cVar2 != '\0') {
    uVar4 = FUN_00078970(&DAT_026bc2b8);
    cVar2 = FUN_005795a0(uVar4);
    if (cVar2 != '\0') goto switchD_007a1bbf_default;
  }
  iVar3 = *(int *)(param_1 + 0x44);
  if (iVar3 == *(int *)(param_1 + 0x40)) {
    iVar3 = FUN_0078ddc0(0);
    if (iVar3 == 6) {
      *(undefined4 *)(param_1 + 0x44) = 7;
      FUN_00753a60(param_1 + 0x48);
      if (*(int *)(param_1 + 0x148) - 5U < 2) {
        FUN_00783ed0(0x18);
      }
    }
    goto switchD_007a1bbf_default;
  }
  *(int *)(param_1 + 0x40) = iVar3;
  switch(iVar3) {
  case 0:
    lVar5 = FUN_005754e0(4);
    uVar6 = DAT_026d0064;
    if (lVar5 != 0) {
      local_30[0] = DAT_026d006c;
      cVar2 = FUN_0028eae0(lVar5,local_30);
      if (cVar2 != '\0') {
        uVar6 = DAT_026d0068;
      }
    }
    local_38[0] = uVar6;
    iVar3 = FUN_004e3f20(local_38);
    if (iVar3 == -1) {
      *(undefined4 *)(param_1 + 0x44) = 3;
    }
    else {
      local_40[0] = uVar6;
      FUN_00765c60(local_40);
      *(undefined4 *)(param_1 + 0x44) = 1;
    }
    break;
  case 1:
    FUN_00788e10(0x1a);
    FUN_00765fb0(2);
    break;
  case 2:
    FUN_009828f0(0xfa);
    *(undefined4 *)(param_1 + 0x44) = 3;
    break;
  case 3:
    FUN_00788e10(0x1b);
    local_48[0] = DAT_026d0060;
    FUN_00765c60(local_48);
    *(undefined4 *)(param_1 + 0x44) = 4;
    break;
  case 4:
    cVar2 = FUN_0078e1c0();
    if (cVar2 == '\0') {
      *(undefined4 *)(param_1 + 0x44) = 5;
    }
    else {
      *(undefined4 *)(param_1 + 0x44) = 6;
    }
    break;
  case 5:
    FUN_00788e10(0x1c);
    uVar4 = 3;
    goto LAB_007a1c9f;
  case 6:
    FUN_00788e10(0x1d);
    uVar4 = 4;
LAB_007a1c9f:
    FUN_00765fb0(uVar4);
    FUN_00982920(0xfa);
    break;
  case 7:
    FUN_00788e10(0x13);
  }
switchD_007a1bbf_default:
  if (*plVar1 != local_28) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

