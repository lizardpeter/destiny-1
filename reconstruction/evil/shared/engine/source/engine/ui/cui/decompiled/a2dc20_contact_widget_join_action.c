
undefined8 FUN_00a2dc20(long param_1)

{
  char extraout_AL;
  char extraout_AL_00;
  char cVar1;
  int iVar2;
  undefined7 extraout_var;
  long lVar3;
  undefined7 extraout_var_00;
  undefined8 *puVar4;
  undefined7 uVar6;
  undefined8 uVar5;
  undefined8 local_60;
  undefined4 local_58;
  undefined4 local_54;
  undefined8 local_50;
  undefined4 local_48 [2];
  undefined1 local_40;
  byte local_3f;
  undefined4 local_38 [2];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  if ((*DAT_0265b510 & 2) == 0) {
    FUN_00955ef0(param_1 + 0x18,param_1,&local_40,1);
    if ((local_3f & 4) != 0) {
      local_48[0] = CONCAT22(local_48[0]._2_2_,0xffff);
      iVar2 = FUN_00a2d990(param_1,local_48);
      lVar3 = FUN_0097a9c0();
      if ((iVar2 != -1) && (lVar3 != 0)) {
        FUN_00979da0(&local_58);
        puVar4 = (undefined8 *)FUN_00545710(local_48[0]);
        if (puVar4 != (undefined8 *)0x0) {
          local_50 = *puVar4;
          local_60 = &DAT_811c9dc5ffffffff;
          local_38[0] = *(undefined4 *)((long)puVar4 + 0xc);
          FUN_00a95930(&local_60,puVar4 + 1,local_38);
          local_58 = (undefined4)local_60;
          local_54 = local_60._4_4_;
        }
        uVar5 = FUN_0097a400(lVar3,iVar2,1,&local_58,0);
        uVar6 = (undefined7)((ulong)uVar5 >> 8);
        cVar1 = '\x01';
        goto LAB_00a2dccc;
      }
    }
    uVar5 = FUN_0057a220();
    FUN_00579ea0(uVar5,param_1 + 0x18,1,0,0);
    cVar1 = extraout_AL_00;
    uVar6 = extraout_var_00;
  }
  else {
    FUN_002b1670(DAT_0265b510,s_join_fireteam_01677c6a,param_1,0x70,thunk_FUN_00a2dc20);
    cVar1 = extraout_AL;
    uVar6 = extraout_var;
  }
LAB_00a2dccc:
  if (*DAT_01a1f100 == local_30) {
    return CONCAT71(uVar6,cVar1 != '\0');
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

