
void FUN_00b53bb0(long param_1,long param_2)

{
  uint *puVar1;
  long *plVar2;
  char cVar3;
  long lVar4;
  uint uVar5;
  ulong uVar6;
  uint local_40 [2];
  long local_38;
  int local_30;
  uint uStack_2c;
  long local_28;
  
  plVar2 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  FUN_0008f5d0(local_40,param_2,0,0x3000);
joined_r0x00b53bea:
  do {
    if (local_30 <= (int)local_40[0]) {
      lVar4 = 0;
      do {
        puVar1 = (uint *)(param_1 + 0x120b8 + lVar4 * 4);
        *puVar1 = *puVar1 | *(uint *)(param_2 + lVar4 * 4);
        lVar4 = lVar4 + 1;
      } while ((int)lVar4 != 0x180);
      if ((*(char *)(param_1 + 1) == '\0') && (cVar3 = FUN_0008f800(param_2,0x3000), cVar3 == '\0'))
      {
        *(undefined1 *)(param_1 + 1) = 1;
      }
      if (*plVar2 != local_28) {
        thunk_FUN_012aa7f6();
        return;
      }
      return;
    }
    *(undefined1 *)(param_1 + 0xb8 + (long)(int)local_40[0] * 6) = 0;
    *(undefined2 *)(param_1 + 0xb6 + (long)(int)local_40[0] * 6) = 0;
    puVar1 = (uint *)(param_1 + 0x12e40 + (long)((int)local_40[0] >> 5) * 4);
    *puVar1 = *puVar1 | 1 << ((byte)local_40[0] & 0x1f);
    uVar6 = (ulong)uStack_2c;
    uVar5 = local_40[0];
    do {
      local_40[0] = uVar5 + 1;
      if (local_30 <= (int)local_40[0]) break;
      uVar6 = uVar6 >> 1;
      uStack_2c = (uint)uVar6;
      if (uStack_2c == 0) {
        local_40[0] = uVar5 + 0x20 & 0xffffffe0;
        if (local_30 <= (int)local_40[0]) break;
        uStack_2c = *(uint *)(local_38 + (long)((int)(uVar5 + 0x20) >> 5) * 4);
        while (uVar6 = (ulong)uStack_2c, uStack_2c == 0) {
          local_40[0] = local_40[0] + 0x20;
          if (local_30 <= (int)local_40[0]) goto joined_r0x00b53bea;
          uStack_2c = *(uint *)(local_38 + (long)((int)local_40[0] >> 5) * 4);
        }
      }
      uVar5 = local_40[0];
    } while ((uVar6 & 1) == 0);
  } while( true );
}

