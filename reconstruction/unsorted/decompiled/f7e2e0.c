
ulong FUN_00f7e2e0(byte *param_1)

{
  uint uVar1;
  int iVar2;
  ulong uVar3;
  undefined8 local_a0;
  undefined8 uStack_98;
  undefined8 uStack_90;
  undefined8 uStack_88;
  undefined8 local_80;
  undefined8 local_78;
  undefined8 local_70;
  undefined8 local_60;
  int iStack_58;
  int iStack_54;
  undefined4 uStack_50;
  int iStack_4c;
  undefined8 uStack_48;
  undefined8 local_40;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  uVar1 = 0;
  if ((*(uint *)(param_1 + 4) & 1) != 0) {
    uVar1 = FUN_00f7d5d0(*(uint *)(param_1 + 4) & 1,4);
    local_40 = 0;
    _iStack_58 = CONCAT44((*(uint *)(param_1 + 0x18) >> 8 & 0x3ff8) + 8,
                          (*(uint *)(param_1 + 0x18) & 0x7ff) * 8 + 8);
    uStack_48 = 0;
    local_60 = (ulong)uVar1 << 0x20;
    _uStack_50 = CONCAT44(1 << (*param_1 >> 2 & 3),1);
    iVar2 = FUN_00f85430((long)&local_40 + 4,5,0);
    uVar1 = 0;
    if (iVar2 == 0) {
      local_60 = CONCAT44(local_60._4_4_,*(uint *)(param_1 + 4) >> 0x14) & 0xffffffff00000007;
      local_a0 = 0;
      uStack_98 = 0;
      uStack_90 = 0;
      uStack_88 = 0;
      local_70 = 0;
      local_78 = 0;
      local_80 = 0;
      iVar2 = FUN_00f85cb0(&local_a0,&local_60);
      if (iVar2 == 0) {
        uVar1 = (uint)uStack_90;
      }
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return (ulong)uVar1;
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

