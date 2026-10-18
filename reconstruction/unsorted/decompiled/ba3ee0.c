
void FUN_00ba3ee0(long param_1,uint *param_2)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  uVar3 = *param_2;
  if (0x40 - *(int *)(param_1 + 0x30) < 5) {
    FUN_000733a0(param_1,(ulong)uVar3,5);
  }
  else {
    *(int *)(param_1 + 0x30) = *(int *)(param_1 + 0x30) + 5;
    *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 5;
    *(ulong *)(param_1 + 0x28) = *(long *)(param_1 + 0x28) << 5 | (ulong)uVar3;
  }
  FUN_00072e30(param_1,param_2 + 1,0x40,0);
  uVar3 = param_2[3];
  if (0x40 - *(int *)(param_1 + 0x30) < 3) {
    FUN_000733a0(param_1,(ulong)uVar3,3);
  }
  else {
    *(int *)(param_1 + 0x30) = *(int *)(param_1 + 0x30) + 3;
    *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 3;
    *(ulong *)(param_1 + 0x28) = *(long *)(param_1 + 0x28) << 3 | (ulong)uVar3;
  }
  uVar3 = param_2[3];
  if (uVar3 == 0) {
    uVar3 = param_2[4];
    if (*(uint *)(param_1 + 0x30) < 0x40) {
      *(uint *)(param_1 + 0x30) = *(uint *)(param_1 + 0x30) + 1;
      *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 1;
      *(ulong *)(param_1 + 0x28) = *(long *)(param_1 + 0x28) * 2 | (ulong)(byte)uVar3;
    }
    else {
      FUN_000733a0(param_1,(ulong)(byte)uVar3,1);
    }
    uVar3 = param_2[3];
  }
  if (uVar3 == 3) {
    uVar3 = param_2[0xe];
    if (*(uint *)(param_1 + 0x30) < 0x40) {
      uVar4 = *(uint *)(param_1 + 0x30) + 1;
      *(uint *)(param_1 + 0x30) = uVar4;
      *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 1;
      *(ulong *)(param_1 + 0x28) = *(long *)(param_1 + 0x28) * 2 | (ulong)(byte)uVar3;
    }
    else {
      FUN_000733a0(param_1,(ulong)(byte)uVar3,1);
      uVar4 = *(uint *)(param_1 + 0x30);
    }
    bVar1 = *(byte *)((long)param_2 + 0x39);
    if (uVar4 < 0x40) {
      *(uint *)(param_1 + 0x30) = uVar4 + 1;
      *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 1;
      *(ulong *)(param_1 + 0x28) = *(long *)(param_1 + 0x28) * 2 | (ulong)bVar1;
    }
    else {
      FUN_000733a0(param_1,(ulong)bVar1,1);
    }
    if ((char)param_2[0xe] == '\0') {
      FUN_00072e30(param_1,(long)param_2 + 0x11,0x40,0);
      iVar2 = DAT_028a5ea0;
      uVar3 = param_2[7];
      if (0x40 - *(int *)(param_1 + 0x30) < DAT_028a5ea0) {
        FUN_000733a0(param_1,(ulong)uVar3,DAT_028a5ea0);
        iVar5 = *(int *)(param_1 + 0x30);
      }
      else {
        iVar5 = *(int *)(param_1 + 0x30) + DAT_028a5ea0;
        *(int *)(param_1 + 0x30) = iVar5;
        *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + iVar2;
        *(ulong *)(param_1 + 0x28) =
             *(long *)(param_1 + 0x28) << ((byte)iVar2 & 0x3f) | (ulong)uVar3;
      }
      uVar3 = param_2[8];
      if (0x40 - iVar5 < 2) {
        FUN_000733a0(param_1,(ulong)uVar3,2);
      }
      else {
        *(int *)(param_1 + 0x30) = iVar5 + 2;
        *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 2;
        *(ulong *)(param_1 + 0x28) = *(long *)(param_1 + 0x28) << 2 | (ulong)uVar3;
      }
      FUN_00072e30(param_1,param_2 + 10,0x40,0);
      FUN_00072e30(param_1,param_2 + 0xc,0x40,0);
    }
  }
  uVar3 = param_2[3];
  if (uVar3 - 3 < 2) {
    FUN_00ae2120(param_1,param_2 + 0x10,0);
    FUN_00ae2700(param_1,param_2 + 0x34,0);
    uVar3 = param_2[3];
  }
  if (uVar3 == 1) {
    uVar3 = param_2[0x3e];
    if (0x40 - *(int *)(param_1 + 0x30) < 5) {
      FUN_000733a0(param_1,(ulong)uVar3,5);
    }
    else {
      *(int *)(param_1 + 0x30) = *(int *)(param_1 + 0x30) + 5;
      *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 5;
      *(ulong *)(param_1 + 0x28) = *(long *)(param_1 + 0x28) << 5 | (ulong)uVar3;
    }
    FUN_00072e30(param_1,param_2 + 0x3f,0x40,0);
    return;
  }
  return;
}

