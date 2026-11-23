
void FUN_0102d440(undefined4 *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  undefined4 uVar1;
  undefined1 auVar2 [64];
  undefined1 extraout_var [56];
  
  auVar2._0_8_ = FUN_00072d90(DAT_01627150,DAT_01627154,param_4,s__ai_policy_vector3d_016271b3 + 1,
                              0x10,0x13);
  auVar2._8_56_ = extraout_var;
  *param_1 = (int)auVar2._0_8_;
  uVar1 = vextractps_avx(auVar2._0_16_,1);
  param_1[1] = uVar1;
  uVar1 = vextractps_avx(auVar2._0_16_,2);
  param_1[2] = uVar1;
  return;
}

