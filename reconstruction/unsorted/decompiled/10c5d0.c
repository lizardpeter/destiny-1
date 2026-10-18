
undefined4 * FUN_0010c5d0(undefined4 *param_1)

{
  long lVar1;
  char cVar2;
  undefined4 *puVar3;
  ulong uVar4;
  long lVar5;
  long lVar6;
  uint local_38 [2];
  long local_30;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  *param_1 = 0x811c9dc5;
  cVar2 = FUN_001072c0(0x10,0,local_38);
  if ((cVar2 != '\0') && (local_38[0] != 0xffffffff)) {
    lVar6 = (ulong)(((uint)((int)local_38[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_38[0] >> 0xd) *
            0x40;
    lVar5 = *DAT_01a238a0;
    lVar1 = *(long *)(lVar5 + 0x10 + lVar6);
    uVar4 = (ulong)((local_38[0] & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar6));
    lVar5 = (lVar1 + uVar4) - ((long)*(int *)(lVar5 + 0x34 + lVar6) & *(ulong *)(lVar1 + 8 + uVar4))
    ;
    if (local_30 + lVar5 != -0x1ac) {
      *param_1 = *(undefined4 *)(local_30 + 0x1b4 + lVar5);
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return param_1;
  }
  puVar3 = (undefined4 *)thunk_FUN_012aa7f6();
  return puVar3;
}

