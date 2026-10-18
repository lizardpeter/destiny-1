
void FUN_0056f9d0(long param_1,char param_2)

{
  undefined8 uVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  long lVar6;
  undefined8 in_R9;
  long lVar7;
  long lVar8;
  long local_38 [3];
  
  local_38[2] = *DAT_01a1f100;
  uVar1 = FUN_00557c40(&DAT_026bc508);
  local_38[0] = FUN_005863c0(uVar1);
  lVar2 = FUN_00557c40(&DAT_026bc810);
  if ((lVar2 != 0) && (local_38[1] = 0, local_38[0] != 0)) {
    lVar3 = FUN_00266e70(param_1);
    if (lVar3 != 0) {
      lVar4 = (long)*(short *)(lVar3 + 0x12) - (long)*(short *)(lVar3 + 0x10);
      lVar3 = param_1 + 8 + (long)*(short *)(lVar3 + 0x10) * 0x10;
      if (param_2 == '\0') {
        lVar8 = 0;
        lVar7 = 0;
        lVar5 = lVar4;
        lVar6 = lVar3;
      }
      else {
        lVar5 = 0;
        lVar6 = 0;
        lVar7 = lVar4;
        lVar8 = lVar3;
      }
      FUN_0058cb50(lVar2,local_38,1,lVar5,lVar6,in_R9,lVar7,lVar8);
    }
  }
  if (*DAT_01a1f100 == local_38[2]) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

