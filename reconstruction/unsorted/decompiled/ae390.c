
void FUN_000ae390(int param_1,long param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  short sVar7;
  undefined1 uVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  undefined4 local_3c;
  long local_38;
  long lVar8;
  
  local_38 = *DAT_01a1f100;
  if (0 < param_1) {
    sVar7 = 0;
    fVar10 = DAT_016136f4;
    do {
      lVar8 = (long)sVar7;
      if ((&DAT_01ad4eec)[lVar8 * 0x18] != '\0') {
        fVar1 = *(float *)(param_2 + 8 + lVar8 * 0xc);
        fVar2 = *(float *)(param_2 + 4 + lVar8 * 0xc);
        fVar3 = *(float *)(param_2 + lVar8 * 0xc);
        fVar12 = fVar2;
        fVar11 = fVar3;
        fVar13 = fVar1;
        if (((fVar3 < fVar10) && (fVar2 < fVar10)) && (fVar1 < fVar10)) {
          fVar4 = fVar3;
          if (fVar3 - fVar2 < 0.0) {
            fVar4 = fVar2;
          }
          if (fVar4 - fVar1 < 0.0) {
            fVar4 = fVar1;
          }
          fVar12 = fVar10;
          fVar11 = fVar10;
          fVar13 = fVar10;
          if (DAT_016136f8 < fVar4) {
            fVar10 = fVar10 / fVar4;
            fVar12 = fVar2 * fVar10;
            fVar11 = fVar3 * fVar10;
            fVar13 = fVar1 * fVar10;
          }
        }
        if (fVar12 < 0.0) {
          fVar12 = 0.0;
        }
        if (fVar13 < 0.0) {
          fVar13 = 0.0;
        }
        if (fVar11 < 0.0) {
          fVar11 = 0.0;
        }
        uVar5 = 0xff;
        uVar6 = 0xff;
        if (fVar13 + DAT_01613700 < 0.0) {
          uVar6 = (undefined1)(int)(fVar13 * DAT_016136fc);
        }
        uVar9 = 0xff;
        if (fVar12 + DAT_01613700 < 0.0) {
          uVar9 = (undefined1)(int)(fVar12 * DAT_016136fc);
        }
        if (fVar11 + DAT_01613700 < 0.0) {
          uVar5 = (undefined1)(int)(fVar11 * DAT_016136fc);
        }
        local_3c = (uint)CONCAT12(uVar6,CONCAT11(uVar9,uVar5));
        thunk_FUN_012ab106((&DAT_01ad4edc)[lVar8 * 6],&local_3c);
        fVar10 = DAT_016136f4;
      }
      sVar7 = sVar7 + 1;
    } while (sVar7 < param_1);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

