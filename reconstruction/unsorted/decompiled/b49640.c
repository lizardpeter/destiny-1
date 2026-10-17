
undefined8 FUN_00b49640(char *param_1,undefined8 param_2)

{
  int *piVar1;
  byte *pbVar2;
  long lVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined8 uVar7;
  undefined *puVar8;
  
  lVar3 = DAT_0282ee90;
  uVar7 = 0;
  if (*param_1 != '\0') {
    iVar5 = FUN_000a0430(param_2);
    pbVar2 = (byte *)(lVar3 + 2 + (long)iVar5 * 0xc);
    *pbVar2 = *pbVar2 | 1;
    uVar4 = DAT_0282eeb8;
    FUN_000f2c60(DAT_0282eeb8,0);
    puVar8 = &DAT_0282ee88;
    iVar6 = -1;
    do {
      iVar6 = iVar6 + 1;
      if (6 < iVar6) goto LAB_00b496b7;
      piVar1 = (int *)(puVar8 + 100);
      puVar8 = puVar8 + 0x38;
    } while (*piVar1 != *(int *)(lVar3 + 8 + (long)iVar5 * 0xc));
    FUN_00b48000();
LAB_00b496b7:
    FUN_000f2dc0(uVar4,0);
    uVar7 = 1;
  }
  return uVar7;
}

