
void FUN_0102c8d0(undefined1 (*param_1) [16],undefined8 param_2,undefined8 param_3,
                 undefined8 param_4)

{
  undefined1 auVar1 [16];
  long *plVar2;
  uint local_2c;
  uint local_28;
  uint local_24;
  long local_20;
  
  plVar2 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  FUN_002ca900(param_4,&local_2c);
  auVar1 = vinsertps_avx(ZEXT416(local_2c),ZEXT416(local_28),0x10);
  auVar1 = vinsertps_avx(auVar1,ZEXT416(local_24),0x20);
  auVar1 = vinsertps_avx(auVar1,ZEXT416(DAT_01627134),0x30);
  *param_1 = auVar1;
  if (*plVar2 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

