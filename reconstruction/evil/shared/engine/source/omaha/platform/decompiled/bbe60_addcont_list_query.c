
undefined8 FUN_000bbe60(long param_1)

{
  undefined8 *puVar1;
  long *plVar2;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  bool bVar6;
  uint local_3c;
  long local_38;
  
  plVar2 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  if (*(long *)(param_1 + 0x38) == 0) {
    uVar5 = 0;
    thunk_FUN_012ab1f6(0,0,0,&local_3c);
    uVar4 = FUN_000b89f0();
    uVar4 = FUN_000ba9f0(uVar4,0,0,(ulong)local_3c * 0x18);
    *(undefined8 *)(param_1 + 0x38) = uVar4;
    thunk_FUN_012ab1f6(0,uVar4,local_3c,&local_3c);
    *(uint *)(param_1 + 0x4c) = local_3c;
    *(undefined4 *)(param_1 + 0x48) = 0;
  }
  else {
    uVar5 = *(uint *)(param_1 + 0x48);
    local_3c = *(uint *)(param_1 + 0x4c);
  }
  bVar6 = false;
  if (uVar5 < local_3c) {
    bVar6 = false;
    do {
      if (bVar6) break;
      if (*(int *)(*(long *)(param_1 + 0x38) + 0x14 + (ulong)uVar5 * 0x18) == 4) {
        puVar1 = (undefined8 *)(*(long *)(param_1 + 0x38) + (ulong)uVar5 * 0x18);
        iVar3 = FUN_000bbd50(0,puVar1);
        if (iVar3 != 0) {
          *(undefined4 *)(param_1 + 0x60) = *(undefined4 *)(puVar1 + 2);
          uVar4 = *puVar1;
          *(undefined8 *)(param_1 + 0x58) = puVar1[1];
          *(undefined8 *)(param_1 + 0x50) = uVar4;
          *(int *)(param_1 + 0x44) = iVar3;
          bVar6 = true;
        }
      }
      uVar5 = *(int *)(param_1 + 0x48) + 1;
      *(uint *)(param_1 + 0x48) = uVar5;
    } while (uVar5 < *(uint *)(param_1 + 0x4c));
  }
  *(byte *)(param_1 + 100) = bVar6 ^ 1;
  if (*plVar2 == local_38) {
    return CONCAT71((int7)((ulong)*plVar2 >> 8),1);
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

