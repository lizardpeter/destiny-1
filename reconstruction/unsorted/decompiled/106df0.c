
undefined8 FUN_00106df0(uint param_1,undefined4 param_2)

{
  long lVar1;
  undefined8 uVar2;
  long lVar3;
  long lVar4;
  ulong uVar5;
  undefined4 local_20;
  undefined4 uStack_1c;
  undefined4 local_18 [2];
  long local_10;
  
  local_10 = *DAT_01a1f100;
  uVar2 = 3;
  if (param_1 != 0xffffffff) {
    lVar3 = (ulong)(((uint)((int)param_1 >> 0xd) >> 0x12 | 0x3ff) & (int)param_1 >> 0xd) * 0x40;
    lVar4 = *DAT_01a238a0;
    uVar2 = 0;
    lVar1 = *(long *)(lVar4 + 0x10 + lVar3);
    uVar5 = (ulong)((param_1 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar3));
    lVar4 = (lVar1 + uVar5) - ((long)*(int *)(lVar4 + 0x34 + lVar3) & *(ulong *)(lVar1 + 8 + uVar5))
    ;
    _local_20 = CONCAT44(*(undefined4 *)(lVar4 + 0x28),param_2);
    local_18[0] = *(undefined4 *)(lVar4 + 0xc);
    if ((ulong)DAT_025d6ff8 != 0) {
      uVar2 = *(undefined8 *)(&DAT_01ad5030 + (ulong)DAT_025d6ff8 * DAT_01ad5010 + DAT_01ad5000);
    }
    uVar2 = FUN_0100d5e0(uVar2,local_18,lVar4 + 0x10,&local_20);
  }
  if (*DAT_01a1f100 == local_10) {
    return uVar2;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

