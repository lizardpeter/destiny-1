
void FUN_000ae260(char param_1,int param_2,undefined8 param_3,long param_4)

{
  int iVar1;
  short sVar2;
  long lVar3;
  undefined2 local_3a;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (0 < param_2) {
    if (param_1 == '\0') {
      sVar2 = 0;
      do {
        lVar3 = (long)sVar2;
        if ((&DAT_01ad4eec)[lVar3 * 0x18] != '\0') {
          local_3a = CONCAT11((char)(int)(DAT_016136e8 * *(float *)(param_4 + 4 + lVar3 * 0x10)),
                              (char)(int)(DAT_016136e8 * *(float *)(param_4 + lVar3 * 0x10)));
          thunk_FUN_012ab0f6((&DAT_01ad4edc)[lVar3 * 6],&local_3a);
        }
        sVar2 = sVar2 + 1;
      } while (sVar2 < param_2);
    }
    else {
      sVar2 = 1;
      do {
        if ((&DAT_01ad4eec)[(long)(short)(sVar2 + -1) * 0x18] != '\0') {
          local_3a = 0;
          thunk_FUN_012ab0f6((&DAT_01ad4edc)[(long)(short)(sVar2 + -1) * 6],&local_3a);
        }
        iVar1 = (int)sVar2;
        sVar2 = sVar2 + 1;
      } while (iVar1 < param_2);
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

