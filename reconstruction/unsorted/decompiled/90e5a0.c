
void FUN_0090e5a0(int param_1,char param_2)

{
  byte *pbVar1;
  long lVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 *puVar6;
  char cVar7;
  int iVar8;
  undefined4 uVar9;
  undefined8 *puVar10;
  long lVar11;
  ulong uVar12;
  long lVar13;
  uint local_88 [18];
  long local_40;
  long local_38;
  
  puVar6 = DAT_0273eaa0;
  local_38 = *DAT_01a1f100;
  lVar2 = *(long *)(DAT_0273ea80 + 8);
  if ((char)DAT_0273ea90[0x2a] != '\0') {
    local_40 = *(long *)((long)DAT_0273ea90 + 0xa9);
    lVar13 = (ulong)(ushort)param_1 * 0x2af0;
    if (*(long *)(lVar2 + 0x620 + lVar13) == local_40) {
      *(undefined4 *)(DAT_0273eaa0 + 0x1c) = *(undefined4 *)(lVar2 + 0x38 + lVar13);
      thunk_FUN_012aa7c6(puVar6 + 5,lVar2 + 0x2870 + lVar13,0xb8);
      *(undefined4 *)((long)puVar6 + 0xe4) = 1;
      lVar13 = lVar2 + 400 + lVar13;
      iVar8 = FUN_00066dc0(lVar13);
      if (0 < iVar8) {
        puVar10 = (undefined8 *)FUN_004102d0(lVar13);
        uVar3 = *puVar10;
        uVar4 = puVar10[1];
        uVar5 = puVar10[3];
        puVar6[2] = puVar10[2];
        puVar6[3] = uVar5;
        *puVar6 = uVar3;
        puVar6[1] = uVar4;
        *(undefined1 *)(puVar6 + 4) = 1;
      }
    }
  }
  lVar13 = (ulong)(ushort)param_1 * 0x2af0;
  FUN_00254e60(lVar2 + 0x2a10 + lVar13,1);
  if (param_2 != '\0') {
    *(undefined4 *)(lVar2 + 0x648 + lVar13) = *(undefined4 *)(lVar2 + 0x644 + lVar13);
  }
  FUN_0066ad80(lVar2 + 0x1660 + lVar13);
  FUN_00bcf500(local_88);
  FUN_00bcf550(local_88,3,0,0);
  cVar7 = FUN_00bcf580(local_88);
  if (cVar7 != '\0') {
    do {
      cVar7 = FUN_00bcfad0(local_88[0]);
      if (cVar7 == '\0') {
        uVar12 = (ulong)((local_88[0] & 0x1fff) * DAT_02689800);
        uVar12 = (ulong)((*(uint *)(((uVar12 + DAT_026897f8) -
                                    (*(ulong *)(DAT_026897f8 + 8 + uVar12) & (long)DAT_02689818)) +
                                   0x68) & 0x1fff) * DAT_02689800);
        lVar11 = (DAT_026897f8 + uVar12) -
                 ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar12));
        if (*(int *)(lVar11 + 0x9e0) == param_1) {
          *(undefined4 *)(lVar11 + 0x9e0) = 0xffffffff;
        }
      }
      cVar7 = FUN_00bcf580(local_88);
    } while (cVar7 != '\0');
  }
  FUN_00911c50(param_1,0xffffffff,0,param_2);
  *(undefined8 *)(lVar2 + 0x64c + lVar13) = 0xffffffffffffffff;
  FUN_00b9f310(param_1);
  *(undefined4 *)(lVar2 + 0x628 + lVar13) = 0xffffffff;
  *(undefined8 *)(lVar2 + 0x620 + lVar13) = 0;
  *(undefined8 *)(lVar2 + 0x62c + lVar13) = 0xffffffffffffffff;
  FUN_00922ef0(param_1,0xffffffff);
  FUN_00923080(param_1,0xffffffff);
  FUN_00923590(param_1);
  pbVar1 = (byte *)(lVar2 + 0x610 + lVar13);
  *pbVar1 = *pbVar1 | 2;
  FUN_00302b20(*(undefined4 *)(lVar2 + 4 + lVar13));
  uVar9 = FUN_005916f0();
  *(undefined4 *)(lVar2 + 0x61c + lVar13) = uVar9;
  pbVar1 = (byte *)(lVar2 + 0x610 + lVar13);
  *pbVar1 = *pbVar1 & 0xfe;
  *DAT_0273ea90 = *DAT_0273ea90 + -1;
  FUN_0090a2c0(param_1);
  FUN_0090e120(0);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

