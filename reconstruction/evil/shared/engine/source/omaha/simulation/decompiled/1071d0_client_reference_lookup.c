
ulong FUN_001071d0(int *param_1,int param_2,undefined8 *param_3)

{
  undefined8 uVar1;
  undefined8 uVar2;
  int *piVar3;
  ulong uVar4;
  ulong uVar5;
  int *piVar6;
  int iVar7;
  int *piVar8;
  
  piVar8 = (int *)0x0;
  if ((ulong)DAT_025d6ff8 != 0) {
    piVar8 = *(int **)(&DAT_01ad5030 + (ulong)DAT_025d6ff8 * DAT_01ad5010 + DAT_01ad5000);
  }
  param_3[1] = 0;
  *param_3 = 0;
  *(undefined4 *)param_3 = 0xffffffff;
  *(undefined4 *)(param_3 + 2) = 0xffffffff;
  uVar4 = FUN_001076c0(param_1);
  uVar5 = uVar4 & 0xffffffffffffff00;
  if ((char)uVar4 != '\0') {
    iVar7 = 0;
    piVar6 = piVar8;
    do {
      piVar3 = piVar6;
      piVar6 = piVar3 + 5;
      if (piVar8[2] <= iVar7) {
        return uVar5;
      }
      iVar7 = iVar7 + 1;
    } while (*piVar6 != *param_1);
    if (iVar7 != 0) {
      iVar7 = (int)*(short *)((long)param_1 + 6) + piVar3[4];
      if (piVar8[(long)iVar7 * 0xe + (long)param_2 * 6 + 0x148] != -1) {
        piVar8 = piVar8 + (long)iVar7 * 0xe + (long)param_2 * 6 + 0x148;
        *(int *)(param_3 + 2) = piVar8[4];
        uVar1 = *(undefined8 *)piVar8;
        uVar2 = *(undefined8 *)(piVar8 + 2);
        param_3[1] = uVar2;
        *param_3 = uVar1;
        uVar5 = CONCAT71((int7)((ulong)uVar2 >> 8),1);
      }
    }
  }
  return uVar5;
}

