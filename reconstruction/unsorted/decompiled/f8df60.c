
void FUN_00f8df60(long param_1,undefined8 param_2,undefined8 *param_3)

{
  int iVar1;
  undefined4 uVar2;
  long lVar3;
  bool bVar4;
  bool bVar5;
  char cVar6;
  long lVar7;
  undefined8 *puVar8;
  undefined8 local_130;
  undefined8 local_128;
  undefined8 local_120;
  undefined8 uStack_118;
  undefined8 uStack_110;
  undefined8 uStack_108;
  undefined8 local_100;
  undefined8 uStack_f8;
  undefined8 uStack_f0;
  undefined8 uStack_e8;
  undefined8 local_e0;
  undefined8 uStack_d8;
  undefined8 uStack_d0;
  undefined8 uStack_c8;
  undefined8 local_c0;
  undefined8 uStack_b8;
  undefined8 uStack_b0;
  undefined8 uStack_a8;
  undefined8 local_a0;
  undefined8 local_98;
  long local_90;
  undefined8 local_88;
  undefined8 local_80;
  undefined8 local_78;
  undefined8 local_70;
  undefined8 local_68;
  long local_60;
  
  local_60 = *DAT_01a1f100;
  *(undefined1 *)(param_1 + 0xba8) = 1;
  FUN_01005910(param_3,*(uint *)(param_1 + 0xba0) >> 2);
  bVar4 = false;
  local_80 = param_3[4];
  local_78 = param_3[5];
  local_70 = param_3[6];
  local_68 = param_3[7];
  local_88 = param_3[3];
  local_a0 = *param_3;
  local_98 = param_3[1];
  local_90 = param_3[2] + -8;
  iVar1 = *(int *)(param_1 + 0x2e8);
  if (iVar1 == 0xb0) {
    bVar5 = true;
  }
  else if (iVar1 == 0xad) {
    bVar5 = true;
    bVar4 = true;
  }
  else if (iVar1 == 0x45) {
    bVar5 = false;
    bVar4 = true;
  }
  else {
    bVar5 = false;
    bVar4 = false;
  }
  if (*(char *)(param_1 + 0x2ed) != '\0') {
    lVar7 = *(long *)(param_1 + 0x2b0) + 8;
    if (*(long *)(param_1 + 0x2b0) == 0) {
      lVar7 = 0;
    }
    FUN_00f7f8e0(param_2,lVar7);
  }
  if (((*(long *)(param_1 + 0x2a8) != 0) && (*(char *)(param_1 + 0x2ee) != '\0')) &&
     (FUN_00f7f940(param_2,*(long *)(param_1 + 0x2a8) + 8,*(undefined4 *)(param_1 + 0x298)),
     *(long *)(param_1 + 0x278) != 0)) {
    FUN_00f80210(param_2,2,0);
  }
  if (((*(long *)(param_1 + 0x2c0) != 0) && (bVar4)) &&
     ((*(char *)(param_1 + 0x2f2) != '\0' &&
      (FUN_00f7fb40(param_2,*(long *)(param_1 + 0x2c0) + 8,*(undefined4 *)(param_1 + 0x29c)),
      *(long *)(param_1 + 0x280) != 0)))) {
    FUN_00f80210(param_2,6,0);
  }
  if (((*(long *)(param_1 + 0x2c8) != 0) && (bVar4)) && (*(char *)(param_1 + 0x2f1) != '\0')) {
    FUN_00f7fa20(param_2,*(long *)(param_1 + 0x2c8) + 8,param_1 + 0x310);
  }
  lVar7 = *(long *)(param_1 + 0x2d0);
  if (((lVar7 != 0) && (bVar5)) && (*(char *)(param_1 + 0x2f0) != '\0')) {
    puVar8 = (undefined8 *)(lVar7 + 8);
    if (*(int *)(param_1 + 0x300) == 0) {
      uVar2 = *(undefined4 *)(param_1 + 0x2a0);
    }
    else {
      local_130 = *puVar8;
      local_128 = *(undefined8 *)(lVar7 + 0x10);
      puVar8 = &local_130;
      FUN_00f834c0(puVar8,*(int *)(param_1 + 0x300));
      uVar2 = *(undefined4 *)(param_1 + 0x2a0);
    }
    FUN_00f7f9b0(param_2,puVar8,uVar2);
    if (*(long *)(param_1 + 0x288) != 0) {
      FUN_00f80210(param_2,4,0);
    }
  }
  if (((*(long *)(param_1 + 0x2d8) != 0) && (bVar5)) && (*(char *)(param_1 + 0x2ef) != '\0')) {
    FUN_00f7fc40(param_2,*(long *)(param_1 + 0x2d8) + 8);
  }
  lVar7 = *(long *)(param_1 + 0x2a8);
  if (lVar7 != 0) {
    lVar3 = *(long *)(param_1 + 0x2b0);
    if (((lVar3 != 0) &&
        ((*(char *)(param_1 + 0x2ee) != '\0' || (*(char *)(param_1 + 0x2ed) != '\0')))) &&
       (cVar6 = *(char *)(lVar3 + 0x38), cVar6 != '\0')) {
      puVar8 = *(undefined8 **)(param_1 + 0x308);
      if (puVar8 == (undefined8 *)0x0) {
        puVar8 = &local_120;
        FUN_00f82f30(puVar8,lVar7 + 0x28 +
                            ((ulong)*(byte *)(lVar7 + 3) + (ulong)*(byte *)(lVar7 + 0x24)) * 4,
                     *(undefined1 *)(lVar7 + 0x25),lVar3 + 0x3c + (ulong)*(byte *)(lVar3 + 3) * 4,
                     cVar6);
        cVar6 = *(char *)(*(long *)(param_1 + 0x2b0) + 0x38);
      }
      FUN_00f7f5a0(param_2,puVar8,cVar6);
    }
    lVar7 = *(long *)(param_1 + 0x2a8);
    if (lVar7 != 0) {
      local_c0 = 0;
      uStack_b8 = 0;
      uStack_b0 = 0;
      uStack_a8 = 0;
      local_e0 = 0;
      uStack_d8 = 0;
      uStack_d0 = 0;
      uStack_c8 = 0;
      local_100 = 0;
      uStack_f8 = 0;
      uStack_f0 = 0;
      uStack_e8 = 0;
      local_120 = 0;
      uStack_118 = 0;
      uStack_110 = 0;
      uStack_108 = 0;
      FUN_00f8bff0(param_1,param_3,2,lVar7 + 0x28,*(undefined1 *)(lVar7 + 3),&local_120);
      FUN_00f8d880(param_1,param_2,2,lVar7 + 0x28,*(undefined1 *)(*(long *)(param_1 + 0x2a8) + 3),
                   &local_120);
    }
  }
  lVar7 = *(long *)(param_1 + 0x2b0);
  if (lVar7 != 0) {
    local_c0 = 0;
    uStack_b8 = 0;
    uStack_b0 = 0;
    uStack_a8 = 0;
    local_e0 = 0;
    uStack_d8 = 0;
    uStack_d0 = 0;
    uStack_c8 = 0;
    local_100 = 0;
    uStack_f8 = 0;
    uStack_f0 = 0;
    uStack_e8 = 0;
    local_120 = 0;
    uStack_118 = 0;
    uStack_110 = 0;
    uStack_108 = 0;
    FUN_00f8bff0(param_1,param_3,1,lVar7 + 0x3c,*(undefined1 *)(lVar7 + 3),&local_120);
    FUN_00f8d880(param_1,param_2,1,lVar7 + 0x3c,*(undefined1 *)(*(long *)(param_1 + 0x2b0) + 3),
                 &local_120);
  }
  lVar7 = *(long *)(param_1 + 0x2c0);
  if ((lVar7 != 0) && (bVar4)) {
    local_c0 = 0;
    uStack_b8 = 0;
    uStack_b0 = 0;
    uStack_a8 = 0;
    local_e0 = 0;
    uStack_d8 = 0;
    uStack_d0 = 0;
    uStack_c8 = 0;
    local_100 = 0;
    uStack_f8 = 0;
    uStack_f0 = 0;
    uStack_e8 = 0;
    local_120 = 0;
    uStack_118 = 0;
    uStack_110 = 0;
    uStack_108 = 0;
    FUN_00f8bff0(param_1,param_3,6,lVar7 + 0x20,*(undefined1 *)(lVar7 + 3),&local_120);
    FUN_00f8d880(param_1,param_2,6,lVar7 + 0x20,*(undefined1 *)(*(long *)(param_1 + 0x2c0) + 3),
                 &local_120);
  }
  lVar7 = *(long *)(param_1 + 0x2c8);
  if ((lVar7 != 0) && (bVar4)) {
    local_c0 = 0;
    uStack_b8 = 0;
    uStack_b0 = 0;
    uStack_a8 = 0;
    local_e0 = 0;
    uStack_d8 = 0;
    uStack_d0 = 0;
    uStack_c8 = 0;
    local_100 = 0;
    uStack_f8 = 0;
    uStack_f0 = 0;
    uStack_e8 = 0;
    local_120 = 0;
    uStack_118 = 0;
    uStack_110 = 0;
    uStack_108 = 0;
    FUN_00f8bff0(param_1,param_3,5,lVar7 + 0x40,*(undefined1 *)(lVar7 + 3),&local_120);
    FUN_00f8d880(param_1,param_2,5,lVar7 + 0x40,*(undefined1 *)(*(long *)(param_1 + 0x2c8) + 3),
                 &local_120);
  }
  lVar7 = *(long *)(param_1 + 0x2d0);
  if ((lVar7 != 0) && (bVar5)) {
    local_c0 = 0;
    uStack_b8 = 0;
    uStack_b0 = 0;
    uStack_a8 = 0;
    local_e0 = 0;
    uStack_d8 = 0;
    uStack_d0 = 0;
    uStack_c8 = 0;
    local_100 = 0;
    uStack_f8 = 0;
    uStack_f0 = 0;
    uStack_e8 = 0;
    local_120 = 0;
    uStack_118 = 0;
    uStack_110 = 0;
    uStack_108 = 0;
    FUN_00f8bff0(param_1,param_3,4,lVar7 + 0x20,*(undefined1 *)(lVar7 + 3),&local_120);
    FUN_00f8d880(param_1,param_2,4,lVar7 + 0x20,*(undefined1 *)(*(long *)(param_1 + 0x2d0) + 3),
                 &local_120);
  }
  lVar7 = *(long *)(param_1 + 0x2d8);
  if ((lVar7 != 0) && (bVar5)) {
    local_c0 = 0;
    uStack_b8 = 0;
    uStack_b0 = 0;
    uStack_a8 = 0;
    local_e0 = 0;
    uStack_d8 = 0;
    uStack_d0 = 0;
    uStack_c8 = 0;
    local_100 = 0;
    uStack_f8 = 0;
    uStack_f0 = 0;
    uStack_e8 = 0;
    local_120 = 0;
    uStack_118 = 0;
    uStack_110 = 0;
    uStack_108 = 0;
    FUN_00f8bff0(param_1,param_3,3,lVar7 + 0x38,*(undefined1 *)(lVar7 + 3));
    FUN_00f8d880(param_1,param_2,3,lVar7 + 0x38,*(undefined1 *)(*(long *)(param_1 + 0x2d8) + 3),
                 &local_120);
  }
  *(undefined2 *)(param_1 + 0x2ed) = 0;
  if (bVar4) {
    *(undefined2 *)(param_1 + 0x2f1) = 0;
  }
  if (bVar5) {
    *(undefined2 *)(param_1 + 0x2ef) = 0;
  }
  if (*(char *)(param_1 + 0x3f0) != '\0') {
    FUN_00f7f010(param_2,*(undefined8 *)(param_1 + 0x328),param_1 + 0x330,0x30,0,1);
    FUN_00f80f10(param_2,0,0x8000000,1);
    *(undefined1 *)(param_1 + 0x3f0) = 0;
  }
  FUN_00f80fe0(param_2);
  FUN_010058b0(param_3);
  if (*(char *)(param_1 + 0x2fc) == '\0') {
    FUN_00f81130(&local_a0,2);
  }
  *(undefined1 *)(param_1 + 0x2fc) = 0;
  if (*DAT_01a1f100 != local_60) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

