
void FUN_0029fe70(void)

{
  undefined8 uVar1;
  undefined4 uVar2;
  int iVar3;
  ulong uVar4;
  uint uVar5;
  ulong uVar6;
  uint local_48 [2];
  long local_40;
  int local_38;
  uint uStack_34;
  undefined8 *local_30;
  long *local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  uVar1 = *(undefined8 *)(DAT_026556d0[1] + 0x10);
  uVar2 = FUN_0006f140(&DAT_026556d0);
  FUN_0008f550(local_48,uVar1,uVar2);
  local_30 = &DAT_026556d0;
  local_28 = DAT_026556d0;
  uVar4 = CONCAT44(uStack_34,local_38);
  if (local_38 <= (int)local_48[0]) {
LAB_0029ffaf:
    if (*DAT_01a1f100 == local_20) {
      return;
    }
    thunk_FUN_012aa7f6();
    return;
  }
LAB_0029fee8:
  uVar6 = (ulong)((local_48[0] & 0xffff) * (int)local_28[2]);
  iVar3 = (int)uVar4;
  if (*(char *)(uVar6 + 0x1c + *local_28) != '\0') {
    FUN_002a1990(*local_28 + uVar6);
    uVar4 = CONCAT44(uStack_34,local_38);
    iVar3 = local_38;
  }
  uVar4 = uVar4 >> 0x20;
  uVar5 = local_48[0];
LAB_0029ff10:
  do {
    local_48[0] = uVar5 + 1;
    if ((int)local_48[0] < iVar3) {
      uVar4 = uVar4 >> 1;
      uStack_34 = (uint)uVar4;
      if (uStack_34 == 0) {
        local_48[0] = uVar5 + 0x20 & 0xffffffe0;
        if (iVar3 <= (int)local_48[0]) {
LAB_0029ff7e:
          uVar4 = 0;
          goto LAB_0029ff80;
        }
        uStack_34 = *(uint *)(local_40 + (long)((int)(uVar5 + 0x20) >> 5) * 4);
        while (uVar4 = (ulong)uStack_34, uStack_34 == 0) {
          local_48[0] = local_48[0] + 0x20;
          if (iVar3 <= (int)local_48[0]) goto LAB_0029ff7e;
          uStack_34 = *(uint *)(local_40 + (long)((int)local_48[0] >> 5) * 4);
        }
      }
      uVar5 = local_48[0];
      if ((uVar4 & 1) == 0) goto LAB_0029ff10;
    }
LAB_0029ff80:
    if ((iVar3 <= (int)local_48[0]) ||
       (uVar5 = local_48[0],
       (*(uint *)(*(long *)(local_28[1] + 0x10) + (ulong)(local_48[0] >> 5 & 0x7ff) * 4) >>
        (local_48[0] & 0x1f) & 1) != 0)) break;
  } while( true );
  uVar4 = CONCAT44(uStack_34,local_38);
  if (local_38 <= (int)local_48[0]) goto LAB_0029ffaf;
  goto LAB_0029fee8;
}

