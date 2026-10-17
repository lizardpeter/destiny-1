
bool FUN_007e1ea0(undefined8 param_1,long param_2,undefined8 param_3,undefined4 param_4)

{
  undefined8 uVar1;
  char cVar2;
  undefined1 uVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar2 = FUN_00f82b70(param_3);
  if (cVar2 != '\0') {
    FUN_00f7fcd0(*(undefined8 *)(param_2 + 0x50),0x31);
    uVar4 = FUN_002836d0(param_3);
    iVar5 = FUN_00f82ba0(param_3);
    puVar7 = (undefined4 *)FUN_00f7feb0(*(undefined8 *)(param_2 + 0x50),4,2);
    *puVar7 = 0;
    FUN_007e1d10(param_2,(ulong)uVar4 << 8,iVar5 * 0x80 + 0x80,puVar7,4);
    local_40[0] = FUN_00f82b00(param_3);
    uVar6 = FUN_00f7d710(local_40);
    FUN_007e1b60(param_1,param_2,uVar6,param_4);
    uVar1 = *(undefined8 *)(param_2 + 0x50);
    puVar7 = (undefined4 *)FUN_00f7feb0(uVar1,4,3);
    *puVar7 = 0;
    FUN_00f80c90(uVar1,4,0,puVar7,1,1,0,0);
    FUN_00f80e00(uVar1,puVar7,0xffffffff,3,1);
  }
  if (*DAT_01a1f100 == local_38) {
    return cVar2 != '\0';
  }
  uVar3 = thunk_FUN_012aa7f6();
  return (bool)uVar3;
}

