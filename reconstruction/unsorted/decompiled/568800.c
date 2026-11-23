
undefined8
FUN_00568800(undefined4 param_1,undefined4 param_2,undefined8 param_3,undefined8 param_4,
            undefined4 param_5,undefined8 param_6,undefined4 param_7,long param_8,undefined4 param_9
            ,undefined8 *param_10,undefined8 param_11)

{
  long lVar1;
  long lVar2;
  undefined8 *puVar3;
  char cVar4;
  undefined4 uVar5;
  int iVar6;
  long *plVar7;
  long *plVar8;
  ulong uVar9;
  undefined8 uVar10;
  long lVar11;
  uint uVar12;
  undefined1 uVar13;
  undefined4 local_18c;
  undefined1 local_188 [8];
  undefined8 local_180;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  plVar7 = (long *)FUN_00560590(param_2);
  uVar5 = (**(code **)(*plVar7 + 0x30))(plVar7);
  plVar8 = (long *)FUN_0055af60(uVar5);
  FUN_000b54b0(local_188,0x1ff6a,0x18,s_handle_response_internal_0163c431);
  local_18c = 0;
  cVar4 = (**(code **)(*plVar8 + 0x18))(plVar8,param_4,param_5,0x1ff6a,&local_18c,local_180);
  if (cVar4 == '\0') {
    cVar4 = FUN_000e4d70(7,4);
    if (cVar4 != '\0') {
      if (DAT_026bac38 == '\0') {
        iVar6 = thunk_FUN_012aa7d6(&DAT_026bac38);
        if (iVar6 != 0) {
          DAT_026bac30 = FUN_000e4a10(s_networking_investment_bap_messag_0163c44a);
          thunk_FUN_012aa7e6(&DAT_026bac38);
        }
      }
      FUN_01008290(local_178,s_networking_investment_bap_messag_0163c44a,param_11,param_2);
      FUN_000e4aa0(DAT_026bac30,local_178);
    }
    uVar13 = 0;
    if (param_10 != (undefined8 *)0x0) {
      (**(code **)*param_10)(param_10,1,param_9,3);
    }
  }
  else {
    (**(code **)(*plVar7 + 0x58))(plVar7,param_1,local_180,local_18c,param_6,param_7);
    iVar6 = FUN_00071f60(param_8 + 0x50);
    uVar13 = 1;
    if (iVar6 != -1) {
      uVar12 = (int)*(uint *)(param_8 + 0x54) >> 0xd;
      lVar1 = *DAT_01a238a0;
      lVar11 = (ulong)((uVar12 >> 0x12 | 0x3ff) & uVar12) * 0x40;
      lVar2 = *(long *)(lVar1 + 0x10 + lVar11);
      uVar9 = (ulong)((*(uint *)(param_8 + 0x54) & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar11));
      puVar3 = *(undefined8 **)
                ((lVar2 + uVar9) -
                ((long)*(int *)(lVar1 + 0x34 + lVar11) & *(ulong *)(lVar2 + 8 + uVar9)));
      (**(code **)*puVar3)(puVar3,local_180,local_18c);
    }
  }
  FUN_000b54e0(local_188);
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar13);
  }
  uVar10 = thunk_FUN_012aa7f6();
  return uVar10;
}

