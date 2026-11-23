
void FUN_0058b570(undefined8 param_1)

{
  char cVar1;
  int iVar2;
  undefined4 local_b0 [2];
  long local_a8;
  long local_a0 [8];
  byte local_60;
  undefined2 local_46;
  undefined1 local_40 [16];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  cVar1 = FUN_00906f70();
  if (cVar1 == '\0') {
    local_a8 = FUN_00587520();
    local_a0[0] = 0;
    if (local_a8 != 0) {
      iVar2 = 0;
      thunk_FUN_012aa986(&DAT_026bc640,0,0x150);
      local_b0[0] = 0x15;
      FUN_0057f860(local_40,&local_a8,local_b0);
      FUN_0057f880(local_40);
      cVar1 = FUN_001d1b20(local_40);
      if (cVar1 != '\0') {
        do {
          FUN_0057f9b0(local_40,local_a0);
          if ((local_60 & 0x11) != 0) {
            DAT_026bc640 = DAT_026bc640 + 1;
          }
          if ((local_60 & 1) != 0) {
            (&DAT_026bc650)[(long)iVar2 * 2] = local_a0[0];
            (&DAT_026bc658)[(long)iVar2 * 8] = local_46;
            iVar2 = iVar2 + 1;
            if (local_a0[0] != 0) {
              DAT_026bc648 = DAT_026bc648 + 1;
            }
          }
          FUN_0057f920(local_40);
          cVar1 = FUN_001d1b20(local_40);
        } while (cVar1 != '\0');
      }
      FUN_0006a350(&DAT_026bc650,0x14,0x10,FUN_0058b740,0);
      iVar2 = thunk_FUN_012aa826(&DAT_026bc640,param_1,0x150);
      if (iVar2 != 0) {
        FUN_00300230(0x2b,*(undefined4 *)PTR_DAT_019e4d08,&DAT_026bc640);
      }
    }
  }
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

