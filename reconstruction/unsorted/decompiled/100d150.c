
ulong FUN_0100d150(long *param_1,undefined8 *param_2)

{
  undefined8 *puVar1;
  short sVar2;
  long lVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  ulong uVar6;
  ulong uVar7;
  short sVar8;
  long lVar9;
  
  uVar6 = FUN_0100cef0();
  uVar7 = uVar6 & 0xffffffffffffff00;
  if (uVar6 != 0) {
    lVar3 = *param_1;
    sVar2 = (short)param_1[1];
    lVar9 = (long)*(int *)((long)param_1 + 0xc);
    sVar8 = sVar2;
    if ((lVar9 != -1) && (sVar8 = -1, sVar2 < *(short *)(lVar3 + 0x2bd1e + lVar9 * 4))) {
      sVar8 = *(short *)(lVar3 + 0x2a51c +
                        ((long)*(short *)(lVar3 + 0x2bd1c + lVar9 * 4) + (long)sVar2) * 2);
    }
    param_2[1] = 0;
    *param_2 = 0;
    *(undefined4 *)param_2 = 0xffffffff;
    *(undefined4 *)(param_2 + 2) = 0xffffffff;
    if ((sVar8 != -1) && (*(int *)(lVar3 + 0x520 + (long)sVar8 * 0x38) != -1)) {
      puVar1 = (undefined8 *)(lVar3 + 0x520 + (long)sVar8 * 0x38);
      *(undefined4 *)(param_2 + 2) = *(undefined4 *)(puVar1 + 2);
      uVar4 = *puVar1;
      uVar5 = puVar1[1];
      param_2[1] = uVar5;
      *param_2 = uVar4;
      uVar7 = CONCAT71((int7)((ulong)uVar5 >> 8),1);
    }
  }
  return uVar7;
}

