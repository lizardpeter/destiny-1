
void FUN_0102c980(undefined1 (*param_1) [16],undefined8 param_2,undefined8 param_3,
                 undefined8 param_4)

{
  long *plVar1;
  char cVar2;
  uint uVar3;
  uint uVar4;
  undefined1 auVar5 [16];
  uint local_58;
  uint local_54;
  uint local_50;
  uint local_4c;
  uint local_3c;
  uint local_38;
  uint local_34;
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  cVar2 = FUN_00073430(param_4);
  if (cVar2 == '\0') {
    cVar2 = FUN_00073430(param_4);
    if (cVar2 == '\0') {
      FUN_002ca900(param_4,&local_58);
      local_4c = FUN_00072c70(param_4,0x20);
      auVar5 = vinsertps_avx(ZEXT416(local_58),ZEXT416(local_54),0x10);
      auVar5 = vinsertps_avx(auVar5,ZEXT416(local_50),0x20);
      auVar5 = vinsertps_avx(auVar5,ZEXT416(local_4c),0x30);
    }
    else {
      uVar3 = FUN_00072c70(param_4,0x20);
      uVar4 = FUN_00072c70(param_4,0x20);
      auVar5 = vunpcklps_avx(ZEXT416(uVar3),ZEXT416(uVar4));
      uVar3 = FUN_00072c70(param_4,0x20);
      auVar5 = vmovlhps_avx(auVar5,ZEXT416(uVar3));
    }
  }
  else {
    FUN_002ca900(param_4,&local_3c);
    auVar5 = vinsertps_avx(ZEXT416(local_3c),ZEXT416(local_38),0x10);
    auVar5 = vinsertps_avx(auVar5,ZEXT416(local_34),0x20);
    auVar5 = vinsertps_avx(auVar5,ZEXT416(DAT_01627140),0x30);
  }
  *param_1 = auVar5;
  if (*plVar1 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

