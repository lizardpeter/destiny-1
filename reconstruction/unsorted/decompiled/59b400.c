
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0059b400(undefined8 param_1,long param_2)

{
  undefined1 auVar1 [16];
  float fVar2;
  undefined4 uVar3;
  long lVar4;
  byte bVar5;
  float fVar6;
  float fVar7;
  
  lVar4 = FUN_0057f580();
  if (lVar4 != 0) {
    if (*(char *)(lVar4 + 0x11) == '\0') {
      bVar5 = *(byte *)(param_2 + 0x39) & 0xfe;
    }
    else {
      bVar5 = *(byte *)(param_2 + 0x39) | 1;
    }
    *(byte *)(param_2 + 0x39) = bVar5;
  }
  uVar3 = FUN_00b403e0();
  *(undefined4 *)(param_2 + 0x44) = uVar3;
  FUN_0076a940(param_2 + 0x48);
  fVar6 = (float)FUN_007683c0();
  *(int *)(param_2 + 0x7c) = (int)fVar6;
  fVar6 = (float)FUN_007683d0();
  *(int *)(param_2 + 0x80) = (int)fVar6;
  uVar3 = FUN_007683b0();
  *(undefined4 *)(param_2 + 0x84) = uVar3;
  fVar6 = (float)FUN_007683f0();
  *(int *)(param_2 + 0x88) = (int)fVar6;
  fVar6 = (float)FUN_00768400();
  *(int *)(param_2 + 0x8c) = (int)fVar6;
  fVar7 = (float)FUN_007683e0();
  fVar2 = DAT_0163f6ec;
  *(float *)(param_2 + 0x90) = fVar7;
  fVar6 = fVar7 + *(float *)(param_2 + 0x84);
  if (fVar6 <= fVar2) {
    *(undefined4 *)(param_2 + 0x84) = 0x3f000000;
    *(undefined4 *)(param_2 + 0x90) = 0x3f000000;
  }
  else {
    auVar1 = vandps_avx(ZEXT416((uint)(fVar6 + DAT_0163f6f0)),_DAT_0163f700);
    if (DAT_0163f6f4 <= auVar1._0_4_) {
      fVar6 = DAT_0163f6f8 / fVar6;
      *(float *)(param_2 + 0x84) = *(float *)(param_2 + 0x84) * fVar6;
      *(float *)(param_2 + 0x90) = fVar6 * fVar7;
    }
  }
  return;
}

