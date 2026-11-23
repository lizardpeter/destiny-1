
ulong FUN_0029b280(long *param_1,undefined8 param_2)

{
  ulong *puVar1;
  char cVar2;
  undefined8 uVar3;
  ulong uVar4;
  undefined4 local_30 [2];
  ulong local_28;
  
  puVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  cVar2 = (**(code **)(*param_1 + 0x18))();
  if (cVar2 == '\0') {
    uVar4 = *puVar1;
    if (uVar4 != local_28) goto LAB_0029b309;
    uVar4 = uVar4 & 0xffffffffffffff00;
  }
  else {
    uVar3 = (**(code **)(*param_1 + 0x10))(param_1);
    local_30[0] = 0;
    uVar4 = FUN_00299d10(param_1,uVar3,0x12,*(undefined4 *)PTR_DAT_0191a360,param_2,0x2cc,local_30);
    if (*puVar1 != local_28) {
LAB_0029b309:
      uVar4 = thunk_FUN_012aa7f6();
      return uVar4;
    }
  }
  return uVar4;
}

