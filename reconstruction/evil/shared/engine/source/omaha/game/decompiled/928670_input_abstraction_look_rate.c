
void FUN_00928670(float param_1,long param_2,float *param_3,char param_4,float *param_5)

{
  float fVar1;
  float *pfVar2;
  float fVar3;
  float fVar4;
  
  pfVar2 = (float *)(param_2 + 0x2d0);
  if (param_4 != '\0') {
    pfVar2 = (float *)(param_2 + 0x2d8);
  }
  fVar3 = pfVar2[1];
  fVar4 = *(float *)(param_2 + 0x2cc);
  if ((*(char *)(param_2 + 0x2a0) != '\0') && (DAT_0166b8d0 < param_1)) {
    fVar3 = fVar3 + *pfVar2 / param_1;
    fVar4 = fVar4 + *(float *)(param_2 + 0x2c8) / param_1;
  }
  fVar1 = param_3[1];
  *param_5 = fVar4 * *param_3;
  param_5[1] = fVar3 * fVar1;
  return;
}

