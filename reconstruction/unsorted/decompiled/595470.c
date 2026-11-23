
undefined8 FUN_00595470(long param_1,undefined8 param_2)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  undefined8 uVar5;
  int iVar6;
  undefined8 local_d8;
  byte local_d0 [16];
  undefined4 local_c0;
  ushort local_bc;
  undefined8 local_b8;
  undefined8 local_60;
  undefined8 local_58;
  undefined8 uStack_50;
  undefined8 local_48;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_58 = 0;
  uStack_50 = 0;
  local_48 = 0;
  local_d8 = param_2;
  if ((*(int *)(param_1 + 0x18) == 0) ||
     (cVar1 = FUN_002a35c0(&local_d8,param_1 + 0x1c), cVar1 != '\0')) {
    FUN_00595e90(param_1 + 0x10,local_d8);
    uVar2 = 0;
  }
  else {
    uVar2 = 0;
    if ((*(uint *)(param_1 + 0x18) | 2) != 3) {
      local_48 = *(undefined8 *)(param_1 + 0x50);
      local_58 = *(undefined8 *)(param_1 + 0x40);
      uStack_50 = *(undefined8 *)(param_1 + 0x48);
      iVar4 = *(int *)(param_1 + 0x7c);
      if (iVar4 == -1) {
        iVar6 = 1;
        if (*(int *)(param_1 + 0x78) == 1) {
          do {
            iVar6 = iVar6 + 1;
            iVar4 = -1;
            if (3 < iVar6) break;
            iVar3 = FUN_00559c30(iVar6);
            iVar4 = iVar6;
          } while (iVar3 != 0);
        }
        else {
          iVar4 = 1;
        }
        cVar1 = FUN_0055a5e0(iVar4);
        if (cVar1 == '\0') goto LAB_005955f3;
        FUN_0055a7e0(iVar4);
        *(int *)(param_1 + 0x7c) = iVar4;
      }
      local_d0[0] = 0;
      local_60 = param_2;
      iVar4 = FUN_0055a3d0(iVar4,local_d0);
      if (iVar4 == 1) {
        local_d0[0] = local_d0[0] | 2;
        local_c0 = swap_bytes((undefined4)local_58);
        local_bc = (ushort)local_48 << 8 | (ushort)local_48 >> 8;
        cVar1 = FUN_000b4f80(&local_60);
        if (cVar1 != '\0') {
          local_d0[0] = local_d0[0] | 0x10;
          local_b8 = local_60;
        }
        uVar2 = FUN_0055a300(*(undefined4 *)(param_1 + 0x7c),local_d0);
      }
    }
  }
LAB_005955f3:
  if (*DAT_01a1f100 != local_38) {
    uVar5 = thunk_FUN_012aa7f6();
    return uVar5;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar2);
}

