
undefined8 FUN_00b2fc70(long param_1,undefined1 *param_2,undefined4 *param_3)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  undefined8 uVar4;
  int iVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  undefined4 local_17c;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_17c = 0;
  if ((*(int *)(param_1 + 0x16c8) == 2) && (uVar1 = *(uint *)(param_1 + 0x16dc), uVar1 < 0x10)) {
    cVar3 = FUN_00b30d60(param_1,0x10,param_1 + 0x16e0,(uint *)(param_1 + 0x16dc),&local_17c);
    if (cVar3 == '\0') {
      if (DAT_0282d6b0 == '\0') {
        iVar5 = thunk_FUN_012aa7d6(&DAT_0282d6b0);
        if (iVar5 != 0) {
          DAT_0282d6a8 = FUN_000e4a10(s_networking_server_bap____s____s__016894fc);
          thunk_FUN_012aa7e6(&DAT_0282d6b0);
        }
      }
      uVar7 = 0;
      FUN_01008290(local_178,s_networking_server_bap____s____s__016894fc,param_1 + 0x1148,
                   (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)],
                   *(undefined4 *)(param_1 + 0x16dc));
      FUN_000e4aa0(DAT_0282d6a8,local_178);
      uVar6 = 0;
      goto LAB_00b2fd6a;
    }
    uVar2 = *(uint *)(param_1 + 0x16dc);
    uVar6 = 1;
    uVar7 = 1;
    if (uVar2 != uVar1) {
      uVar7 = 0;
      if (uVar2 == 0x10) {
        FUN_00b34c70((long)&PTR_DAT_00001eb8 + param_1,param_1 + 0x16e0,param_1 + 0x16f0);
        iVar5 = *(int *)(param_1 + 0x16d8) + -0x10;
        *(int *)(param_1 + 0x1838) = iVar5;
        cVar3 = FUN_00b34c80((long)&PTR_DAT_00001eb8 + param_1,iVar5,param_1 + 0x1840);
        if (cVar3 == '\0') {
          if (DAT_0282d6c0 == '\0') {
            iVar5 = thunk_FUN_012aa7d6(&DAT_0282d6c0);
            if (iVar5 != 0) {
              DAT_0282d6b8 = FUN_000e4a10(s_networking_server_bap____s____s__01689543);
              thunk_FUN_012aa7e6(&DAT_0282d6c0);
            }
          }
          uVar7 = 0;
          FUN_01008290(local_178,s_networking_server_bap____s____s__01689543,param_1 + 0x1148,
                       (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)],
                       *(undefined4 *)(param_1 + 0x1838));
          FUN_000e4aa0(DAT_0282d6b8,local_178);
          local_17c = 0x13;
          *(undefined8 *)(param_1 + 0x1840) = 0;
          uVar6 = 0;
        }
        else {
          *(undefined4 *)(param_1 + 0x16c8) = 6;
        }
      }
      goto LAB_00b2fd6a;
    }
  }
  else {
    local_17c = 0x2b;
    uVar7 = 0;
  }
  uVar6 = uVar7;
  uVar7 = 1;
LAB_00b2fd6a:
  *param_3 = local_17c;
  *param_2 = uVar7;
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar6);
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

