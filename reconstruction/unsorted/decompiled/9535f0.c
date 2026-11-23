
void FUN_009535f0(uint param_1,int param_2,long param_3,undefined8 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int *piVar7;
  undefined8 uVar8;
  long lVar9;
  undefined8 uVar10;
  long lVar11;
  byte bVar12;
  byte bVar13;
  bool bVar14;
  bool bVar15;
  bool bVar16;
  int local_918 [6];
  undefined4 local_900;
  int local_8f8 [2];
  undefined1 local_8f0 [20];
  undefined1 local_8dc;
  undefined4 local_8c8 [2];
  undefined1 local_8c0 [2176];
  code *local_40;
  long local_38;
  
  lVar9 = DAT_0274bfa0;
  local_38 = *DAT_01a1f100;
  cVar1 = FUN_00b21010();
  if ((cVar1 == '\0') && (cVar1 = FUN_00b21030(), cVar1 == '\0')) {
    if ((int)param_1 < 3) {
      uVar8 = FUN_009503d0();
      local_8c8[0] = DAT_0274bf84;
      uVar6 = FUN_00244e40();
      FUN_00950620(uVar8,local_8c8,uVar6,0);
    }
    goto LAB_0095390e;
  }
  iVar2 = FUN_009549a0();
  iVar3 = FUN_00954a20();
  bVar16 = iVar2 <= iVar3;
  bVar14 = param_1 == 2;
  bVar15 = false;
  if ((!bVar14 && !bVar16) && (cVar1 = FUN_009545f0(), cVar1 != '\0')) {
    iVar4 = FUN_00b29350();
    bVar15 = iVar4 == param_2;
  }
  iVar4 = FUN_007850a0();
  if (iVar4 == 0x24) {
    if (bVar14 || bVar16) {
      piVar7 = &DAT_0274bf90;
    }
    else {
      piVar7 = &DAT_0274bf98;
      if (bVar15) {
        piVar7 = &DAT_0274bf94;
      }
    }
LAB_0095374f:
    iVar2 = *piVar7;
    if (iVar2 != -0x7ee3623b) {
      bVar16 = 2 < (int)param_1;
      if ((int)param_1 < 3) {
        FUN_00982b00(local_8f0,1,4);
        FUN_009796a0(local_8c0);
        local_8dc = 0;
        local_8f8[0] = iVar2;
        FUN_00979ab0(local_8f8,local_8c0);
        local_40 = FUN_00953940;
        uVar8 = *(undefined8 *)(lVar9 + 0x28);
        uVar10 = FUN_00982110();
        lVar11 = FUN_009798c0(uVar8,uVar10,local_8f0,local_8c0);
        bVar16 = lVar11 != 0;
      }
      if (bVar16) {
        *(int *)(lVar9 + 0xb0) = iVar2;
        *(bool *)(lVar9 + 0xb4) = (param_1 & 0xfffffffd) != 0;
        *(int *)(lVar9 + 0xb8) = param_2;
        thunk_FUN_012aa7c6(lVar9 + 0xbc,param_3,0x4e);
        *(undefined8 *)(lVar9 + 0x110) = param_4;
      }
      if (2 < (int)param_1) {
        FUN_00979640(local_918);
        if (((iVar2 == DAT_0274bf88) || (iVar2 == DAT_0274bf94)) && (param_1 != 4)) {
          local_900 = 1;
        }
        else {
          local_900 = 0;
        }
        local_918[0] = iVar2;
        FUN_00953940(local_918);
      }
      goto LAB_0095390e;
    }
  }
  else {
    iVar4 = FUN_009549a0();
    iVar5 = FUN_00954a20();
    if (0 < iVar4 - iVar5) {
      piVar7 = &DAT_0274bf8c;
      if (bVar15) {
        piVar7 = &DAT_0274bf88;
      }
      if ((bool)((param_1 != 2 && iVar3 < iVar2) | bVar15)) goto LAB_0095374f;
    }
  }
  cVar1 = FUN_00b21010();
  if ((cVar1 != '\0') || (cVar1 = FUN_00b21030(), cVar1 != '\0')) {
    lVar9 = FUN_007756e0(1);
    bVar12 = (param_1 & 0xfffffffd) != 0 | 2;
    bVar13 = bVar12;
    if (lVar9 != 0) {
      iVar2 = FUN_00b81560(lVar9,param_3 + 8);
      bVar13 = 1;
      if (iVar2 == -1) {
        bVar13 = bVar12;
      }
    }
    FUN_00b21600(0,bVar14 || bVar16,bVar13,param_2,param_3,param_4);
  }
LAB_0095390e:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

