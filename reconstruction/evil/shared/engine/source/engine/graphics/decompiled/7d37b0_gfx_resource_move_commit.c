
void FUN_007d37b0(uint param_1,ulong param_2)

{
  int iVar1;
  long lVar2;
  undefined4 uVar3;
  uint uVar4;
  long lVar5;
  long *plVar6;
  ulong uVar7;
  long lVar8;
  ulong uVar9;
  undefined8 local_50;
  ulong local_48;
  uint local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_40[0] = param_1;
  if (param_1 != 0xffffffff) {
    uVar4 = (uint)param_2;
    uVar3 = FUN_000de720(param_2 & 0xffffffff);
    FUN_0006fb60(((int)param_1 >> 0x1f & 0x3c00U | 0x3ff) & param_1 >> 0xd);
    FUN_0006fb60(((int)uVar4 >> 0x1f & 0x3c00U | 0x3ff) & (uint)(param_2 >> 0xd) & 0x7ffff);
    lVar5 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
    lVar2 = *DAT_01a238a0;
    lVar8 = *(long *)(lVar2 + 0x10 + lVar5);
    iVar1 = *(int *)(lVar2 + 0x34 + lVar5);
    uVar7 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar5));
    uVar9 = *(ulong *)(lVar8 + 8 + uVar7);
    lVar5 = (*DAT_0254ee98)(param_1,param_2 & 0xffffffff,1,1);
    lVar8 = (lVar8 + uVar7) - ((long)iVar1 & uVar9);
    lVar2 = lVar8 + lVar5;
    uVar4 = FUN_000de720(param_1);
    uVar9 = (ulong)uVar4;
    uVar4 = FUN_0006dbd0(local_40);
    FUN_0006f5a0(param_1,lVar2,uVar4 | 0xc0000000);
    FUN_0006f5a0(param_2 & 0xffffffff,lVar8,(uint)lVar5 | 0xc0000000);
    lVar8 = FUN_000de6f0(uVar3);
    plVar6 = (long *)FUN_000de6f0(uVar9);
    *plVar6 = lVar2;
    FUN_000de1e0(uVar9,uVar3);
    *(byte *)(lVar8 + 0x16) = *(byte *)(lVar8 + 0x16) | 1;
    *(byte *)((long)plVar6 + 0x16) = *(byte *)((long)plVar6 + 0x16) | 1;
    local_50 = 0;
    local_48 = uVar9;
    FUN_007da960(0,0,0,FUN_007d3960,&local_48,&local_50,0);
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

