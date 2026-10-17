
void FUN_007d82f0(long param_1)

{
  char cVar1;
  code *local_a0;
  code *pcStack_98;
  code *pcStack_90;
  undefined8 uStack_88;
  code *local_80;
  undefined8 uStack_78;
  undefined8 uStack_70;
  undefined8 uStack_68;
  undefined8 local_60;
  undefined8 local_58;
  undefined8 local_50;
  long local_40;
  
  local_40 = *DAT_01a1f100;
  cVar1 = FUN_007e9a10();
  if ((cVar1 != '\0') && (*(char *)(param_1 + 8) != '\0')) {
    FUN_00070530(&DAT_026df1d0,s_object_effect_instances_0165fd70,DAT_01947f00,0x10,4,0xffffffff,
                 0x80,8,0,0xe,0);
    uStack_78 = 0;
    uStack_70 = 0;
    uStack_68 = 0;
    uStack_88 = 0;
    local_50 = 0;
    local_58 = 0;
    local_60 = 0;
    local_a0 = FUN_007d8410;
    pcStack_98 = FUN_007d8820;
    pcStack_90 = FUN_007d8820;
    local_80 = FUN_007d8820;
    FUN_002fb9c0(1,&local_a0);
  }
  if (*DAT_01a1f100 == local_40) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

