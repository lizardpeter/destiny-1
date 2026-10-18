
void FUN_007e0780(long param_1,undefined8 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,int param_6)

{
  long lVar1;
  long lVar2;
  undefined8 uVar3;
  undefined8 *puVar4;
  
  lVar2 = *(long *)(param_1 + 0x50);
  *(ulong *)(lVar2 + 0x28) = *(ulong *)(lVar2 + 0x28) | 2;
  lVar1 = lVar2 + 0xc0;
  FUN_00f8b980(lVar1);
  FUN_00f8e680(lVar1,lVar2,lVar2 + 0x80);
  FUN_00f7f4a0(lVar2,param_3,param_4,param_5);
  FUN_00f8e880(lVar1,lVar2,lVar2 + 0x80);
  if (param_6 == 1) {
    uVar3 = *(undefined8 *)(param_1 + 0x50);
    puVar4 = (undefined8 *)FUN_00f7feb0(uVar3,8,3);
    *puVar4 = 0;
    FUN_00f81090(uVar3,0x2f,puVar4,1);
    FUN_00f80e00(uVar3,puVar4,0xffffffff,3,1);
    FUN_00f80f10(uVar3,0x38,0,1);
  }
  *(byte *)(lVar2 + 0x28) = *(byte *)(lVar2 + 0x28) & 0xfd;
  *(undefined8 *)(param_1 + 0x1d48) = 0;
  FUN_00f8b980(lVar1,0);
  return;
}

