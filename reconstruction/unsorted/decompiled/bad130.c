
void FUN_00bad130(undefined8 param_1)

{
  char cVar1;
  long lVar2;
  int iVar3;
  long local_d08;
  undefined1 local_d00 [20];
  undefined4 local_cec;
  int local_ce0;
  int local_cd0;
  undefined1 local_c28 [3072];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  lVar2 = thunk_FUN_00aeacd0();
  if (*(int *)(lVar2 + 8) != 1) {
    local_cec = 1;
    FUN_00072240(local_d00,local_c28,0xc00);
    FUN_000723b0(local_d00,1);
    FUN_00ba3ee0(local_d00,param_1);
    FUN_00072560(local_d00,0);
    cVar1 = FUN_00072210(local_d00);
    if (cVar1 == '\0') {
      iVar3 = (int)(((uint)(local_ce0 + 7 + local_cd0 >> 0x1f) >> 0x1d) + 7 + local_ce0 + local_cd0)
              >> 3;
      local_d08 = 0;
      FUN_00300b00(0xc,iVar3,&local_d08);
      if (local_d08 == 0) {
        cVar1 = FUN_005915a0();
        if (cVar1 != '\0') {
          cVar1 = FUN_00591b30();
          if (cVar1 == '\0') {
            FUN_00591b60();
          }
        }
      }
      else {
        thunk_FUN_012aa7c6(*(undefined8 *)(local_d08 + 8),local_c28,(long)iVar3);
        FUN_00300b90(local_d08);
      }
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

