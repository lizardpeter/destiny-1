
void FUN_002f2230(void)

{
  uint *puVar1;
  undefined8 *puVar2;
  byte bVar3;
  char cVar4;
  int iVar5;
  undefined4 uVar6;
  undefined8 uVar7;
  undefined8 *puVar8;
  uint uVar9;
  
  switch(*(undefined4 *)(DAT_026881b8 + 2)) {
  case 1:
    cVar4 = FUN_0023a4d0(DAT_026881b8 + 3);
    if (cVar4 == '\0') {
      cVar4 = FUN_0023a4f0(DAT_026881b8 + 3);
      puVar8 = DAT_026881b8;
      if (cVar4 == '\0') {
        FUN_00071db0(DAT_026881b8 + 3);
        *(undefined4 *)((long)DAT_026881b8 + 0x14) = 3;
        *(undefined4 *)(DAT_026881b8 + 2) = 0;
      }
      else {
        uVar6 = (**(code **)(*(long *)*DAT_026881b8 + 0x10))();
        *(undefined4 *)(puVar8 + 10) = uVar6;
        uVar7 = FUN_00239ef0(0x4a0,0,0);
        puVar8[0xb] = uVar7;
        thunk_FUN_012aa986(uVar7,0,0x4a0);
        *(undefined8 *)puVar8[0xb] = 0x4a0;
        *(undefined4 *)(puVar8 + 0xd) = 0;
        FUN_0023af20(DAT_026881b8 + 7);
        *(undefined4 *)(DAT_026881b8 + 2) = 2;
      }
    }
    break;
  case 2:
    cVar4 = FUN_0023a4d0(DAT_026881b8 + 7);
    if (cVar4 == '\0') {
      bVar3 = FUN_0023a4f0(DAT_026881b8 + 7);
      puVar8 = DAT_026881b8;
      if (DAT_026881b8[0xb] != 0) {
        FUN_00239e50();
        puVar8[0xb] = 0;
      }
      if (puVar8[0xc] != 0) {
        FUN_00239e50();
        puVar8[0xc] = 0;
      }
      cVar4 = FUN_0023a4f0(DAT_026881b8 + 7);
      FUN_00071db0(DAT_026881b8 + 7);
      *(uint *)((long)DAT_026881b8 + 0x14) = cVar4 == '\0' | 2;
      *(uint *)(DAT_026881b8 + 2) = (uint)bVar3 + (uint)bVar3 * 2;
    }
    break;
  case 3:
    cVar4 = FUN_002f1410();
    if (cVar4 != '\0') {
      uVar9 = 0;
      do {
        if (3 < uVar9) goto LAB_002f23ff;
        puVar8 = (undefined8 *)FUN_002f1770(uVar9);
        uVar9 = uVar9 + 1;
      } while (*(int *)(puVar8 + 5) != 1);
      DAT_026881b8[0x14] = *puVar8;
      FUN_0023af20(DAT_026881b8 + 0xe);
      *(undefined4 *)(puVar8 + 5) = 2;
      *(undefined4 *)(DAT_026881b8 + 2) = 4;
LAB_002f23ff:
      if ((*(int *)(DAT_026881b8 + 2) == 3) && (cVar4 = FUN_002f15f0(), cVar4 == '\0')) {
        uVar9 = 0;
        do {
          puVar8 = (undefined8 *)FUN_002f1770(uVar9);
          if (*(int *)(puVar8 + 5) == 3) {
            cVar4 = FUN_0008f800(puVar8 + 3,0x7f);
            if (cVar4 == '\0') {
              iVar5 = FUN_0008f950(puVar8 + 3,0x7f);
              puVar1 = (uint *)((long)puVar8 + (long)(iVar5 >> 5) * 4 + 0x18);
              *puVar1 = *puVar1 & ~(1 << ((byte)iVar5 & 0x1f));
              uVar6 = FUN_002f14d0(iVar5);
              puVar2 = DAT_026881b8;
              *(undefined4 *)(DAT_026881b8 + 0x19) = uVar6;
              *(undefined4 *)((long)puVar2 + 0xcc) = 0xffffffff;
              puVar2[0x18] = *puVar8;
              FUN_0023af20(DAT_026881b8 + 0x15);
              *(undefined4 *)(DAT_026881b8 + 2) = 5;
              return;
            }
          }
          uVar9 = uVar9 + 1;
        } while (uVar9 < 4);
      }
    }
    break;
  case 4:
    cVar4 = FUN_0023a4d0(DAT_026881b8 + 0xe);
    if (cVar4 != '\0') {
      return;
    }
    FUN_002f25b0(DAT_026881b8 + 0xe);
    goto LAB_002f2495;
  case 5:
    cVar4 = FUN_0023a4d0(DAT_026881b8 + 0x15);
    if (cVar4 != '\0') {
      return;
    }
    FUN_002f2650(DAT_026881b8 + 0x15);
LAB_002f2495:
    *(undefined4 *)(DAT_026881b8 + 2) = 3;
  }
  return;
}

