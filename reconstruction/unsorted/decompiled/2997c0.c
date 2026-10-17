
void FUN_002997c0(long *param_1)

{
  long lVar1;
  undefined8 uVar2;
  long lVar3;
  undefined4 local_50 [2];
  undefined1 local_48 [40];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  if ((int)param_1[3] == 0) {
    lVar3 = param_1[0xd90];
    lVar1 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar1 = FUN_000694d0();
    }
    if (59999 < lVar1 - lVar3) {
      FUN_00240d00(local_48);
      uVar2 = (**(code **)(*param_1 + 0x10))(param_1);
      local_50[0] = 0;
      FUN_00299d10(param_1,uVar2,0x2f,*(undefined4 *)PTR_DAT_0191a470,local_48,0x24,local_50);
      lVar3 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar3 = FUN_000694d0();
      }
      param_1[0xd90] = lVar3;
    }
  }
  if (*DAT_01a1f100 != local_20) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

