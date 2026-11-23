
void FUN_007e1d10(long *param_1,undefined8 param_2,uint param_3,undefined8 param_4,ulong param_5)

{
  long lVar1;
  long lVar2;
  uint *puVar3;
  undefined8 *puVar4;
  uint uVar5;
  ulong uVar6;
  uint uVar7;
  undefined1 local_68 [16];
  undefined1 local_58 [16];
  undefined1 local_48 [16];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar2 = param_1[10];
  param_3 = param_3 >> 2;
  FUN_00f7d0a0(local_48,param_2,0x4404,param_3);
  FUN_00f7d010(local_48,0x6d);
  lVar1 = lVar2 + 0xc0;
  FUN_00f8b2e0(lVar1,0,0,1,local_48);
  uVar6 = param_5 >> 2 & 0x3fffffff;
  uVar5 = (uint)uVar6;
  FUN_00f7d0a0(local_58,param_4,0x4404,uVar6);
  FUN_00f7d010(local_58,0x10);
  FUN_00f8b0c0(lVar1,0,0,1,local_58);
  puVar3 = (uint *)FUN_00f7feb0(lVar2,8,2);
  uVar7 = uVar5 + 0x3fffffff & uVar5;
  *puVar3 = param_3;
  puVar3[1] = uVar5 - (uVar7 == 0);
  FUN_00f7d180(local_68,puVar3,8);
  FUN_00f7d010(local_68,0x10);
  FUN_00f8b500(lVar1,0,0,1,local_68);
  puVar4 = (undefined8 *)(*param_1 + 0x70);
  if (uVar7 != 0) {
    puVar4 = (undefined8 *)(*param_1 + 0x78);
  }
  FUN_007e0780(param_1,*puVar4,param_3 + 0x3f >> 6,1,1,1);
  FUN_00f8b500(lVar1,0,0,1,0);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

