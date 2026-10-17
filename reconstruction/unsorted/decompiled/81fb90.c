
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0081fb90(long param_1,long param_2,undefined8 param_3)

{
  undefined4 uVar1;
  long lVar2;
  uint *puVar3;
  undefined1 auVar4 [16];
  undefined1 auVar5 [16];
  undefined1 auVar6 [16];
  undefined8 uVar7;
  undefined8 *puVar8;
  undefined8 uVar9;
  undefined1 auVar10 [16];
  undefined8 local_88;
  undefined8 uStack_80;
  undefined8 local_78;
  undefined8 uStack_70;
  undefined8 uStack_60;
  
  uVar7 = uRam0000000001662e58;
  uVar9 = _DAT_01662e50;
  lVar2 = *DAT_01a1f100;
  uVar1 = *(undefined4 *)(param_2 + 0x120);
  puVar3 = *(uint **)(param_1 + 0x1010);
  auVar4 = vinsertps_avx(ZEXT416(*puVar3),ZEXT416(puVar3[1]),0x10);
  auVar4 = vinsertps_avx(auVar4,ZEXT416(puVar3[5]),0x20);
  auVar4 = vinsertps_avx(auVar4,ZEXT416(puVar3[6]),0x30);
  auVar5 = vinsertps_avx(ZEXT416(puVar3[7]),ZEXT416((uint)((float)puVar3[10] * DAT_01662ea4)),0x10);
  auVar5 = vinsertps_avx(auVar5,ZEXT416(puVar3[7]),0x20);
  auVar5 = vinsertps_avx(auVar5,ZEXT416(puVar3[10]),0x30);
  auVar6 = vpshufd_avx(ZEXT416(puVar3[1]),0);
  auVar10._0_8_ =
       CONCAT44((auVar6._4_4_ + fRam0000000001662e64) * fRam0000000001662e74,
                (auVar6._0_4_ + _DAT_01662e60) * _DAT_01662e70);
  auVar10._8_4_ = (auVar6._8_4_ + fRam0000000001662e68) * fRam0000000001662e78;
  auVar10._12_4_ = (auVar6._12_4_ + fRam0000000001662e6c) * fRam0000000001662e7c;
  puVar8 = (undefined8 *)FUN_007df630(param_3,1,*(undefined4 *)(param_2 + 0x90),0x40);
  uStack_60 = auVar10._8_8_;
  puVar8[7] = uVar7;
  puVar8[6] = uVar9;
  puVar8[5] = uStack_60;
  puVar8[4] = auVar10._0_8_;
  uStack_70 = auVar5._8_8_;
  puVar8[3] = uStack_70;
  local_78 = auVar5._0_8_;
  puVar8[2] = local_78;
  local_88 = auVar4._0_8_;
  uStack_80 = auVar4._8_8_;
  puVar8[1] = uStack_80;
  *puVar8 = local_88;
  puVar8 = (undefined8 *)FUN_007df630(param_3,2,uVar1,0x40);
  puVar8[7] = uVar7;
  puVar8[6] = uVar9;
  puVar8[5] = uStack_60;
  puVar8[4] = auVar10._0_8_;
  puVar8[3] = uStack_70;
  puVar8[2] = local_78;
  puVar8[1] = uStack_80;
  *puVar8 = local_88;
  if (*DAT_01a1f100 == lVar2) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
  }
  uVar9 = thunk_FUN_012aa7f6();
  return uVar9;
}

