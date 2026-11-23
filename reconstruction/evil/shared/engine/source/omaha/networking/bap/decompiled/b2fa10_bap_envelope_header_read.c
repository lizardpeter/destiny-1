
ulong FUN_00b2fa10(long param_1,undefined1 *param_2,undefined4 *param_3)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 uVar3;
  char cVar4;
  int iVar5;
  ulong uVar6;
  undefined1 uVar7;
  undefined4 local_17c;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_17c = 0;
  iVar5 = *(int *)(param_1 + 0x16cc);
  cVar4 = FUN_00b30d60(param_1,6,param_1 + 0x16d0,(int *)(param_1 + 0x16cc),&local_17c);
  if (cVar4 == '\0') {
    if (DAT_0282d690 == '\0') {
      iVar5 = thunk_FUN_012aa7d6(&DAT_0282d690);
      if (iVar5 != 0) {
        DAT_0282d688 = FUN_000e4a10(s_networking_server_bap____s____s__01689460);
        thunk_FUN_012aa7e6(&DAT_0282d690);
      }
    }
    FUN_01008290(local_178,s_networking_server_bap____s____s__01689460,param_1 + 0x1148,
                 (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)],
                 *(undefined4 *)(param_1 + 0x16cc));
    FUN_000e4aa0(DAT_0282d688,local_178);
  }
  else {
    iVar2 = *(int *)(param_1 + 0x16cc);
    uVar3 = 1;
    if (iVar2 == iVar5) {
      uVar7 = 1;
      goto LAB_00b2fc15;
    }
    uVar7 = 0;
    if (iVar2 != 6) goto LAB_00b2fc15;
    *(char *)(param_1 + 0x16d6) = *(char *)(param_1 + 0x16d0);
    cVar4 = *(char *)(param_1 + 0x16d1);
    *(char *)(param_1 + 0x16d7) = cVar4;
    uVar1 = swap_bytes(*(undefined4 *)(param_1 + 0x16d2));
    *(undefined4 *)(param_1 + 0x16d8) = uVar1;
    uVar3 = 1;
    if (*(char *)(param_1 + 0x16d0) != '\x01') {
      if (DAT_0282d6a0 == '\0') {
        iVar5 = thunk_FUN_012aa7d6(&DAT_0282d6a0);
        if (iVar5 != 0) {
          DAT_0282d698 = FUN_000e4a10(s_networking_server_bap____s____s__016894a6);
          thunk_FUN_012aa7e6(&DAT_0282d6a0);
        }
      }
      uVar3 = 0;
      FUN_01008290(local_178,s_networking_server_bap____s____s__016894a6,param_1 + 0x1148,
                   (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)],
                   *(undefined1 *)(param_1 + 0x16d6),1);
      FUN_000e4aa0(DAT_0282d698,local_178);
      local_17c = 0xc;
      cVar4 = *(char *)(param_1 + 0x16d7);
    }
    if ((cVar4 == '\0') || (cVar4 == '\x02')) {
      *(undefined4 *)(param_1 + 0x16c8) = 3;
      goto LAB_00b2fc15;
    }
    if (cVar4 == '\x01') {
      *(undefined4 *)(param_1 + 0x16c8) = 2;
      goto LAB_00b2fc15;
    }
    local_17c = 0xe;
  }
  uVar7 = 0;
  uVar3 = 0;
LAB_00b2fc15:
  *param_3 = local_17c;
  *param_2 = uVar7;
  if (*DAT_01a1f100 == local_38) {
    return (ulong)CONCAT31((int3)((uint)local_17c >> 8),uVar3);
  }
  uVar6 = thunk_FUN_012aa7f6();
  return uVar6;
}

