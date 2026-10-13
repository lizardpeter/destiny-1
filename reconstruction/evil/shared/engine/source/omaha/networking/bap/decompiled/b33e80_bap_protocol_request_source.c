
ulong FUN_00b33e80(long param_1,undefined8 param_2,ushort *param_3,undefined4 *param_4)

{
  char cVar1;
  ushort uVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  long lVar6;
  long *plVar7;
  long *plVar8;
  ulong uVar9;
  undefined4 local_a80;
  int local_a7c;
  undefined1 local_a78 [64];
  undefined1 local_a38 [2048];
  undefined1 local_238 [64];
  undefined1 local_1f8 [64];
  undefined1 local_1b8 [64];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar6 = -1;
  if (*(int *)(param_1 + 0x20) != 0) {
    lVar6 = (long)*(int *)(param_1 + 0x1c);
  }
  uVar3 = *(int *)(param_1 + 0x24 + lVar6 * 0x18) - 1;
  iVar5 = 0;
  if (uVar3 < 5) {
    iVar5 = *(int *)(&DAT_015e0a80 + (long)(int)uVar3 * 4);
  }
  plVar7 = (long *)FUN_0055af60(iVar5);
  uVar4 = (**(code **)(*plVar7 + 8))(plVar7);
  plVar8 = (long *)FUN_0055d370(uVar4);
  uVar9 = (**(code **)*plVar8)(plVar8);
  if ((uVar9 & 0x10) == 0) {
LAB_00b33f35:
    if (iVar5 == 0x1a) {
      local_a7c = 0;
      cVar1 = (**(code **)(*plVar7 + 0x18))
                        (plVar7,*(undefined8 *)(param_4 + 2),*param_4,100,&local_a7c,
                         param_1 + 0x103d);
      if (cVar1 == '\0') {
        if (DAT_0282da10 == '\0') {
          iVar5 = thunk_FUN_012aa7d6(&DAT_0282da10);
          if (iVar5 != 0) {
            DAT_0282da08 = FUN_000e4a10(s_networking_server_bap_protocol_s_0168a7c6);
            thunk_FUN_012aa7e6(&DAT_0282da10);
          }
        }
        local_238[0] = 0;
        if (*param_3 < 0x130) {
          FUN_0100a3d0(local_238,&DAT_0160ec9c);
        }
        else {
          FUN_00065030(local_238,s_enum_out_of_range_01639778,0x40);
        }
        FUN_01008290(local_178,s_networking_server_bap_protocol_s_0168a7c6,local_238);
        uVar4 = DAT_0282da08;
        goto LAB_00b34224;
      }
      *(long *)(param_1 + 0x1099) = (long)local_a7c;
      *(undefined1 *)(param_1 + 0x103c) = 1;
    }
    else {
      local_a80 = 0;
      cVar1 = (**(code **)(*plVar7 + 0x18))
                        (plVar7,*(undefined8 *)(param_4 + 2),*param_4,0x800,&local_a80,local_a38);
      if (cVar1 == '\0') {
        if (DAT_0282da20 == '\0') {
          iVar5 = thunk_FUN_012aa7d6(&DAT_0282da20);
          if (iVar5 != 0) {
            DAT_0282da18 = FUN_000e4a10(s_networking_server_bap_protocol_s_0168a820);
            thunk_FUN_012aa7e6(&DAT_0282da20);
          }
        }
        local_a78[0] = 0;
        if (*param_3 < 0x130) {
          FUN_0100a3d0(local_a78,&DAT_0160ec9c);
        }
        else {
          FUN_00065030(local_a78,s_enum_out_of_range_01639778,0x40);
        }
        FUN_01008290(local_178,s_networking_server_bap_protocol_s_0168a820,local_a78);
        uVar4 = DAT_0282da18;
        goto LAB_00b34224;
      }
    }
    *(undefined4 *)(param_1 + 0x38 + lVar6 * 0x18) = 2;
    uVar9 = CONCAT71((int7)((ulong)(lVar6 * 3) >> 8),1);
  }
  else {
    uVar2 = (**(code **)(*plVar8 + 0x78))(plVar8,param_3);
    if (uVar2 == 200) goto LAB_00b33f35;
    if (DAT_0282da00 == '\0') {
      iVar5 = thunk_FUN_012aa7d6(&DAT_0282da00);
      if (iVar5 != 0) {
        DAT_0282d9f8 = FUN_000e4a10(s_networking_server_bap_protocol_s_0168a770);
        thunk_FUN_012aa7e6(&DAT_0282da00);
      }
    }
    local_1b8[0] = 0;
    if (*param_3 < 0x130) {
      FUN_0100a3d0(local_1b8,&DAT_0160ec9c);
    }
    else {
      FUN_00065030(local_1b8,s_enum_out_of_range_01639778,0x40);
    }
    local_1f8[0] = 0;
    if (uVar2 < 0x20a) {
      FUN_0100a3d0(local_1f8,&DAT_0160ec9c,uVar2);
    }
    else {
      FUN_00065030(local_1f8,s_enum_out_of_range_01639778,0x40);
    }
    FUN_01008290(local_178,s_networking_server_bap_protocol_s_0168a770,local_1b8,local_1f8);
    uVar4 = DAT_0282d9f8;
LAB_00b34224:
    FUN_000e4aa0(uVar4,local_178);
    uVar9 = (**(code **)**(undefined8 **)(param_1 + 0x10))
                      (*(undefined8 **)(param_1 + 0x10),0,*(undefined4 *)(param_1 + 8),4);
    uVar9 = uVar9 & 0xffffffffffffff00;
  }
  if (*DAT_01a1f100 == local_38) {
    return uVar9;
  }
  uVar9 = thunk_FUN_012aa7f6();
  return uVar9;
}

