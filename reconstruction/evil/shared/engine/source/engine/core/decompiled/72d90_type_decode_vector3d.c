
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
FUN_00072d90(undefined4 param_1,undefined4 param_2,undefined8 param_3,undefined8 param_4,
            undefined4 param_5,undefined4 param_6)

{
  undefined1 auVar1 [16];
  char cVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  undefined1 auVar5 [16];
  undefined8 extraout_XMM0_Qb;
  undefined1 auVar6 [64];
  undefined4 local_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined1 extraout_var [56];
  
  cVar2 = FUN_00073430();
  uVar4 = 0;
  if (cVar2 == '\0') {
    uVar3 = FUN_00072c70(param_3,param_6);
    uVar4 = FUN_00094fe0(uVar3,param_6);
    uVar3 = FUN_00072c70(param_3,param_5);
    auVar6._0_8_ = FUN_00091a80(param_1,param_2,uVar3,1 << ((byte)param_5 & 0x1f));
    auVar6._8_56_ = extraout_var;
    auVar1 = vpshufd_avx(auVar6._0_16_,0);
    local_38 = (float)uVar4;
    uStack_34 = (float)((ulong)uVar4 >> 0x20);
    uStack_30 = (float)extraout_XMM0_Qb;
    uStack_2c = (float)((ulong)extraout_XMM0_Qb >> 0x20);
    auVar5._0_4_ = local_38 * auVar1._0_4_;
    auVar5._4_4_ = uStack_34 * auVar1._4_4_;
    auVar5._8_4_ = uStack_30 * auVar1._8_4_;
    auVar5._12_4_ = uStack_2c * auVar1._12_4_;
    auVar1 = vandps_avx(auVar5,_DAT_0160fbf0);
    uVar4 = auVar1._0_8_;
  }
  return uVar4;
}

