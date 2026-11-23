
ulong FUN_00792ed0(long param_1,int param_2,undefined8 param_3,int *param_4)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  long lVar5;
  undefined8 uVar6;
  ulong uVar7;
  byte bVar8;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  *param_4 = -1;
  uVar3 = 0;
  switch(param_2) {
  case 0:
    uVar3 = FUN_007937d0(param_1,param_4);
    break;
  case 1:
    uVar3 = FUN_00793a00(param_1,param_4);
    break;
  case 2:
    iVar4 = FUN_00785040();
    *param_4 = iVar4;
    cVar1 = FUN_00752150(3);
    if ((cVar1 == '\0') || (*param_4 == -1)) {
      *param_4 = -1;
      goto switchD_00792f1f_caseD_c;
    }
    FUN_00785020();
    goto LAB_007932cb;
  case 3:
    bVar8 = FUN_000672f0();
    goto LAB_00793273;
  case 4:
    bVar8 = FUN_00244f70(0);
    goto LAB_00793273;
  case 5:
    uVar2 = FUN_00ac5a50();
    bVar8 = FUN_0092c7e0(uVar2);
    goto LAB_00793273;
  case 6:
    uVar3 = FUN_007927b0();
    break;
  case 7:
    uVar3 = FUN_007929c0();
    break;
  case 8:
    lVar5 = FUN_0034e3c0();
    if (*(char *)(lVar5 + 0xe9) != '\0') goto switchD_00792f1f_caseD_c;
    lVar5 = FUN_0034e5d0();
    cVar1 = FUN_002e8400(*(undefined4 *)(lVar5 + 0x24));
    goto LAB_0079326e;
  case 9:
    uVar3 = FUN_00792aa0();
    break;
  case 10:
    uVar3 = FUN_00792b80();
    break;
  case 0xb:
    uVar3 = 0;
    cVar1 = FUN_00772750(0,&local_40);
    if (cVar1 == '\0') goto switchD_00792f1f_caseD_c;
    bVar8 = FUN_00b741f0(local_40);
    goto LAB_00793273;
  default:
    goto switchD_00792f1f_caseD_c;
  case 0xd:
    *param_4 = -1;
    goto switchD_00792f1f_caseD_c;
  case 0xe:
    cVar1 = FUN_00752150(3);
    if (cVar1 == '\0') goto switchD_00792f1f_caseD_c;
    cVar1 = FUN_002a7a80(&DAT_02655df8);
    goto LAB_0079326e;
  case 0xf:
    lVar5 = FUN_002dfef0();
    if (lVar5 == 0) goto switchD_00792f1f_caseD_c;
    iVar4 = FUN_00129570(lVar5);
    bVar8 = iVar4 == 2;
    goto LAB_00793273;
  case 0x10:
    cVar1 = FUN_00752150(3);
    if (cVar1 == '\0') goto switchD_00792f1f_caseD_c;
    cVar1 = FUN_005a03f0();
    goto LAB_0079326e;
  case 0x11:
    cVar1 = FUN_00752150(3);
    if (cVar1 == '\0') goto switchD_00792f1f_caseD_c;
    iVar4 = FUN_00559c30(0);
    bVar8 = iVar4 != 3;
    goto LAB_00793273;
  case 0x12:
    uVar3 = FUN_00793c20();
    break;
  case 0x13:
    *param_4 = -1;
    cVar1 = FUN_00752150(3);
    if (cVar1 == '\0') goto switchD_00792f1f_caseD_c;
    uVar6 = FUN_00021860(&DAT_026bc270);
    iVar4 = FUN_00575970(uVar6);
    if (iVar4 == 0) {
      iVar4 = *param_4;
      uVar3 = 0;
    }
    else {
      uVar2 = FUN_00575970(uVar6);
      iVar4 = FUN_0078e2d0(uVar2);
      *param_4 = iVar4;
      uVar3 = (uint)(iVar4 != -1) * 2;
    }
    if ((iVar4 == -1) && (cVar1 = FUN_005428f0(), cVar1 == '\0')) {
      *param_4 = 0xaf;
      uVar3 = 2;
      goto switchD_00792f1f_caseD_c;
    }
    break;
  case 0x14:
    cVar1 = FUN_00752150(3);
    if (cVar1 == '\0') goto switchD_00792f1f_caseD_c;
    iVar4 = FUN_0078de90();
    bVar8 = iVar4 == 3;
    goto LAB_00793273;
  case 0x15:
    cVar1 = FUN_0074b2f0();
    if ((cVar1 == '\0') || (cVar1 = FUN_00752150(3), cVar1 == '\0')) goto switchD_00792f1f_caseD_c;
    iVar4 = FUN_0078dea0();
    bVar8 = iVar4 == 5;
    goto LAB_00793273;
  case 0x16:
    cVar1 = FUN_00953bc0();
    if (cVar1 == '\0') goto switchD_00792f1f_caseD_c;
    FUN_00953bd0();
    goto LAB_007932cb;
  case 0x17:
    cVar1 = FUN_007724f0(0);
    if (cVar1 != '\0') {
      bVar8 = FUN_00775430(0);
      goto LAB_00793273;
    }
    goto LAB_007932cb;
  case 0x18:
    cVar1 = FUN_00752150(3);
    if (cVar1 == '\0') goto switchD_00792f1f_caseD_c;
    uVar3 = 0;
    cVar1 = FUN_007724f0(0);
    if (cVar1 == '\0') goto switchD_00792f1f_caseD_c;
    uVar3 = 0;
    iVar4 = FUN_00794ca0(0,*(undefined8 *)(param_1 + 0x18));
    if (iVar4 == 0) goto switchD_00792f1f_caseD_c;
    if (iVar4 == 2) {
      uVar3 = 1;
      goto switchD_00792f1f_caseD_c;
    }
    goto LAB_007932cb;
  case 0x19:
    uVar3 = FUN_00793da0();
    break;
  case 0x1c:
    uVar3 = FUN_00794290();
    break;
  case 0x1d:
    uVar3 = FUN_00794350();
    break;
  case 0x1e:
    uVar3 = FUN_00794720(param_1,param_4);
    break;
  case 0x1f:
    cVar1 = FUN_00752150(3);
    if (((cVar1 == '\0') || (cVar1 = FUN_007724f0(1), cVar1 == '\0')) ||
       (iVar4 = FUN_00794ca0(1,*(undefined8 *)(param_1 + 0x20)), iVar4 == 0))
    goto switchD_00792f1f_caseD_c;
    if (iVar4 == 2) {
      uVar3 = 1;
      goto switchD_00792f1f_caseD_c;
    }
    goto LAB_007932cb;
  case 0x20:
    uVar3 = FUN_00794910(param_1,param_4);
    break;
  case 0x21:
    cVar1 = FUN_00ae8ee0();
    if (cVar1 == '\0') goto switchD_00792f1f_caseD_c;
    uVar6 = FUN_00ae8ef0();
    FUN_00065030(param_3,uVar6,0x100);
    goto LAB_007932cb;
  case 0x22:
    uVar6 = FUN_003409a0();
    cVar1 = FUN_00340cb0(uVar6);
LAB_0079326e:
    bVar8 = cVar1 == '\0';
LAB_00793273:
    uVar3 = (uint)bVar8 * 2;
    break;
  case 0x24:
    uVar3 = FUN_00794ac0(param_1,param_4);
    break;
  case 0x25:
    cVar1 = FUN_00752150(3);
    if (((cVar1 == '\0') || (cVar1 = FUN_007724f0(2), cVar1 == '\0')) ||
       (iVar4 = FUN_00794ca0(2,*(undefined8 *)(param_1 + 0x28)), iVar4 == 0))
    goto switchD_00792f1f_caseD_c;
    if (iVar4 == 2) {
      uVar3 = 1;
      goto switchD_00792f1f_caseD_c;
    }
    goto LAB_007932cb;
  }
  if (uVar3 == 2) {
LAB_007932cb:
    uVar3 = 2;
    if (*param_4 == -1) {
      *param_4 = *(int *)(&DAT_015cf750 + (long)param_2 * 4);
    }
  }
switchD_00792f1f_caseD_c:
  if (*DAT_01a1f100 == local_38) {
    return (ulong)uVar3;
  }
  uVar7 = thunk_FUN_012aa7f6();
  return uVar7;
}

