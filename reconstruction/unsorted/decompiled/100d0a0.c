
ulong FUN_0100d0a0(long *param_1,int param_2,undefined8 *param_3)

{
  undefined8 *puVar1;
  short sVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 in_RAX;
  ulong uVar5;
  long lVar6;
  long lVar7;
  short sVar8;
  
  lVar6 = *param_1;
  sVar2 = (short)param_1[1];
  uVar5 = CONCAT62((int6)((ulong)in_RAX >> 0x10),sVar2);
  lVar7 = (long)*(int *)((long)param_1 + 0xc);
  sVar8 = sVar2;
  if ((lVar7 != -1) && (sVar8 = -1, sVar2 < *(short *)(lVar6 + 0x2bd1e + lVar7 * 4))) {
    uVar5 = (ulong)sVar2;
    sVar8 = *(short *)(lVar6 + 0x2a51c + ((long)*(short *)(lVar6 + 0x2bd1c + lVar7 * 4) + uVar5) * 2
                      );
  }
  param_3[1] = 0;
  *param_3 = 0;
  *(undefined4 *)param_3 = 0xffffffff;
  *(undefined4 *)(param_3 + 2) = 0xffffffff;
  uVar5 = uVar5 & 0xffffffffffffff00;
  if (sVar8 != -1) {
    lVar6 = lVar6 + (long)sVar8 * 0x38;
    if (*(int *)(lVar6 + 0x520 + (long)param_2 * 0x18) != -1) {
      puVar1 = (undefined8 *)(lVar6 + 0x520 + (long)param_2 * 0x18);
      *(undefined4 *)(param_3 + 2) = *(undefined4 *)(puVar1 + 2);
      uVar3 = *puVar1;
      uVar4 = puVar1[1];
      param_3[1] = uVar4;
      *param_3 = uVar3;
      uVar5 = CONCAT71((int7)((ulong)uVar4 >> 8),1);
    }
  }
  return uVar5;
}

