
void FUN_007e2480(undefined8 param_1,long *param_2,uint param_3)

{
  long lVar1;
  long lVar2;
  undefined4 *puVar3;
  ulong uVar4;
  uint uVar5;
  uint uVar6;
  undefined8 *puVar7;
  uint uVar8;
  ulong uVar9;
  undefined8 in_XMM0_Qb;
  undefined4 local_58 [2];
  undefined4 local_50 [2];
  undefined1 local_48 [16];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar5 = FUN_007e2200(param_2,param_3 & 0x3c);
  if (uVar5 != 0) {
    lVar2 = param_2[10];
    *(undefined4 *)(lVar2 + 0x3a8) = 0;
    FUN_00f7fe20(lVar2,0);
    FUN_00992780(local_50);
    FUN_00f81d60(local_50,0,7);
    FUN_00f81ec0(local_50,7);
    FUN_00f81b40(local_50,0);
    FUN_00f81b30(local_50,0);
    FUN_00f7e950(lVar2,local_50[0]);
    uVar8 = (int)(uVar5 << 0x1d) >> 0x1f & 0xf;
    uVar6 = uVar8 + 0xf0;
    if ((uVar5 & 8) == 0) {
      uVar6 = uVar8;
    }
    uVar9 = 2;
    if ((uVar5 & 0x10) == 0) {
      uVar9 = (ulong)((uVar5 & 8) >> 3 ^ 1) ^ 1;
    }
    uVar8 = uVar6 | 0xf00;
    if ((uVar5 & 0x10) == 0) {
      uVar8 = uVar6;
    }
    uVar6 = uVar8 | 0xf000;
    uVar4 = 3;
    if ((uVar5 & 0x20) == 0) {
      uVar6 = uVar8;
      uVar4 = uVar9;
    }
    FUN_00f7e740(lVar2,uVar6);
    puVar7 = (undefined8 *)FUN_00f7feb0(lVar2,0x10,4);
    *puVar7 = param_1;
    puVar7[1] = in_XMM0_Qb;
    FUN_00f7d180(local_48,puVar7,0x10);
    FUN_00f7d010(local_48,0x10);
    lVar1 = lVar2 + 0xc0;
    FUN_00f8b500(lVar1,1,0,1,local_48);
    FUN_00992780(local_58);
    FUN_00f819f0(local_58,0);
    FUN_00f7e7c0(lVar2,0,local_58[0]);
    FUN_00f7e7c0(lVar2,1,local_58[0]);
    FUN_00f7e7c0(lVar2,2,local_58[0]);
    FUN_00f7e7c0(lVar2,3,local_58[0]);
    puVar3 = *(undefined4 **)(*param_2 + 0x20);
    FUN_00f8b790(lVar1,puVar3 + 5,*puVar3,*(undefined8 *)(puVar3 + 2));
    FUN_00f8b8c0(lVar1,*(undefined8 *)(*param_2 + 0x28 + uVar4 * 8));
    FUN_00f7f1e0(lVar2,0x11);
    FUN_00f8df60(lVar1,lVar2,lVar2 + 0x80);
    FUN_00f7f260(lVar2,3);
    FUN_00f8e880(lVar1,lVar2,lVar2 + 0x80);
    FUN_00f7e740(lVar2,*(undefined4 *)
                        (&DAT_015d16e0 + (ulong)*(uint *)((long)param_2 + 0x25b4) * 0x24));
    FUN_00f7e7c0(lVar2,0,(int)param_2[0x4bb]);
    FUN_00f7e7c0(lVar2,1,(int)param_2[0x4bb]);
    FUN_00f7e7c0(lVar2,2,(int)param_2[0x4bb]);
    FUN_00f7e7c0(lVar2,3,(int)param_2[0x4bb]);
    FUN_00f7e950(lVar2,*(undefined4 *)((long)param_2 + 0x25dc));
    FUN_007e0430(param_2);
    FUN_00f8b500(lVar1,1,0,1,0);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

