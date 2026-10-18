
bool FUN_007e2000(long *param_1,undefined8 param_2,byte param_3)

{
  long lVar1;
  long lVar2;
  char cVar3;
  byte bVar4;
  undefined1 uVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  undefined4 *puVar9;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar3 = FUN_00f82b70(param_2);
  if (cVar3 != '\0') {
    lVar2 = param_1[10];
    uVar6 = FUN_00057e60(param_2);
    local_40[0] = FUN_00f82b00(param_2);
    iVar7 = FUN_00f7d730(local_40);
    iVar8 = FUN_00f82ae0(param_2);
    bVar4 = FUN_00f826c0(param_2);
    FUN_00f7fd40(lVar2,uVar6,(uint)((iVar8 * 0x40 + 0x40) * iVar7 << (bVar4 & 0x1f)) >> 8,
                 0x40 << (param_3 & 0x1f),0,0x2000000,1);
    FUN_00f7fcd0(lVar2,0x2e);
    FUN_00f7e8d0(lVar2,2,0xcc);
    FUN_007e0240(param_1,param_2);
    lVar1 = lVar2 + 0xc0;
    puVar9 = *(undefined4 **)(*param_1 + 0x20);
    FUN_00f8b790(lVar1,puVar9 + 5,*puVar9,*(undefined8 *)(puVar9 + 2));
    FUN_00f8b8c0(lVar1,0);
    FUN_00f7f1e0(lVar2,0x11);
    FUN_00f8df60(lVar1,lVar2,lVar2 + 0x80);
    FUN_00f7f260(lVar2,3);
    FUN_00f8e880(lVar1,lVar2,lVar2 + 0x80);
    lVar1 = param_1[10];
    puVar9 = (undefined4 *)FUN_00f7feb0(lVar1,4,3);
    *puVar9 = 0;
    FUN_00f80c90(lVar1,4,0,puVar9,1,1,0,0);
    FUN_00f80e00(lVar1,puVar9,0xffffffff,3,1);
    FUN_00f7e8d0(lVar2,1,0xcc);
    FUN_007e0430(param_1);
  }
  if (*DAT_01a1f100 == local_38) {
    return cVar3 != '\0';
  }
  uVar5 = thunk_FUN_012aa7f6();
  return (bool)uVar5;
}

