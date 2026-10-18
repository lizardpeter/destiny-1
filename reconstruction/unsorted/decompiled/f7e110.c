
void FUN_00f7e110(uint *param_1,uint param_2)

{
  uint uVar1;
  long *plVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint local_58;
  uint local_54;
  uint local_50;
  uint local_4c;
  uint local_48;
  uint local_44;
  undefined4 local_40;
  uint local_3c;
  long local_38;
  
  plVar2 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  FUN_00f872d0(&local_3c);
  uVar1 = *param_1;
  *param_1 = (local_3c & 7) << 0xd | uVar1 & 0xff8f1fff | (param_2 & 7) << 0x14;
  local_40 = FUN_00f7d5a0(uVar1 & 3);
  uVar3 = FUN_00f7d710(&local_40);
  uVar1 = *param_1;
  FUN_00f87270(&local_44,param_2);
  FUN_00f872a0(&local_48,param_2);
  uVar4 = 0;
  uVar5 = (local_48 & 0x1f) << 8 | (local_44 & 0xf) << 4 | param_1[0xb] & 0xffffe000 | 1;
  param_1[0xb] = uVar5;
  local_4c = 0;
  local_50 = 0;
  local_54 = 0;
  local_58 = 0;
  uVar6 = 0;
  uVar7 = 0;
  uVar8 = 0;
  if ((local_44 & 0xfffffffd) == 4) {
    FUN_00f87370(param_2,uVar3,1 << ((byte)uVar1 >> 2 & 3),&local_4c,&local_50,&local_54,&local_58);
    uVar5 = param_1[0xb];
    uVar4 = (local_58 & 3) << 0x13;
    uVar6 = (local_54 & 3) << 0x11;
    uVar7 = (local_50 & 3) << 0xf;
    uVar8 = (local_4c & 3) << 0xd;
  }
  param_1[0xb] = uVar5 & 0xffe01fff | uVar8 | uVar7 | uVar6 | uVar4;
  if (*plVar2 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

