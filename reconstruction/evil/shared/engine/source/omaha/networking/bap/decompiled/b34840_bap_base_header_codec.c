
undefined8 FUN_00b34840(ushort *param_1,uint param_2,ushort *param_3)

{
  undefined4 uVar1;
  char cVar2;
  int iVar3;
  undefined8 uVar4;
  ushort uVar5;
  uint uVar6;
  undefined1 uVar7;
  undefined1 local_168 [320];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  uVar7 = 0;
  if (5 < param_2) {
    param_3[2] = param_1[2];
    *(undefined4 *)param_3 = *(undefined4 *)param_1;
    uVar1 = swap_bytes(*(undefined4 *)(param_1 + 1));
    *(undefined4 *)(param_3 + 1) = uVar1;
    uVar6 = (*param_1 & 0xff00) << 8 | (uint)*param_1 << 0x18;
    uVar7 = 1;
    uVar5 = (ushort)(uVar6 >> 0x10);
    *param_3 = uVar5;
    if (0x12f < uVar5) {
      cVar2 = FUN_000e4d70(7,4);
      uVar7 = 0;
      if (cVar2 != '\0') {
        if (DAT_0282da38 == '\0') {
          iVar3 = thunk_FUN_012aa7d6(&DAT_0282da38);
          if (iVar3 != 0) {
            DAT_0282da30 = FUN_000e4a10(s_networking_investment_bap_header_0168abb5);
            thunk_FUN_012aa7e6(&DAT_0282da38);
          }
        }
        uVar7 = 0;
        FUN_01008290(local_168,s_networking_investment_bap_header_0168abb5,uVar6 >> 0x10);
        FUN_000e4aa0(DAT_0282da30,local_168);
      }
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar7);
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

