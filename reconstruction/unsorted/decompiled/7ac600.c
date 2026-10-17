
void FUN_007ac600(long param_1,undefined8 param_2,int param_3)

{
  long *plVar1;
  char cVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 uVar5;
  char *pcVar6;
  long lVar7;
  undefined8 uVar8;
  char *pcVar9;
  undefined8 uVar10;
  undefined4 local_40 [2];
  undefined4 local_38 [2];
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  pcVar6 = (char *)FUN_00574ef0();
  lVar7 = FUN_0078b450();
  if (param_3 == 3) {
    *(undefined4 *)(param_1 + 0x30) = 0;
  }
  else if (((lVar7 == 0) || (*(short *)(lVar7 + 2) == -1)) ||
          (cVar2 = FUN_00545230(), cVar2 == '\0')) {
    *(int *)(param_1 + 0x30) = param_3;
  }
  else {
    *(undefined4 *)(param_1 + 0x30) = 0;
    FUN_00783e50(0,0x1b);
  }
  *(undefined8 *)(param_1 + 0x40) = 0xffffffffffffffff;
  *(undefined8 *)(param_1 + 0x38) = 0xffffffffffffffff;
  *(undefined4 *)(param_1 + 0x5c) = 0;
  *(undefined1 *)(param_1 + 0x48) = 0;
  *(undefined4 *)(param_1 + 0x54) = 0;
  *(undefined8 *)(param_1 + 0x4c) = 0;
  *(undefined2 *)(param_1 + 0x4c) = 0xffff;
  *(undefined4 *)(param_1 + 0x58) = 0xffffffff;
  cVar2 = FUN_00b21010();
  if ((cVar2 != '\0') && (iVar4 = FUN_00b403e0(), iVar4 == 3)) {
    uVar8 = FUN_009503d0();
    local_38[0] = DAT_026d07b8;
    FUN_00950eb0(uVar8,local_38);
  }
  FUN_00774f40(0);
  uVar5 = FUN_00752a00();
  FUN_00772a70(0,uVar5);
  FUN_0078b3c0(0);
  FUN_0078b420(0);
  FUN_0078bc50();
  uVar3 = 1;
  if ((2 < *(int *)(param_1 + 0x30) - 4U) && (*(int *)(param_1 + 0x30) != 0x119)) {
    uVar3 = 0;
  }
  FUN_0078df80(uVar3);
  pcVar9 = (char *)FUN_00574ef0();
  if ((*pcVar9 == '\x01') && (cVar2 = FUN_00545230(*(undefined2 *)(pcVar9 + 2)), cVar2 == '\0')) {
    iVar4 = *(int *)(param_1 + 0x30);
    uVar10 = 0x13;
LAB_007ac75e:
    uVar8 = uVar10;
    if (iVar4 == 4) goto LAB_007ac76a;
  }
  else {
    iVar4 = *(int *)(param_1 + 0x30);
    uVar8 = 0x21;
    if ((1 < iVar4 - 5U) && (uVar10 = 0x22, iVar4 != 0x119)) goto LAB_007ac75e;
  }
  FUN_00788e10(uVar8);
LAB_007ac76a:
  cVar2 = FUN_00766750();
  if (cVar2 == '\0') {
    uVar8 = FUN_00765ee0();
    FUN_00758d20(uVar8);
    local_40[0] = DAT_026d07b4;
    FUN_00756bc0(uVar8,local_40);
  }
  FUN_00765fb0(7);
  FUN_00766ea0();
  FUN_00766ce0();
  FUN_00b22ce0();
  FUN_0058ebb0(1);
  if (1 < (int)*pcVar6 - 1U) {
    FUN_00587d70();
  }
  FUN_00954790(1);
  if (*plVar1 != local_30) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

