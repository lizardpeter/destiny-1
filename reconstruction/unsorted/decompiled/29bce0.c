
ulong FUN_0029bce0(long *param_1,undefined8 param_2)

{
  ulong uVar1;
  undefined8 uVar2;
  ulong uVar3;
  undefined4 local_630 [2];
  undefined1 local_628 [1536];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  uVar1 = (**(code **)(*param_1 + 0x18))();
  uVar3 = uVar1 & 0xffffffffffffff00;
  if ((char)uVar1 != '\0') {
    thunk_FUN_012aa7c6(local_628,param_2,0x600);
    uVar2 = (**(code **)(*param_1 + 0x10))(param_1);
    local_630[0] = 0;
    uVar3 = FUN_00299d10(param_1,uVar2,0x14,*(undefined4 *)PTR_DAT_0191a3a8,local_628,0x600,
                         local_630);
  }
  if (*DAT_01a1f100 == local_28) {
    return uVar3;
  }
  uVar1 = thunk_FUN_012aa7f6();
  return uVar1;
}

