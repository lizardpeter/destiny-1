
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong FUN_00300920(uint param_1,undefined4 param_2,long *param_3,undefined4 param_4)

{
  long lVar1;
  int iVar2;
  int iVar3;
  long lVar4;
  long lVar5;
  char cVar6;
  long lVar7;
  ulong uVar8;
  float fVar9;
  float fVar10;
  float local_40;
  float local_3c;
  long local_38;
  
  lVar4 = DAT_02689540;
  local_38 = *DAT_01a1f100;
  uVar8 = 0;
  if (*(char *)(DAT_02689540 + 0x6c) != '\0') goto LAB_00300ad6;
  cVar6 = FUN_0023fc50();
  if (cVar6 != '\0') goto LAB_00300ad6;
  *param_3 = 0;
  cVar6 = FUN_002ffe70(param_1);
  lVar5 = DAT_02689540;
  if (cVar6 == '\0') {
    lVar1 = lVar4 + 0x28;
    if ((0x220U >> (param_1 & 0x1f) & 1) == 0) {
      local_3c = 0.0;
      local_40 = 0.0;
      iVar2 = *(int *)(lVar4 + 0x30);
      iVar3 = *(int *)(lVar4 + 0x2c);
      lVar7 = FUN_000b0020(*(undefined8 *)(DAT_02689540 + 0x58));
      lVar4 = *(long *)(*(long *)(lVar5 + 0x58) + 0x50);
      FUN_00240e30(param_4,&local_3c,&local_40);
      fVar9 = (float)iVar2 * DAT_01629e1c;
      fVar10 = (float)lVar7 / (float)lVar4;
      if (fVar9 - fVar10 < 0.0) {
        fVar9 = fVar10;
      }
      if ((fVar9 <= local_3c) && ((float)iVar3 * _DAT_01629e20 <= local_40)) goto LAB_00300a72;
      cVar6 = FUN_0023fc80();
      uVar8 = 2;
      if (cVar6 != '\0') {
        cVar6 = FUN_0023fd30();
        if (cVar6 == '\0') {
          FUN_00240d90();
        }
      }
    }
    else {
LAB_00300a72:
      FUN_002ffaa0(lVar1,param_2,param_3,param_4);
      uVar8 = (ulong)(*param_3 == 0);
    }
    FUN_002ffdc0(lVar1);
    FUN_002ffde0(lVar1);
  }
  else {
    FUN_002ffaa0(lVar4,param_2,param_3,param_4);
    FUN_002ffdc0(lVar4);
    FUN_002ffde0(lVar4);
    uVar8 = 0;
  }
  if ((undefined1 *)*param_3 == (undefined1 *)0x0) {
    if (*(char *)(DAT_02689540 + 0x6c) == '\0') {
      cVar6 = FUN_0023fc80();
      if (cVar6 != '\0') {
        cVar6 = FUN_0023fd30();
        if (cVar6 == '\0') {
          FUN_00240d90();
        }
      }
    }
  }
  else {
    *(undefined1 *)*param_3 = (char)param_1;
  }
LAB_00300ad6:
  if (*DAT_01a1f100 == local_38) {
    return uVar8;
  }
  uVar8 = thunk_FUN_012aa7f6();
  return uVar8;
}

