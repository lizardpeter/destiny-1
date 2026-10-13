
undefined8
FUN_00564300(undefined4 param_1,ushort *param_2,undefined4 param_3,undefined8 param_4,
            undefined8 *param_5,undefined4 param_6,undefined8 param_7)

{
  char cVar1;
  int iVar2;
  long *plVar3;
  long *plVar4;
  undefined8 uVar5;
  undefined1 uVar6;
  undefined4 uVar7;
  undefined4 local_20c;
  undefined1 local_208 [8];
  undefined8 local_200;
  undefined1 local_1f8 [64];
  undefined1 local_1b8 [64];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_000b54b0(local_208,0x20000,0x18,s_handle_message_internal_0163b373);
  local_20c = 0;
  plVar3 = (long *)FUN_00565290(*param_2);
  plVar4 = (long *)FUN_0055af60(*param_2);
  cVar1 = (**(code **)(*plVar4 + 0x18))(plVar4,param_4,param_3,0x20000,&local_20c,local_200);
  if (cVar1 == '\0') {
    (**(code **)(*plVar3 + 0x20))(plVar3,param_1,param_2,0);
    if (DAT_026ba948 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_026ba948);
      if (iVar2 != 0) {
        DAT_026ba940 = FUN_000e4a10(s_networking_investment_push___s_F_0163b38b);
        thunk_FUN_012aa7e6(&DAT_026ba948);
      }
    }
    local_1b8[0] = 0;
    if (*param_2 < 0x130) {
      FUN_0100a3d0(local_1b8,&DAT_0160ec9c);
    }
    else {
      FUN_00065030(local_1b8,s_enum_out_of_range_01639778,0x40);
    }
    FUN_01008290(local_178,s_networking_investment_push___s_F_0163b38b,param_7,local_1b8,param_3);
    uVar7 = DAT_026ba940;
  }
  else {
    cVar1 = (**(code **)(*plVar3 + 0x28))(plVar3,param_1,param_2,local_20c,local_200);
    uVar6 = 1;
    if (cVar1 != '\0') goto LAB_0056455b;
    if (DAT_026ba958 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_026ba958);
      if (iVar2 != 0) {
        DAT_026ba950 = FUN_000e4a10(s_networking_investment_push___s_F_0163b3dc);
        thunk_FUN_012aa7e6(&DAT_026ba958);
      }
    }
    local_1f8[0] = 0;
    if (*param_2 < 0x130) {
      FUN_0100a3d0(local_1f8,&DAT_0160ec9c);
    }
    else {
      FUN_00065030(local_1f8,s_enum_out_of_range_01639778,0x40);
    }
    FUN_01008290(local_178,s_networking_investment_push___s_F_0163b3dc,param_7,local_1f8,local_20c);
    uVar7 = DAT_026ba950;
  }
  FUN_000e4aa0(uVar7,local_178);
  uVar6 = 0;
  if (param_5 != (undefined8 *)0x0) {
    (**(code **)*param_5)(param_5,2,param_6,5);
  }
LAB_0056455b:
  FUN_000b54e0(local_208);
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar6);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

