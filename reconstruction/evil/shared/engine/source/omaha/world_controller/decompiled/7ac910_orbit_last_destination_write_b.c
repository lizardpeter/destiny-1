
void FUN_007ac910(long param_1)

{
  char cVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  long lVar6;
  char *pcVar7;
  undefined8 uVar8;
  long lVar9;
  long lVar10;
  undefined2 *puVar11;
  long extraout_RDX;
  undefined2 *puVar12;
  int *piVar13;
  undefined1 local_78 [24];
  int local_60;
  undefined1 local_48 [16];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_0078c3e0();
  FUN_00774980(0,1);
  lVar6 = FUN_00574ef0();
  FUN_00774f50(*(char *)(lVar6 + 300) == '\0');
  FUN_007ace30(param_1);
  cVar1 = FUN_00765ea0();
  if (cVar1 != '\0') goto LAB_007aca66;
  pcVar7 = (char *)FUN_00574ef0();
  lVar6 = FUN_00775770(0);
  if ((DAT_026d0730 == '\0') && (FUN_00765f00(local_78), local_60 != -1)) {
    uVar8 = FUN_00765ee0();
    cVar1 = FUN_00757690(uVar8);
    if (cVar1 == '\0') {
      cVar1 = FUN_00756c00(uVar8);
      if (cVar1 != '\0') {
        FUN_00756ef0(uVar8);
        FUN_00757230(uVar8);
        lVar10 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          lVar10 = FUN_000694d0();
        }
        *(long *)(param_1 + 0x38) = lVar10;
      }
    }
    else {
      FUN_007576a0();
      FUN_007578a0(uVar8);
      FUN_00757e10(uVar8);
    }
  }
  uVar8 = FUN_00765ee0();
  cVar1 = FUN_007581e0(uVar8);
  if (cVar1 != '\0') {
    lVar10 = *(long *)(param_1 + 0x38);
    if (lVar10 == -1) goto LAB_007aca66;
    lVar9 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar9 = FUN_000694d0();
    }
    if (lVar9 - lVar10 < 0x1389) goto LAB_007aca66;
  }
  cVar1 = FUN_0078c270();
  if (cVar1 == '\0') {
    if (*(char *)(param_1 + 0x48) == '\0') {
      cVar1 = FUN_007754d0(0);
      if (((cVar1 != '\0') && ((int)*pcVar7 - 1U < 2)) && (*(short *)(pcVar7 + 2) != -1)) {
        lVar10 = FUN_00775770(0);
        cVar1 = FUN_00b8f690(lVar10 + 0x9b8);
        if (cVar1 == '\0') {
          FUN_00785060(0);
        }
        else {
          sVar2 = FUN_00b8e1c0(lVar10 + 0x9b8);
          iVar3 = FUN_00785060(0);
          if ((sVar2 != -1) && (iVar3 != 0x1b)) goto LAB_007acaed;
        }
        FUN_0078b550(pcVar7);
        FUN_007acf00();
        goto LAB_007aca66;
      }
LAB_007acaed:
      iVar3 = FUN_00785060(0);
      if ((iVar3 == 0x1b) && (cVar1 = FUN_007ad090(param_1), cVar1 == '\0')) {
        lVar6 = FUN_00775770(0);
        piVar13 = (int *)0x0;
        if (lVar6 != 0) {
          cVar1 = FUN_00b8f690(lVar6 + 0x4b8);
          if (cVar1 != '\0') {
            cVar1 = FUN_00b8f690(lVar6 + 0x4b8);
            piVar13 = (int *)0x0;
            if (cVar1 != '\0') {
              piVar13 = (int *)(lVar6 + 0x59c);
            }
          }
        }
        uVar8 = FUN_00587520();
        lVar6 = FUN_0057de80(uVar8);
        if ((((piVar13 != (int *)0x0) && (iVar3 = *piVar13, iVar3 != -0x7ee3623b)) && (lVar6 != 0))
           && (*(int *)(lVar6 + 0x480) != iVar3)) {
          *(int *)(lVar6 + 0x480) = iVar3;
        }
        uVar8 = 0x19;
        uVar5 = 0xf;
      }
      else {
        if ((lVar6 == 0) || (cVar1 = FUN_00b8f690(lVar6), cVar1 == '\0')) goto LAB_007aca66;
        lVar10 = lVar6 + 0x8b8;
        cVar1 = FUN_00b8f690(lVar10);
        if (cVar1 != '\0') {
          cVar1 = FUN_00b8f690(lVar10);
          puVar12 = (undefined2 *)(lVar6 + 0x99c);
          puVar11 = (undefined2 *)0x0;
          if (cVar1 != '\0') {
            puVar11 = puVar12;
          }
          iVar3 = thunk_FUN_012aa826(param_1 + 0x4c,puVar11,0xc);
          if (iVar3 != 0) {
            cVar1 = FUN_00b8f690(lVar10);
            puVar11 = (undefined2 *)0x0;
            if (cVar1 != '\0') {
              puVar11 = puVar12;
            }
            FUN_007ad170(param_1,param_1 + 0x4c,puVar11);
            cVar1 = FUN_00b8f690(lVar10);
            puVar11 = (undefined2 *)0x0;
            if (cVar1 != '\0') {
              puVar11 = puVar12;
            }
            *(undefined2 *)(param_1 + 0x4c) = *puVar11;
            *(undefined8 *)(param_1 + 0x50) = *(undefined8 *)(puVar11 + 2);
          }
        }
        lVar6 = thunk_FUN_0078b450();
        if ((lVar6 != 0) && (cVar1 = FUN_00545230(*(undefined2 *)(lVar6 + 2)), cVar1 != '\0')) {
          iVar3 = FUN_00945ba0();
          if ((*(short *)(lVar6 + 6) == -1) && (cVar1 = FUN_00775530(0), cVar1 != '\0')) {
            FUN_002725c0(local_48);
            cVar1 = FUN_009553f0(local_48);
            if (cVar1 != '\0') {
              FUN_00955500(local_48);
            }
          }
          if ((iVar3 != -1) && (iVar4 = FUN_0094f6a0(iVar3), iVar4 == -1)) {
            FUN_0094f650(iVar3,0);
          }
        }
        cVar1 = FUN_007754d0(0);
        if (cVar1 != '\0') {
          lVar6 = FUN_00775770(0);
          cVar1 = FUN_00b8f690(lVar6 + 0x9b8);
          if (cVar1 == '\0') {
            FUN_00785060(0);
          }
          else {
            sVar2 = FUN_00b8e1c0(lVar6 + 0x9b8);
            iVar3 = FUN_00785060(0);
            if ((sVar2 != -1) && (iVar3 != 0x1b)) goto LAB_007acd3f;
          }
          FUN_007ad360(param_1);
          iVar3 = *(int *)(param_1 + 0x30);
          if ((iVar3 - 4U < 3) || (iVar3 == 0x119)) {
            FUN_007ad760();
          }
          else if (iVar3 == 0) {
            FUN_007ad500(param_1);
          }
        }
LAB_007acd3f:
        uVar5 = FUN_00785080(0);
        if (((uVar5 == 0xffffffff) || (uVar5 < 0x10)) ||
           ((0x107 < uVar5 - 0x10 && (uVar5 == 0x119)))) {
          lVar6 = FUN_00775770(0);
          lVar6 = lVar6 + 0x9b8;
          cVar1 = FUN_00b8f690(lVar6);
          if (cVar1 == '\0') {
            FUN_00785060(0);
            goto LAB_007aca66;
          }
          sVar2 = FUN_00b8e1c0(lVar6);
          iVar3 = FUN_00785060(0);
          if ((sVar2 == -1) || (iVar3 == 0x1b)) goto LAB_007aca66;
          iVar3 = FUN_0078b250();
          if (iVar3 != 3) {
            FUN_0078b170(2);
          }
          lVar10 = FUN_00775770(0);
          lVar10 = FUN_011c3f80(lVar10 + 0x9b8);
          sVar2 = *(short *)(lVar10 + 2);
          if (sVar2 == -1) {
            uVar5 = *(uint *)(param_1 + 0x30);
          }
          else {
            uVar8 = FUN_005494c0();
            FUN_005498e0(uVar8,CONCAT62((int6)((ulong)lVar6 >> 0x10),sVar2) & 0xffffffff);
            uVar5 = *(uint *)(param_1 + 0x30);
            if (*(int *)(extraout_RDX + 0x18) != -0x7ee3623b) {
              uVar8 = 0x25;
              goto LAB_007aca61;
            }
          }
          uVar8 = 0x1c;
        }
        else {
          uVar8 = 0x19;
        }
      }
    }
    else {
      uVar8 = 0x19;
      uVar5 = 9;
    }
  }
  else {
    uVar8 = 0x19;
    uVar5 = 0x39;
  }
LAB_007aca61:
  FUN_00784e50(uVar8,uVar5);
LAB_007aca66:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

