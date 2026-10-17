
undefined8 FUN_00bb4690(undefined1 *param_1)

{
  long *plVar1;
  long lVar2;
  undefined8 uVar3;
  undefined1 uVar4;
  undefined1 local_30 [8];
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  lVar2 = thunk_FUN_00aeacd0();
  FUN_002c7e10(local_30,*(undefined4 *)(lVar2 + 0x5b180));
  uVar4 = 1;
  if ((param_1[1] & 1) == 0) {
    switch(*param_1) {
    case 1:
      FUN_00bac5e0(param_1);
      break;
    case 2:
      FUN_00baaa50(param_1);
      break;
    case 3:
      break;
    case 4:
      FUN_00bab380(param_1);
      break;
    case 5:
      FUN_00bab970(param_1);
      break;
    default:
      uVar4 = 0;
      break;
    case 9:
      FUN_00bacc00(param_1);
      break;
    case 10:
      FUN_00bacd20(param_1);
      break;
    case 0xb:
      FUN_00bad000(param_1);
      break;
    case 0xc:
      FUN_00bad260(param_1);
      break;
    case 0xe:
      FUN_00bad430(param_1);
      break;
    case 0xf:
      FUN_00bad520(param_1);
      break;
    case 0x10:
      FUN_00bad870(param_1);
      break;
    case 0x11:
      FUN_00badce0(param_1);
      break;
    case 0x12:
      FUN_00bae0f0(param_1);
      break;
    case 0x13:
      FUN_00bb1d00(param_1);
      break;
    case 0x14:
      FUN_00bb1ea0(param_1);
      break;
    case 0x26:
      FUN_00bae330(param_1);
      break;
    case 0x27:
      FUN_00bae3e0(param_1);
      break;
    case 0x33:
      FUN_00baf610(param_1);
      break;
    case 0x34:
      FUN_00baf920(param_1);
      break;
    case 0x36:
      FUN_00baff10(param_1);
      break;
    case 0x3b:
      FUN_00bb0100(param_1);
      break;
    case 0x3c:
      FUN_00bb06e0(param_1);
      break;
    case 0x3d:
      FUN_00bb0ee0(param_1);
      break;
    case 0x3e:
      FUN_00bb11b0(param_1);
      break;
    case 0x3f:
      FUN_00bb1440(param_1);
      break;
    case 0x41:
      FUN_00bb1440(param_1);
      break;
    case 0x42:
      FUN_00bae5a0(param_1);
      break;
    case 0x43:
      FUN_00bae880(param_1);
      break;
    case 0x44:
      FUN_00baf2e0(param_1);
      break;
    case 0x4c:
      FUN_00baf560(param_1);
      break;
    case 0x4d:
      FUN_00bb19e0(param_1);
      break;
    case 0x4e:
      FUN_00bb1b70(param_1);
    }
  }
  FUN_002c7e20(local_30);
  if (*plVar1 == local_28) {
    return CONCAT71((int7)((ulong)*plVar1 >> 8),uVar4);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

