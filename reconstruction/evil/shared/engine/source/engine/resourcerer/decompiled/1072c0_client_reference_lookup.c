
ulong FUN_001072c0(int param_1,int param_2,undefined8 *param_3)

{
  undefined8 *puVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  ulong uVar4;
  long lVar5;
  short sVar6;
  
  lVar5 = 0;
  uVar4 = (ulong)DAT_025d6ff8;
  if (uVar4 != 0) {
    uVar4 = uVar4 * DAT_01ad5010;
    lVar5 = *(long *)(&DAT_01ad5030 + uVar4 + DAT_01ad5000);
  }
  sVar6 = 0;
  if (param_1 != -1) {
    uVar4 = (ulong)param_1;
    sVar6 = -1;
    if (0 < *(short *)(lVar5 + 0x2bd1e + uVar4 * 4)) {
      uVar4 = (ulong)*(short *)(lVar5 + 0x2bd1c + uVar4 * 4);
      sVar6 = *(short *)(lVar5 + 0x2a51c + uVar4 * 2);
    }
  }
  param_3[1] = 0;
  *param_3 = 0;
  *(undefined4 *)param_3 = 0xffffffff;
  *(undefined4 *)(param_3 + 2) = 0xffffffff;
  uVar4 = uVar4 & 0xffffffffffffff00;
  if (sVar6 != -1) {
    lVar5 = lVar5 + (long)sVar6 * 0x38;
    if (*(int *)(lVar5 + 0x520 + (long)param_2 * 0x18) != -1) {
      puVar1 = (undefined8 *)(lVar5 + 0x520 + (long)param_2 * 0x18);
      *(undefined4 *)(param_3 + 2) = *(undefined4 *)(puVar1 + 2);
      uVar2 = *puVar1;
      uVar3 = puVar1[1];
      param_3[1] = uVar3;
      *param_3 = uVar2;
      uVar4 = CONCAT71((int7)((ulong)uVar3 >> 8),1);
    }
  }
  return uVar4;
}

