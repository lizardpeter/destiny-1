
ulong FUN_00bd8040(undefined4 param_1)

{
  char cVar1;
  ulong uVar2;
  short sVar3;
  int local_c8 [14];
  undefined4 local_90;
  undefined4 local_8c;
  undefined4 local_88;
  undefined8 local_80;
  undefined8 local_78;
  undefined8 local_70;
  undefined8 local_68;
  undefined8 local_60;
  undefined1 local_58;
  undefined8 local_50;
  undefined8 local_48;
  undefined8 local_40;
  undefined8 local_38;
  undefined8 local_30;
  undefined1 local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  FUN_00668780(local_c8);
  local_28 = 0;
  cVar1 = FUN_00bd51e0(param_1,&local_50);
  if (cVar1 == '\0') {
    local_90 = 0xffffffff;
    local_c8[0] = -1;
  }
  else {
    local_80 = local_50;
    local_78 = local_48;
    local_60 = local_30;
    local_68 = local_38;
    local_70 = local_40;
    local_58 = local_28;
    FUN_00668710(local_c8,&local_80);
    if (local_c8[0] != -1) {
      local_88 = FUN_006ed9f0(local_8c);
      sVar3 = -1;
      if (local_c8[0] != -1) {
        do {
          cVar1 = FUN_00bc9af0(local_8c);
          if (cVar1 != '\0') {
            sVar3 = (short)local_c8[0];
            break;
          }
          FUN_006687b0(local_c8);
          if (local_c8[0] == -1) {
            local_88 = 0xffffffff;
            break;
          }
          local_88 = FUN_006ed9f0(local_8c);
        } while (local_c8[0] != -1);
      }
      goto LAB_00bd814b;
    }
  }
  local_88 = 0xffffffff;
  sVar3 = -1;
LAB_00bd814b:
  if (*DAT_01a1f100 != local_20) {
    uVar2 = thunk_FUN_012aa7f6();
    return uVar2;
  }
  return (ulong)(uint)(int)sVar3;
}

