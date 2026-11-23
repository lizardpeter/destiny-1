
void FUN_007e0de0(long param_1,uint param_2,undefined1 param_3)

{
  long lVar1;
  ulong uVar2;
  undefined *puVar3;
  undefined *puVar4;
  
  uVar2 = (ulong)*(uint *)(&DAT_018dec70 + (ulong)param_2 * 4);
  if (*(char *)(param_1 + 0x24) == '\0') {
    puVar4 = &DAT_015d1d70;
  }
  else {
    puVar4 = &DAT_015d1cd0;
  }
  if (*(int *)(FUN_000025b0 + param_1) == 1) {
    puVar3 = PTR_DAT_01a1f4c0 + (ulong)*(uint *)(&DAT_018ded80 + (ulong)param_2 * 4) * 0x28;
  }
  else {
    puVar3 = (undefined *)0x15d1e38;
  }
  lVar1 = param_1 + 0x25dc;
  FUN_00f81b40(lVar1,puVar4[uVar2 * 0xc + 4]);
  FUN_00f81d60(lVar1,puVar4[uVar2 * 0xc + 5],*(undefined4 *)(puVar4 + uVar2 * 0xc + 8));
  FUN_00f81b30(lVar1,puVar3[4]);
  FUN_00f81b80(lVar1,puVar3[4]);
  FUN_00f81ec0(lVar1,*(undefined4 *)(puVar3 + 8));
  FUN_00f81d90(lVar1,*(undefined4 *)(puVar3 + 0x18));
  FUN_00f81e50(param_1 + 0x25e0,*(undefined4 *)(puVar3 + 0x10),*(undefined4 *)(puVar3 + 0xc),
               *(undefined4 *)(puVar3 + 0x14));
  FUN_00f81e70(param_1 + 0x25e0,*(undefined4 *)(puVar3 + 0x20),*(undefined4 *)(puVar3 + 0x1c),
               *(undefined4 *)(puVar3 + 0x24));
  *(undefined4 *)(param_1 + 0x25e4) = 0;
  *(undefined *)(param_1 + 0x25e5) = puVar3[5];
  *(undefined *)(param_1 + 0x25e6) = puVar3[6];
  if (puVar3[4] == '\0') {
    *(undefined1 *)(param_1 + 0x25e4) = 0;
    *(undefined1 *)(param_1 + 0x25e7) = 0;
  }
  else {
    *(undefined1 *)(param_1 + 0x25e4) = param_3;
    *(undefined1 *)(param_1 + 0x25e7) = param_3;
  }
  FUN_00f7e950(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(param_1 + 0x25dc));
  FUN_00f7e840(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(param_1 + 0x25e4));
  FUN_00f7e9b0(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(param_1 + 0x25e0));
  *(uint *)(param_1 + 0x25b8) = param_2;
  return;
}

