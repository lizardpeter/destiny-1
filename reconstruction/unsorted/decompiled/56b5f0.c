
void FUN_0056b5f0(long param_1)

{
  char cVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  int local_58 [2];
  undefined4 local_50;
  undefined4 local_48;
  undefined4 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  puVar2 = (undefined4 *)(param_1 + 0x4fdec);
  iVar3 = (int)param_1 + 0x40a0;
  iVar4 = 0;
  do {
    puVar2[-0x17] = 0xffffffff;
    cVar1 = FUN_0056d6e0(param_1,iVar4,0,local_58);
    if (cVar1 != '\0') {
      puVar2[-0x16] = local_50;
      puVar2[-0x14] = local_40;
      puVar2[-0x15] = local_48;
      puVar2[-0x17] = local_58[0] - iVar3;
    }
    puVar2[-0x13] = 0xffffffff;
    cVar1 = FUN_0056d6e0(param_1,iVar4,1,local_58);
    if (cVar1 != '\0') {
      puVar2[-0x12] = local_50;
      puVar2[-0x10] = local_40;
      puVar2[-0x11] = local_48;
      puVar2[-0x13] = local_58[0] - iVar3;
    }
    puVar2[-0xf] = 0xffffffff;
    cVar1 = FUN_0056d6e0(param_1,iVar4,2,local_58);
    if (cVar1 != '\0') {
      puVar2[-0xe] = local_50;
      puVar2[-0xc] = local_40;
      puVar2[-0xd] = local_48;
      puVar2[-0xf] = local_58[0] - iVar3;
    }
    puVar2[-0xb] = 0xffffffff;
    cVar1 = FUN_0056d6e0(param_1,iVar4,3,local_58);
    if (cVar1 != '\0') {
      puVar2[-10] = local_50;
      puVar2[-8] = local_40;
      puVar2[-9] = local_48;
      puVar2[-0xb] = local_58[0] - iVar3;
    }
    puVar2[-7] = 0xffffffff;
    cVar1 = FUN_0056d6e0(param_1,iVar4,4,local_58);
    if (cVar1 != '\0') {
      puVar2[-6] = local_50;
      puVar2[-4] = local_40;
      puVar2[-5] = local_48;
      puVar2[-7] = local_58[0] - iVar3;
    }
    puVar2[-3] = 0xffffffff;
    cVar1 = FUN_0056d6e0(param_1,iVar4,5,local_58);
    if (cVar1 != '\0') {
      puVar2[-2] = local_50;
      *puVar2 = local_40;
      puVar2[-1] = local_48;
      puVar2[-3] = local_58[0] - iVar3;
    }
    puVar2 = puVar2 + 0x18;
    iVar4 = iVar4 + 1;
  } while (iVar4 != 8);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

