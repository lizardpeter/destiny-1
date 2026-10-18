
void FUN_0057b160(long param_1,uint *param_2)

{
  ushort uVar1;
  bool bVar2;
  int iVar3;
  undefined4 uVar4;
  long lVar5;
  long lVar6;
  undefined8 uVar7;
  long lVar8;
  undefined8 *puVar9;
  undefined **ppuVar10;
  uint uVar11;
  undefined4 *puVar12;
  uint local_68;
  int local_64;
  undefined4 local_60 [2];
  undefined8 local_58;
  undefined4 local_50;
  undefined4 local_4c;
  undefined8 local_48;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar5 = FUN_0097a9c0();
  puVar12 = (undefined4 *)0x0;
  ppuVar10 = &PTR_DAT_0193f4c0;
  uVar11 = 0;
  do {
    if ((*param_2 >> (uVar11 & 0x1f) & 1) != 0) {
      puVar12 = (undefined4 *)*ppuVar10;
    }
    ppuVar10 = ppuVar10 + 1;
    uVar11 = uVar11 + 1;
  } while (uVar11 != 0x15);
  bVar2 = false;
  local_68 = (uint)CONCAT62((int6)((ulong)ppuVar10 >> 0x10),0xffff);
  local_64 = -1;
  if ((*param_2 & 0x400) != 0) {
    lVar6 = FUN_005753c0(4);
    uVar7 = FUN_00582a40();
    lVar8 = FUN_00580840(uVar7,param_1 + 8);
    if (((lVar8 != 0) && (lVar6 != 0)) && (lVar5 != 0)) {
      iVar3 = FUN_00547bb0(lVar6,*(undefined2 *)(lVar8 + 10));
      if (iVar3 == -1) {
        if (*(short *)(lVar8 + 8) != *(short *)(lVar8 + 10)) {
          iVar3 = FUN_00547bb0(lVar6);
          if (iVar3 != -1) {
            uVar1 = *(ushort *)(lVar8 + 8);
            goto LAB_0057b230;
          }
        }
      }
      else {
        uVar1 = *(ushort *)(lVar8 + 10);
LAB_0057b230:
        local_68 = (uint)uVar1;
        bVar2 = true;
        local_64 = iVar3;
      }
    }
  }
  if ((*param_2 & 0x8000) == 0) {
    if (bVar2) {
      FUN_00979da0(&local_50);
      puVar9 = (undefined8 *)FUN_00545710(local_68);
      if (puVar9 != (undefined8 *)0x0) {
        local_48 = *puVar9;
        local_58 = &DAT_811c9dc5ffffffff;
        local_40[0] = *(undefined4 *)((long)puVar9 + 0xc);
        FUN_00a95930(&local_58,puVar9 + 1,local_40);
        local_50 = (undefined4)local_58;
        local_4c = local_58._4_4_;
      }
      FUN_0097a400(lVar5,local_64,1,&local_50,0);
      goto LAB_0057b2e8;
    }
    if (puVar12 == (undefined4 *)0x0) goto LAB_0057b2e8;
  }
  else {
    puVar12 = &DAT_026bc338;
  }
  uVar7 = FUN_009503d0();
  local_60[0] = *puVar12;
  uVar4 = FUN_00244e40();
  FUN_00950620(uVar7,local_60,uVar4,0);
LAB_0057b2e8:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

