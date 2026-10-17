
void FUN_00baaa50(undefined1 *param_1)

{
  undefined4 uVar1;
  char cVar2;
  uint uVar3;
  int iVar4;
  undefined8 uVar5;
  long *plVar6;
  undefined8 uVar7;
  ulong uVar8;
  undefined8 local_220;
  undefined8 uStack_218;
  undefined8 uStack_210;
  undefined8 uStack_208;
  undefined8 local_200;
  undefined8 uStack_1f8;
  undefined8 uStack_1f0;
  undefined8 uStack_1e8;
  undefined8 local_1e0;
  undefined8 uStack_1d8;
  undefined8 uStack_1d0;
  undefined8 uStack_1c8;
  undefined8 local_1c0;
  undefined8 uStack_1b8;
  undefined8 uStack_1b0;
  undefined8 uStack_1a8;
  undefined8 local_1a0;
  undefined8 uStack_198;
  undefined8 uStack_190;
  undefined8 uStack_188;
  undefined8 local_180;
  undefined8 uStack_178;
  undefined8 uStack_170;
  undefined8 uStack_168;
  undefined8 local_160;
  undefined8 uStack_158;
  undefined8 uStack_150;
  undefined8 uStack_148;
  undefined1 local_138 [20];
  undefined4 local_124;
  long local_60;
  
  local_60 = *DAT_01a1f100;
  local_160 = 0;
  uStack_158 = 0;
  uStack_150 = 0;
  uStack_148 = 0;
  local_180 = 0;
  uStack_178 = 0;
  uStack_170 = 0;
  uStack_168 = 0;
  local_1a0 = 0;
  uStack_198 = 0;
  uStack_190 = 0;
  uStack_188 = 0;
  local_1c0 = 0;
  uStack_1b8 = 0;
  uStack_1b0 = 0;
  uStack_1a8 = 0;
  local_1e0 = 0;
  uStack_1d8 = 0;
  uStack_1d0 = 0;
  uStack_1c8 = 0;
  local_200 = 0;
  uStack_1f8 = 0;
  uStack_1f0 = 0;
  uStack_1e8 = 0;
  local_220 = 0;
  uStack_218 = 0;
  uStack_210 = 0;
  uStack_208 = 0;
  uVar1 = *(undefined4 *)(param_1 + 4);
  uVar7 = *(undefined8 *)(param_1 + 8);
  uVar5 = FUN_00b9f3d0();
  local_124 = 1;
  FUN_00072240(local_138,uVar7,uVar1);
  FUN_00072400(local_138);
  uVar3 = FUN_00072c70(local_138,2);
  local_220._0_4_ = uVar3;
  FUN_00ba82a0(local_138,(long)&local_220 + 4);
  if ((3 < (uint)local_220) || (local_220._4_4_ == -1)) goto LAB_00baac7f;
  cVar2 = FUN_00072210(local_138);
  if (cVar2 != '\0') goto LAB_00baac7f;
  plVar6 = (long *)FUN_00bb2bf0(uVar5,(uint)local_220);
  FUN_000730b0(local_138,&uStack_218,0x280);
  cVar2 = FUN_00073430(local_138);
  if (cVar2 == '\0') {
    uStack_1c8 = CONCAT44(uStack_1c8._4_4_,0xffffffff);
  }
  else {
    FUN_00ba82a0(local_138,&uStack_1c8);
  }
  iVar4 = (**(code **)(*plVar6 + 0x10))(plVar6);
  uStack_148 = CONCAT44(iVar4,(undefined4)uStack_148);
  if (0 < iVar4) {
    (**(code **)(*plVar6 + 0x60))(plVar6,(long)&uStack_1c8 + 4,local_138);
  }
  cVar2 = FUN_00072210(local_138);
  FUN_00072650(local_138);
  if ((cVar2 != '\0') || (local_220._4_4_ == -1)) goto LAB_00baac7f;
  uVar7 = FUN_00b9f3d0();
  plVar6 = (long *)FUN_00bb2bf0(uVar7,(uint)local_220);
  cVar2 = FUN_00906f70();
  if (cVar2 != '\0') {
    iVar4 = FUN_00ba7ca0(local_220._4_4_,(uint)local_220);
    if ((iVar4 != local_220._4_4_) || (iVar4 == -1)) goto LAB_00baac7f;
  }
  cVar2 = FUN_00ba7fe0();
  if (cVar2 == '\0') {
    *param_1 = 3;
    goto LAB_00baac7f;
  }
  cVar2 = FUN_00906f70();
  if (cVar2 == '\0') {
    uVar7 = thunk_FUN_00aeacd0();
    FUN_00bb63f0(uVar7);
    FUN_00ba8150(local_220._4_4_);
  }
  uVar8 = 0xffffffff;
  if ((int)uStack_1c8 == -1) {
LAB_00baac56:
    cVar2 = (**(code **)(*plVar6 + 0xa8))(plVar6,(long)&uStack_1c8 + 4,local_220._4_4_,uVar8);
    if (cVar2 != '\0') goto LAB_00baac7f;
  }
  else {
    iVar4 = FUN_00ba7f80();
    if (iVar4 != -1) {
      uVar8 = uStack_1c8 & 0xffffffff;
      goto LAB_00baac56;
    }
  }
  FUN_00baacb0(&uStack_218);
LAB_00baac7f:
  if (*DAT_01a1f100 == local_60) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

