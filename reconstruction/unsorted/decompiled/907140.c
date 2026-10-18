
void FUN_00907140(long param_1)

{
  float fVar1;
  uint uVar2;
  int *piVar3;
  int iVar4;
  uint uVar5;
  long lVar6;
  
  if ((((DAT_0273dcd0 != (char *)0x0) && (DAT_0273dcd0[0x2b48] != '\0')) && (*DAT_0273dcd0 == '\0'))
     && (DAT_0273dcd0[1] != '\0')) {
    lVar6 = 0;
    do {
      if ((*(uint *)(param_1 + 0x10) >> ((uint)lVar6 & 0x1f) & 1) != 0) {
        fVar1 = *(float *)(param_1 + 0x2c + lVar6 * 0xe0);
        uVar2 = 1;
        if ((fVar1 <= 0.0) && (uVar2 = 0, fVar1 < 0.0)) {
          uVar2 = 2;
        }
        uVar5 = 4;
        if (*(float *)(param_1 + 0x28 + lVar6 * 0xe0) <= 0.0) {
          uVar5 = 8;
        }
        iVar4 = 0;
        do {
          piVar3 = (int *)FUN_003055a0();
          *piVar3 = *piVar3 * 0x19660d + 0x3c6ef35f;
          iVar4 = iVar4 + 1;
        } while (iVar4 < (int)(uVar5 | uVar2));
      }
      lVar6 = lVar6 + 1;
    } while ((int)lVar6 != 0x14);
  }
  return;
}

