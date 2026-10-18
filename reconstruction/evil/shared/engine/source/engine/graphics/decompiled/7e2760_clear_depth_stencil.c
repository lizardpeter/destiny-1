
void FUN_007e2760(undefined4 param_1,long *param_2,uint param_3,undefined1 param_4)

{
  long lVar1;
  long lVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined8 uVar5;
  bool bVar6;
  undefined4 local_50 [2];
  undefined4 local_48 [2];
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar2 = param_2[10];
  *(undefined4 *)(lVar2 + 0x3a8) = 0;
  FUN_00f7fe20(lVar2,0);
  FUN_00992780(local_40);
  FUN_00992780(local_48);
  if (((param_3 & 0x80) == 0) || (iVar4 = FUN_00079280(param_2 + 0x4d6), iVar4 == 0)) {
    uVar5 = 0;
  }
  else {
    FUN_00f81b40(local_40,1);
    FUN_00992780(local_50);
    FUN_00f81e50(local_50,3,3,3);
    FUN_00f7e9b0(lVar2,local_50[0]);
    FUN_00f7e840(lVar2,(uint)*(byte *)((long)param_2 + 0x25ec) << 0x10 | 0xff00ffff);
    FUN_00f7eb50(lVar2,param_4);
    FUN_00f81b30(local_48,1);
    uVar5 = 7;
  }
  FUN_00f81ec0(local_48,uVar5);
  bVar6 = (param_3 & 0x40) != 0;
  if (bVar6) {
    FUN_00f81b30(local_40,1);
  }
  FUN_00f81d60(local_48,bVar6,7);
  FUN_00f80550(lVar2,local_40[0]);
  FUN_00f81b40(local_48,1);
  FUN_00f7e950(lVar2,local_48[0]);
  FUN_00f7eaf0(param_1,lVar2);
  FUN_00f7e740(lVar2,0);
  lVar1 = lVar2 + 0xc0;
  FUN_00f8b8c0(lVar1,0);
  puVar3 = *(undefined4 **)(*param_2 + 0x20);
  FUN_00f8b790(lVar1,puVar3 + 5,*puVar3,*(undefined8 *)(puVar3 + 2));
  FUN_00f7f1e0(lVar2,0x11);
  FUN_00f8df60(lVar1,lVar2,lVar2 + 0x80);
  FUN_00f7f260(lVar2,3);
  FUN_00f8e880(lVar1,lVar2,lVar2 + 0x80);
  FUN_00f7e740(lVar2,*(undefined4 *)
                      (&DAT_015d16e0 + (ulong)*(uint *)((long)param_2 + 0x25b4) * 0x24));
  FUN_00992780(local_40);
  FUN_00f80550(lVar2,local_40[0]);
  if ((param_3 & 0x80) != 0) {
    FUN_00f7e840(lVar2,*(undefined4 *)((long)param_2 + 0x25e4));
    FUN_00f7e9b0(lVar2,(int)param_2[0x4bc]);
  }
  FUN_00f7e950(lVar2,*(undefined4 *)((long)param_2 + 0x25dc));
  param_2[0x3a5] = 1;
  param_2[0x3a6] = 1;
  FUN_00f8b790(lVar1,0,0,0);
  FUN_00f8b8c0(lVar1,0);
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

