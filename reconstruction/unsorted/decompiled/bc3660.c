
undefined8 FUN_00bc3660(undefined8 param_1,long param_2)

{
  undefined4 uVar1;
  byte *pbVar2;
  uint *puVar3;
  long lVar4;
  uint *puVar5;
  uint3 uVar6;
  char cVar7;
  byte *pbVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  uint uVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  byte bVar15;
  bool bVar16;
  undefined8 *local_60;
  undefined **local_58;
  undefined8 uStack_50;
  undefined8 local_48;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar10 = *(undefined8 *)(param_2 + 0x30);
  uStack_50 = 0;
  local_58 = &PTR_FUN_01943f30;
  local_48 = 0xffffffff;
  if (*(long *)(param_2 + 0x38) != 0) {
    FUN_006eca80(&local_58,*(long *)(param_2 + 0x38),*(undefined4 *)(param_2 + 0x58));
    pbVar2 = *(byte **)(param_2 + 8);
    uVar11 = (*(int *)(pbVar2 + 8) << 0x12) >> 0x12;
    if ((uVar11 & 0xfffffffe) == 0xfffffffe) {
      if (0 < ((*(int *)(pbVar2 + 8) << 4) >> 0x12) + 0x1f >> 5) {
        pbVar8 = *(byte **)pbVar2;
LAB_00bc370d:
        if ((*pbVar8 & 1) != 0) {
          cVar7 = FUN_002c8290(*(undefined4 *)PTR_DAT_0191a858,pbVar2,0,uVar10,&local_58);
          uVar9 = 0;
          if (cVar7 == '\0') goto LAB_00bc398c;
        }
      }
    }
    else {
      pbVar8 = pbVar2;
      if (uVar11 == 0) goto LAB_00bc370d;
    }
  }
  local_60 = (undefined8 *)(param_2 + 8);
  cVar7 = *(char *)(param_2 + 0x54);
  puVar3 = *(uint **)(param_2 + 0x10);
  lVar4 = *(long *)(param_2 + 0x48);
  puVar5 = (uint *)*local_60;
  uVar11 = (int)(puVar5[2] << 0x12) >> 0x12;
  if ((uVar11 & 0xfffffffe) == 0xfffffffe) {
    bVar15 = 0;
    if (0 < ((int)(puVar5[2] << 4) >> 0x12) + 0x1f >> 5) {
      bVar15 = **(byte **)puVar5;
LAB_00bc378f:
      bVar15 = bVar15 & 1;
    }
  }
  else {
    bVar15 = 0;
    if (uVar11 == 0) {
      bVar15 = (byte)*puVar5;
      goto LAB_00bc378f;
    }
  }
  uVar1 = *(undefined4 *)PTR_DAT_0191a858;
  if (*(uint *)(lVar4 + 0x30) < 0x40) {
    *(uint *)(lVar4 + 0x30) = *(uint *)(lVar4 + 0x30) + 1;
    *(int *)(lVar4 + 0x24) = *(int *)(lVar4 + 0x24) + 1;
    *(ulong *)(lVar4 + 0x28) = *(long *)(lVar4 + 0x28) * 2 | (ulong)bVar15;
  }
  else {
    FUN_000733a0(lVar4,bVar15,1);
  }
  if (bVar15 != 0) {
    if (cVar7 == '\0') {
      FUN_002c8120(uVar1,puVar5,0,uVar10,lVar4,0);
      uVar11 = puVar3[2];
      uVar13 = (int)(uVar11 << 0x12) >> 0x12;
      if (((uVar13 & 0xfffffffe) == 0xfffffffe) ||
         ((uVar14 = *puVar3, uVar13 != 0 && (bVar16 = uVar14 != 0, uVar14 = 0, bVar16)))) {
        if ((uVar11 & 0x3fff) != 0x3ffe) {
          thunk_FUN_002c72d0(puVar3,1);
        }
        **(uint **)puVar3 = **(uint **)puVar3 | 1;
        uVar11 = puVar3[2];
      }
      else {
        *puVar3 = uVar14 | 1;
        uVar11 = uVar11 & 0xffffc000;
        puVar3[2] = uVar11;
      }
      if ((int)(uVar11 << 4) >> 0x12 < 1) {
        puVar3[2] = uVar11 & 0xf0003fff | 0x4000;
      }
    }
    else {
      FUN_0023a4a0(lVar4,uVar1);
      iVar12 = puVar5[2] << 0x12;
      uVar11 = iVar12 >> 0x12;
      uVar13 = uVar11 & 0xfffffffe;
      if (uVar13 == 0xfffffffe) {
        uVar6 = (uint3)(iVar12 >> 0x1a);
        uVar11 = (uint)uVar6 << 8;
        if (0 < ((int)(puVar5[2] << 4) >> 0x12) + 0x1f >> 5) {
          uVar11 = CONCAT31(uVar6,**(undefined1 **)puVar5) & 0xffffff01;
        }
        uVar14 = uVar11 & 0xff;
      }
      else {
        uVar14 = 0;
        if (uVar11 == 0) {
          uVar14 = *puVar5 & 1;
        }
      }
      FUN_0023a4a0(lVar4,uVar14,uVar13,uVar11);
      FUN_002c8120(uVar1,puVar5,0,uVar10,lVar4,1);
      uVar11 = puVar3[2];
      uVar13 = (int)(uVar11 << 0x12) >> 0x12;
      if (((uVar13 & 0xfffffffe) == 0xfffffffe) ||
         ((uVar14 = *puVar3, uVar13 != 0 && (bVar16 = uVar14 != 0, uVar14 = 0, bVar16)))) {
        if ((uVar11 & 0x3fff) != 0x3ffe) {
          thunk_FUN_002c72d0(puVar3,1);
        }
        **(uint **)puVar3 = **(uint **)puVar3 | 1;
        uVar11 = puVar3[2];
      }
      else {
        *puVar3 = uVar14 | 1;
        uVar11 = uVar11 & 0xffffc000;
        puVar3[2] = uVar11;
      }
      if ((int)(uVar11 << 4) >> 0x12 < 1) {
        puVar3[2] = uVar11 & 0xf0003fff | 0x4000;
      }
      FUN_0023a4a0(lVar4);
      FUN_0023a4a0(lVar4);
    }
  }
  FUN_011c1510(*(undefined8 *)(param_2 + 0x10),*local_60);
  uVar9 = 1;
LAB_00bc398c:
  if (*DAT_01a1f100 != local_38) {
    uVar10 = thunk_FUN_012aa7f6();
    return uVar10;
  }
  return uVar9;
}

