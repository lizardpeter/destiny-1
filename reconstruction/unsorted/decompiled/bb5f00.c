
void FUN_00bb5f00(long param_1,char param_2,undefined4 *param_3,byte *param_4)

{
  char cVar1;
  ushort uVar2;
  undefined4 uVar3;
  long lVar4;
  int iVar5;
  int *piVar6;
  undefined4 *puVar7;
  uint uVar8;
  
  *param_4 = *param_4 | 1;
  *(byte *)(param_3 + 1) = *(byte *)(param_3 + 1) | 1;
  *param_3 = *(undefined4 *)(param_1 + 0x3c);
  uVar3 = FUN_005916f0();
  param_3[0x490] = uVar3;
  uVar3 = FUN_003055b0();
  param_3[0x491] = uVar3;
  lVar4 = FUN_0074b390();
  param_3[2] = *(undefined4 *)(lVar4 + 0x10);
  param_3[3] = *(undefined4 *)(lVar4 + 0x18);
  *(undefined4 *)(param_4 + 0xc) = *param_3;
  FUN_00bb6080(param_1);
  uVar2 = *(ushort *)(param_3 + 1) & 0xfffd;
  if (param_2 != '\0') {
    uVar2 = *(ushort *)(param_3 + 1) | 2;
  }
  *(ushort *)(param_3 + 1) = uVar2;
  if ((uVar2 & 2) != 0) {
    param_3[4] = 0;
    piVar6 = (int *)(param_1 + 0x90);
    puVar7 = param_3 + 8;
    iVar5 = 0;
    do {
      if (*piVar6 != -1) {
        cVar1 = FUN_00ba86d0(piVar6,puVar7);
        if (cVar1 != '\0') {
          param_3[4] = param_3[4] | 1 << ((byte)iVar5 & 0x1f);
        }
      }
      piVar6 = piVar6 + 0x80;
      puVar7 = puVar7 + 0x38;
      iVar5 = iVar5 + 1;
    } while (iVar5 != 0x14);
    puVar7 = param_3 + 8;
    piVar6 = (int *)(param_1 + 0x98);
    uVar8 = 0;
    do {
      if (((piVar6[-2] != -1) && (*piVar6 != 0)) && (((uint)param_3[4] >> (uVar8 & 0x1f) & 1) != 0))
      {
        FUN_00bbbb70(puVar7,piVar6[-1]);
      }
      puVar7 = puVar7 + 0x38;
      piVar6 = piVar6 + 0x80;
      uVar8 = uVar8 + 1;
    } while (uVar8 != 0x14);
  }
  if (*(char *)(param_1 + 0x51) != '\0') {
    *(byte *)(param_3 + 1) = *(byte *)(param_3 + 1) | 4;
    *(undefined1 *)(param_1 + 0x51) = 0;
  }
  uVar3 = FUN_00ba4bc0();
  FUN_002ff570(param_3 + 0x72e,uVar3);
  uVar3 = FUN_00ba4bd0();
  FUN_002ff570(param_3 + 0x738,uVar3);
  FUN_00bb6160();
  FUN_00b9b720(param_3,0);
  return;
}

