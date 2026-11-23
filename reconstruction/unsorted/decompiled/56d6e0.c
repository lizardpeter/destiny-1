
ulong FUN_0056d6e0(long param_1,undefined4 param_2,int param_3,long *param_4)

{
  undefined4 uVar1;
  uint *in_RAX;
  undefined **ppuVar2;
  
  switch(param_2) {
  case 0:
    if (param_3 == 1) {
      *param_4 = param_1 + 0x46e0;
      *(undefined4 *)(param_4 + 1) = 0x14;
      param_4[2] = 0xa48;
      ppuVar2 = &PTR_DAT_0197e308;
    }
    else {
      in_RAX = &switchD_0056d6f9::switchdataD_0056da54;
      if (param_3 != 0) goto switchD_0056d6f9_default;
      *param_4 = param_1 + 0x40a0;
      *(undefined4 *)(param_4 + 1) = 0x14;
      param_4[2] = 0x50;
      ppuVar2 = &PTR_DAT_0197e380;
    }
    break;
  case 1:
    if (param_3 != 3) {
      if (param_3 == 1) {
        *param_4 = param_1 + 0x11c80;
        *(undefined4 *)(param_4 + 1) = 1;
        param_4[2] = (long)&DAT_00001578;
        ppuVar2 = &PTR_DAT_0197e310;
      }
      else {
        in_RAX = &switchD_0056d6f9::switchdataD_0056da54;
        if (param_3 != 0) goto switchD_0056d6f9_default;
        *param_4 = param_1 + 0x11480;
        *(undefined4 *)(param_4 + 1) = 1;
        param_4[2] = 0x800;
        ppuVar2 = &PTR_DAT_0197e388;
      }
      break;
    }
    *param_4 = param_1 + 0x131f8;
    *(undefined4 *)(param_4 + 1) = 0x14;
LAB_0056da17:
    param_4[2] = 0xb8;
    ppuVar2 = &PTR_DAT_0197e3d0;
    break;
  case 2:
    if (param_3 == 1) {
      *param_4 = param_1 + 0x18888;
      *(undefined4 *)(param_4 + 1) = 0xe7;
      param_4[2] = 0x30;
      ppuVar2 = &PTR_DAT_0197e318;
    }
    else {
      in_RAX = &switchD_0056d6f9::switchdataD_0056da54;
      if (param_3 != 0) goto switchD_0056d6f9_default;
      *param_4 = param_1 + 0x14058;
      *(undefined4 *)(param_4 + 1) = 0xe7;
      param_4[2] = 0x50;
      ppuVar2 = &PTR_DAT_0197e390;
    }
    break;
  case 3:
    if (param_3 == 1) {
      *param_4 = param_1 + 0x1b918;
      *(undefined4 *)(param_4 + 1) = 10;
      param_4[2] = 0xa80;
      ppuVar2 = &PTR_DAT_0197e320;
    }
    else {
      in_RAX = &switchD_0056d6f9::switchdataD_0056da54;
      if (param_3 != 0) goto switchD_0056d6f9_default;
      *param_4 = param_1 + 0x1b878;
      *(undefined4 *)(param_4 + 1) = 1;
      param_4[2] = 0xa0;
      ppuVar2 = &PTR_DAT_0197e3a8;
    }
    break;
  case 4:
    in_RAX = &switchD_0056d6f9::switchdataD_0056da54;
    switch(param_3) {
    case 0:
      *param_4 = param_1 + 0x22218;
      *(undefined4 *)(param_4 + 1) = 1;
      param_4[2] = 0x75c8;
      ppuVar2 = &PTR_DAT_0197e3b0;
      break;
    case 1:
      *param_4 = param_1 + 0x297e0;
      *(undefined4 *)(param_4 + 1) = 1;
      param_4[2] = 0x7378;
      ppuVar2 = &PTR_DAT_0197e328;
      break;
    case 2:
      *param_4 = param_1 + 0x4ea08;
      *(undefined4 *)(param_4 + 1) = 1;
      param_4[2] = 0x48;
      ppuVar2 = &PTR_DAT_0197e340;
      break;
    case 3:
      *param_4 = param_1 + 0x30b58;
      *(undefined4 *)(param_4 + 1) = 0x29a;
      goto LAB_0056da17;
    case 4:
      *param_4 = param_1 + 0x4ea50;
      *(undefined4 *)(param_4 + 1) = 1;
      param_4[2] = 0xf90;
      ppuVar2 = &PTR_DAT_0197e3d8;
      break;
    default:
      goto switchD_0056d6f9_default;
    }
    break;
  case 5:
    in_RAX = &switchD_0056d6f9::switchdataD_0056da54;
    if (param_3 != 5) goto switchD_0056d6f9_default;
    *param_4 = param_1 + 0x4f9e0;
    *(undefined4 *)(param_4 + 1) = 1;
    param_4[2] = 0x3b0;
    ppuVar2 = &PTR_DAT_0197e178;
    break;
  case 6:
    if (param_3 == 1) {
      *param_4 = param_1 + 0x1b3e8;
      *(undefined4 *)(param_4 + 1) = 1;
      param_4[2] = 1000;
      ppuVar2 = &PTR_DAT_0197e330;
    }
    else {
      in_RAX = &switchD_0056d6f9::switchdataD_0056da54;
      if (param_3 != 0) goto switchD_0056d6f9_default;
      *param_4 = param_1 + 0x1b3d8;
      *(undefined4 *)(param_4 + 1) = 1;
      param_4[2] = 0x10;
      ppuVar2 = &PTR_DAT_0197e398;
    }
    break;
  case 7:
    if (param_3 == 1) {
      *param_4 = param_1 + 0x1b7e0;
      *(undefined4 *)(param_4 + 1) = 1;
      param_4[2] = 0x98;
      ppuVar2 = &PTR_DAT_0197e338;
    }
    else {
      in_RAX = &switchD_0056d6f9::switchdataD_0056da54;
      if (param_3 != 0) goto switchD_0056d6f9_default;
      *param_4 = param_1 + 0x1b7d0;
      *(undefined4 *)(param_4 + 1) = 1;
      param_4[2] = 0x10;
      ppuVar2 = &PTR_DAT_0197e3a0;
    }
    break;
  default:
switchD_0056d6f9_default:
    *param_4 = 0;
    *(undefined4 *)(param_4 + 1) = 0;
    param_4[2] = 0;
    *(undefined4 *)(param_4 + 3) = 0xffffffff;
    return (ulong)in_RAX & 0xffffffffffffff00;
  }
  uVar1 = *(undefined4 *)*ppuVar2;
  *(undefined4 *)(param_4 + 3) = uVar1;
  return CONCAT71((uint7)(uint3)((uint)uVar1 >> 8),1);
}

