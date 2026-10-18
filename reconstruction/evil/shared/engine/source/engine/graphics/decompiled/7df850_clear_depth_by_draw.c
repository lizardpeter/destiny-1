
void FUN_007df850(long *param_1,long *param_2)

{
  long lVar1;
  long lVar2;
  long lVar3;
  char cVar4;
  undefined4 *puVar5;
  undefined4 local_48 [2];
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar4 = FUN_00f7e4c0(param_2);
  if (cVar4 != '\0') {
    lVar2 = param_1[10];
    FUN_00f7fcd0(lVar2,0x2c);
    FUN_00f7eec0(lVar2,param_2);
    FUN_00f7ea20(lVar2);
    FUN_00992780(local_40);
    FUN_00f81b70(local_40,1);
    FUN_00f81b60(local_40,1);
    FUN_00f80550(lVar2,local_40[0]);
    FUN_00f7e8d0(lVar2,0,0xcc);
    FUN_00f8f4b0(DAT_0165fe7c,DAT_0165fe7c,lVar2,0,0,*(uint *)(param_2 + 6) & 0xffff,
                 *(uint *)(param_2 + 6) >> 0x10);
    lVar1 = lVar2 + 0xc0;
    FUN_00f8b8c0(lVar1,0);
    puVar5 = *(undefined4 **)(*param_1 + 0x20);
    FUN_00f8b790(lVar1,puVar5 + 5,*puVar5,*(undefined8 *)(puVar5 + 2));
    FUN_00f7f1e0(lVar2,0x11);
    FUN_00f8df60(lVar1,lVar2,lVar2 + 0x80);
    FUN_00f7f260(lVar2,3);
    FUN_00f8e880(lVar1,lVar2,lVar2 + 0x80);
    lVar3 = param_1[10];
    puVar5 = (undefined4 *)FUN_00f7feb0(lVar3,4,3);
    *puVar5 = 0;
    FUN_00f80c90(lVar3,4,0,puVar5,1,1,0,0);
    FUN_00f80e00(lVar3,puVar5,0xffffffff,3,1);
    FUN_007dfac0((int)param_1[0x4b1],*(undefined4 *)((long)param_1 + 0x258c),param_1,
                 (int)param_1[0x4af],*(undefined4 *)((long)param_1 + 0x257c),(int)param_1[0x4b0],
                 *(undefined4 *)((long)param_1 + 0x2584));
    FUN_00f7e8d0(lVar2,1,0xcc);
    FUN_00992780(local_48);
    FUN_00f80550(lVar2,local_48[0]);
    FUN_00f7e950(lVar2,*(undefined4 *)((long)param_1 + 0x25dc));
    if (param_1 + 0x4d6 != param_2) {
      FUN_00f7eec0(lVar2);
    }
    param_1[0x3a5] = 1;
    param_1[0x3a6] = 1;
    FUN_00f8b790(lVar1,0,0,0);
    FUN_00f8b8c0(lVar1,0);
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

