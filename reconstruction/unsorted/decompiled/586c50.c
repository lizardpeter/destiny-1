
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00586c50(undefined8 param_1,undefined8 param_2)

{
  int iVar1;
  long lVar2;
  undefined8 *puVar3;
  undefined8 uVar4;
  float fVar5;
  undefined1 auStack_23980 [24];
  undefined4 uStack_23968;
  undefined1 auStack_23960 [24];
  undefined8 uStack_23948;
  undefined4 auStack_23940 [2];
  undefined8 uStack_23938;
  undefined1 auStack_23930 [145000];
  undefined1 local_2c8 [8];
  undefined8 local_2c0;
  undefined1 local_2b8;
  undefined8 local_2b0;
  undefined1 local_2a8;
  undefined1 local_2a7 [64];
  undefined1 local_267;
  undefined4 local_264;
  undefined1 local_260;
  undefined1 local_25f [512];
  undefined1 local_5f;
  undefined4 local_5c;
  undefined1 local_58 [32];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar1 = FUN_000911d0();
  fVar5 = (float)((iVar1 * 0x19660d + 0x3c6ef35fU >> 0x10) * 1000 >> 0x10) / _DAT_0163ddd0;
  lVar2 = FUN_0034e610();
  if (fVar5 < *(float *)(lVar2 + 0x10)) {
    lVar2 = FUN_000ca690(8);
    if (lVar2 != 0) {
      puVar3 = (undefined8 *)FUN_00068570();
      FUN_00068890(local_58,0x20);
      uVar4 = *puVar3;
      thunk_FUN_012aa986(local_2c8,0,0x270);
      local_2c8[0] = 1;
      local_2b8 = 1;
      local_2c0 = param_2;
      local_2b0 = uVar4;
      thunk_FUN_012aabc6(local_2a7,local_58,0x20);
      local_2a8 = 1;
      uVar4 = FUN_000596f0();
      FUN_00065030(local_25f,uVar4,0x200);
      local_260 = 1;
      local_264 = FUN_00059700();
      local_267 = 1;
      local_5c = 0xd;
      local_5f = 1;
      thunk_FUN_012aa986(auStack_23940,0,0x23678);
      auStack_23940[0] = 3;
      FUN_000a2c20(auStack_23960,auStack_23930,0x23668);
      FUN_000a2c80(auStack_23960,&DAT_015b9570,local_2c8);
      uStack_23938 = uStack_23948;
      FUN_000a2c20(auStack_23980,lVar2,0x800);
      FUN_000a2c80(auStack_23980,&DAT_015b9520,auStack_23940);
      FUN_000ca760(lVar2,uStack_23968);
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

