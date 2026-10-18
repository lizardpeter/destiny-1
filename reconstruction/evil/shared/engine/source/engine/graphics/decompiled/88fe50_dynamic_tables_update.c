
ulong FUN_0088fe50(long param_1,long param_2,long param_3)

{
  undefined4 uVar1;
  long lVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  char cVar10;
  long lVar11;
  ulong uVar12;
  int iVar13;
  long lVar14;
  int iVar15;
  int local_44;
  long local_40;
  ulong local_38;
  
  local_38 = *DAT_01a1f100;
  iVar13 = *(int *)(param_1 + 8);
  iVar13 = (iVar13 + 1) - ((iVar13 + 1) - (iVar13 + 1 >> 0x1f) & 0xfffffffeU);
  *(int *)(param_1 + 8) = iVar13;
  iVar15 = *(int *)(param_1 + 0x14);
  *(uint *)(param_1 + 0x14) = (iVar15 + 1) - ((iVar15 + 1) - (iVar15 + 1 >> 0x1f) & 0xfffffffeU);
  uVar1 = *(undefined4 *)(param_1 + (long)iVar13 * 4);
  lVar2 = *(long *)(param_2 + 8);
  local_40 = 0;
  local_44 = 0;
  cVar10 = FUN_00818f80(uVar1,1,&local_40,&local_44);
  if (cVar10 != '\0') {
    FUN_00818dd0(uVar1);
    lVar11 = local_40;
    iVar13 = local_44;
    lVar14 = 0;
    iVar15 = 0;
    do {
      thunk_FUN_012aa7c6(lVar11 + iVar15,lVar2 + lVar14,0x200);
      iVar15 = iVar15 + iVar13;
      lVar14 = lVar14 + 0x200;
    } while ((short)lVar14 != 0x4000);
    FUN_00818fa0(uVar1);
  }
  uVar1 = *(undefined4 *)(param_1 + 0xc + (long)*(int *)(param_1 + 0x14) * 4);
  lVar2 = *(long *)(param_3 + 8);
  local_40 = 0;
  local_44 = 0;
  cVar10 = FUN_00818f80(uVar1,1,&local_40);
  if (cVar10 != '\0') {
    FUN_00818dd0(uVar1);
    lVar11 = 0;
    iVar13 = 0;
    do {
      uVar3 = *(undefined8 *)(lVar2 + lVar11);
      uVar4 = *(undefined8 *)(lVar2 + 8 + lVar11);
      uVar5 = *(undefined8 *)(lVar2 + 0x10 + lVar11);
      uVar6 = *(undefined8 *)(lVar2 + 0x18 + lVar11);
      uVar7 = *(undefined8 *)(lVar2 + 0x20 + lVar11);
      uVar8 = *(undefined8 *)(lVar2 + 0x28 + lVar11);
      uVar9 = *(undefined8 *)(lVar2 + 0x30 + lVar11);
      lVar14 = (long)iVar13;
      *(undefined8 *)(local_40 + 0x38 + lVar14) = *(undefined8 *)(lVar2 + 0x38 + lVar11);
      *(undefined8 *)(local_40 + 0x30 + lVar14) = uVar9;
      *(undefined8 *)(local_40 + 0x28 + lVar14) = uVar8;
      *(undefined8 *)(local_40 + 0x20 + lVar14) = uVar7;
      *(undefined8 *)(local_40 + 0x18 + lVar14) = uVar6;
      *(undefined8 *)(local_40 + 0x10 + lVar14) = uVar5;
      *(undefined8 *)(local_40 + 8 + lVar14) = uVar4;
      *(undefined8 *)(local_40 + lVar14) = uVar3;
      iVar13 = iVar13 + local_44;
      lVar11 = lVar11 + 0x40;
    } while ((short)lVar11 != 0x800);
    FUN_00818fa0(uVar1);
  }
  if (*DAT_01a1f100 == local_38) {
    return *DAT_01a1f100 & 0xffffffffffffff00;
  }
  uVar12 = thunk_FUN_012aa7f6();
  return uVar12;
}

