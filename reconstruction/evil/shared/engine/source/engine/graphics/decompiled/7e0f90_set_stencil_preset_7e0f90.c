
void FUN_007e0f90(long param_1,int param_2)

{
  long lVar1;
  undefined *puVar2;
  
  if ((*(long *)(param_1 + 0x50) != 0) && (*(int *)(&DAT_000025e8 + param_1) != param_2)) {
    if (*(int *)(FUN_000025b0 + param_1) == 1) {
      puVar2 = PTR_DAT_01a1f4c0 +
               (ulong)*(uint *)(&DAT_018ded80 + (ulong)*(uint *)(param_1 + 0x25b8) * 4) * 0x28;
    }
    else {
      puVar2 = (undefined *)0x15d1e38;
    }
    lVar1 = param_1 + 0x25dc;
    FUN_00f81b30(lVar1,puVar2[4]);
    FUN_00f81b80(lVar1,puVar2[4]);
    FUN_00f81ec0(lVar1,*(undefined4 *)(puVar2 + 8));
    FUN_00f81d90(lVar1,*(undefined4 *)(puVar2 + 0x18));
    FUN_00f81e50(param_1 + 0x25e0,*(undefined4 *)(puVar2 + 0x10),*(undefined4 *)(puVar2 + 0xc),
                 *(undefined4 *)(puVar2 + 0x14));
    FUN_00f81e70(param_1 + 0x25e0,*(undefined4 *)(puVar2 + 0x20),*(undefined4 *)(puVar2 + 0x1c),
                 *(undefined4 *)(puVar2 + 0x24));
    *(undefined4 *)(param_1 + 0x25e4) = 0;
    *(undefined *)(param_1 + 0x25e5) = puVar2[5];
    *(undefined *)(param_1 + 0x25e6) = puVar2[6];
    *(char *)(param_1 + 0x25e4) = (char)param_2;
    *(char *)(param_1 + 0x25e7) = (char)param_2;
    FUN_00f7e950(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(param_1 + 0x25dc));
    FUN_00f7e840(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(param_1 + 0x25e4));
    FUN_00f7e9b0(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(param_1 + 0x25e0));
    *(int *)(&DAT_000025e8 + param_1) = param_2;
  }
  return;
}

