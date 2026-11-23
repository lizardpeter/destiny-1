
void FUN_0057f9d0(long param_1,long *param_2,int param_3,undefined8 *param_4)

{
  byte bVar1;
  ushort uVar2;
  undefined8 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  long *plVar7;
  long lVar8;
  long lVar9;
  
  plVar7 = (long *)(param_1 + 0x14);
  iVar4 = 0;
  do {
    iVar5 = iVar4;
    iVar6 = -1;
    if (0 < iVar5) break;
    lVar8 = *plVar7;
    plVar7 = plVar7 + 1;
    iVar4 = iVar5 + 1;
    iVar6 = iVar5;
  } while (*param_2 != lVar8);
  lVar9 = (long)param_3 * 0x68;
  param_4[0xb] = 0;
  param_4[10] = 0;
  param_4[9] = 0;
  param_4[8] = 0;
  param_4[7] = 0;
  param_4[6] = 0;
  param_4[5] = 0;
  param_4[4] = 0;
  param_4[3] = 0;
  param_4[2] = 0;
  param_4[1] = 0;
  *param_4 = 0;
  lVar8 = (long)iVar6;
  if (*(short *)(param_1 + lVar9 + 0x8a + lVar8 * 2) == 0) {
    *param_4 = 0;
    FUN_002b8260(param_4 + 1);
    param_4[7] = 0;
    FUN_0006c520((long)param_4 + 0x41);
    *(undefined2 *)((long)param_4 + 0x5a) = 0;
    *(undefined8 *)((long)param_4 + 0x52) = 0;
    *(undefined1 *)(param_4 + 8) = 0;
  }
  else {
    *param_4 = *(undefined8 *)(param_1 + 0x28 + lVar9);
    uVar3 = *(undefined8 *)(param_1 + 0x50 + lVar9);
    param_4[6] = *(undefined8 *)(param_1 + 0x58 + lVar9);
    param_4[5] = uVar3;
    param_4[4] = *(undefined8 *)(param_1 + 0x48 + lVar9);
    param_4[3] = *(undefined8 *)(param_1 + 0x40 + lVar9);
    uVar3 = *(undefined8 *)(param_1 + 0x30 + lVar9);
    param_4[2] = *(undefined8 *)(param_1 + 0x38 + lVar9);
    param_4[1] = uVar3;
    param_4[7] = *(undefined8 *)(param_1 + 0x60 + lVar9);
    FUN_002483f0((long)param_4 + 0x41,param_1 + 0x68 + lVar9);
    uVar2 = *(ushort *)(param_1 + lVar9 + 0x8a + lVar8 * 2);
    *(ushort *)((long)param_4 + 0x5a) = uVar2;
    *(undefined8 *)((long)param_4 + 0x52) = *(undefined8 *)(param_1 + 0x14 + lVar8 * 8);
    bVar1 = *(byte *)(param_1 + 0x8c + lVar9);
    *(byte *)(param_4 + 8) = bVar1;
    if ((uVar2 & 1) == 0) {
      *(byte *)(param_4 + 8) = bVar1 & 0xf7;
    }
  }
  return;
}

