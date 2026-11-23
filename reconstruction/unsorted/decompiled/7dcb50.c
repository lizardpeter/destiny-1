
undefined8 FUN_007dcb50(long *param_1)

{
  long lVar1;
  undefined8 uVar2;
  bool bVar3;
  int iVar4;
  long lVar5;
  int iVar6;
  undefined1 local_60 [16];
  undefined8 local_50;
  long local_48;
  undefined4 local_30;
  undefined4 local_2c;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  thunk_FUN_012aba56(*(undefined4 *)(*param_1 + 0x80),local_60);
  lVar1 = *param_1;
  if (-1 < local_48) {
    iVar6 = (int)*(undefined8 *)(lVar1 + 0x13410);
    iVar6 = iVar6 - (((uint)((long)*(undefined8 *)(lVar1 + 0x13410) >> 0x3f) >> 0x1d) + iVar6 &
                    0xfffffff8);
    bVar3 = false;
    iVar4 = iVar6;
    do {
      lVar5 = (long)iVar4 * 0x20;
      if ((local_48 == *(long *)(lVar1 + 0x13310 + lVar5)) &&
         (bVar3 = true, *(long *)(lVar1 + 0x13320 + lVar5) == 0)) {
        *(undefined8 *)(lVar1 + 0x13320 + lVar5) = local_50;
        *(undefined4 *)(lVar1 + 0x13328 + lVar5) = local_30;
        *(undefined4 *)(lVar1 + 0x1332c + lVar5) = local_2c;
      }
      iVar4 = (iVar4 + 1) - (iVar4 + 1 + ((uint)(iVar4 + 1 >> 0x1f) >> 0x1d) & 0xfffffff8);
    } while ((iVar4 != iVar6) && (!bVar3));
  }
  *(undefined4 *)(*param_1 + 0x2dc) = 0;
  *(undefined4 *)(*param_1 + 0x2d0) = 0;
  *(undefined4 *)(*param_1 + 0x132e0 + (ulong)*(uint *)(*param_1 + 0xb0) * 4) = 0;
  *(undefined1 *)(*param_1 + 0x2d8) = 0;
  *(undefined4 *)(*param_1 + 0xc0) = 0;
  FUN_007dcce0(param_1);
  FUN_00f8ede0(param_1[10]);
  lVar1 = param_1[10];
  if (*(long *)(lVar1 + 0x40) != 0) {
    FUN_00f84db0(lVar1 + 0x40);
  }
  FUN_00f7e5e0(lVar1);
  *(undefined2 *)(lVar1 + 0xc84) = 0;
  *(undefined4 *)(lVar1 + 0xc80) = 0;
  FUN_007dc270(param_1,1);
  if (*DAT_01a1f100 != local_20) {
    uVar2 = thunk_FUN_012aa7f6();
    return uVar2;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
}

