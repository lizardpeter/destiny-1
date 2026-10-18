
void FUN_00771b10(int param_1)

{
  int *piVar1;
  ulong uVar2;
  undefined4 uVar3;
  long lVar4;
  long lVar5;
  long lVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  
  lVar4 = FUN_00768060();
  if (lVar4 != 0) {
    lVar9 = (long)param_1;
    lVar8 = *(long *)(lVar4 + 0x13008 + lVar9 * 8);
    if (lVar8 != -1) {
      lVar5 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar5 = FUN_000694d0();
      }
      uVar2 = *(ulong *)(lVar4 + 0xfe58);
      param_1 = param_1 + 1;
      uVar7 = uVar2;
      if ((-1 < param_1) && (uVar7 = (long)param_1, (ulong)(long)param_1 < uVar2)) {
        uVar7 = uVar2;
      }
      *(ulong *)(lVar4 + 0xfe58) = uVar7;
      lVar6 = lVar9 * 0x10;
      *(undefined1 *)(lVar4 + 0xfe60 + lVar6) = 1;
      lVar8 = (long)*(int *)(lVar4 + 0xfe64 + lVar6) + (lVar5 - lVar8);
      uVar3 = 0x7fffffff;
      if (lVar8 < 0x80000000) {
        uVar3 = (undefined4)lVar8;
      }
      *(undefined4 *)(lVar4 + 0xfe64 + lVar6) = uVar3;
      *(undefined1 *)(lVar4 + 0xfe68 + lVar6) = 1;
      piVar1 = (int *)(lVar4 + 0xfe6c + lVar6);
      *piVar1 = *piVar1 + 1;
      *(undefined8 *)(lVar4 + 0x13008 + lVar9 * 8) = 0xffffffffffffffff;
    }
  }
  return;
}

