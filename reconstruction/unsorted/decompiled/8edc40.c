
void FUN_008edc40(long param_1,long param_2)

{
  float fVar1;
  float fVar2;
  long lVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  byte bVar6;
  undefined4 uVar7;
  undefined4 local_c8 [20];
  undefined4 local_78;
  undefined4 local_74;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_68;
  undefined4 local_64;
  undefined4 local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_50;
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined1 local_30;
  long local_28;
  
  bVar6 = 0;
  local_28 = *DAT_01a1f100;
  if (0.0 < *(float *)(param_1 + 0x360)) {
    lVar3 = FUN_00526f80();
    fVar1 = *(float *)(lVar3 + 0xf4);
    fVar2 = fVar1;
    if (*(float *)(param_1 + 0x360) - fVar1 < DAT_0166a788) {
      fVar2 = *(float *)(param_1 + 0x360);
    }
    uVar7 = FUN_00091690(0,fVar1,0,DAT_0166a784,fVar2);
    lVar3 = FUN_00526f80();
    local_70 = *(undefined4 *)(lVar3 + 0x108);
    local_74 = *(undefined4 *)(lVar3 + 0x104);
    local_78 = *(undefined4 *)(lVar3 + 0x100);
    local_60 = *(undefined4 *)(lVar3 + 0xf8);
    local_5c = *(undefined4 *)(lVar3 + 0xfc);
    local_34 = 1;
    local_54 = *(undefined4 *)(param_2 + 0x194);
    local_50 = *(undefined4 *)(param_2 + 0x198);
    local_4c = *(undefined4 *)(param_2 + 0x19c);
    local_48 = *(undefined4 *)(param_2 + 0x1a0);
    local_44 = *(undefined4 *)(param_2 + 0x1a4);
    local_40 = *(undefined4 *)(param_2 + 0x1a8);
    local_3c = *(undefined4 *)(param_2 + 0x1ac);
    local_38 = *(undefined4 *)(param_2 + 0x1b0);
    local_30 = 1;
    local_6c = local_70;
    local_68 = local_78;
    local_64 = local_74;
    local_58 = local_60;
    FUN_00864e20(uVar7,local_c8,(undefined4 *)(param_2 + 0x170),&local_78);
    puVar4 = local_c8;
    puVar5 = (undefined4 *)(param_2 + 0x170);
    for (lVar3 = 0x13; lVar3 != 0; lVar3 = lVar3 + -1) {
      *puVar5 = *puVar4;
      puVar4 = puVar4 + (ulong)bVar6 * -2 + 1;
      puVar5 = puVar5 + (ulong)bVar6 * -2 + 1;
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

