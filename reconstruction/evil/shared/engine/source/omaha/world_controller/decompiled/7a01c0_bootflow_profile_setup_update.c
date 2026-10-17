
void FUN_007a01c0(long param_1)

{
  long *plVar1;
  char cVar2;
  long lVar3;
  undefined8 local_28;
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  cVar2 = FUN_00788e50();
  if (cVar2 != '\0') {
    switch(*(undefined4 *)(param_1 + 0x38)) {
    case 0:
      FUN_00788e10(0x16);
      FUN_00765fb0(4);
      *(undefined4 *)(param_1 + 0x38) = 1;
      break;
    case 1:
    case 3:
    case 5:
      break;
    case 2:
      FUN_00788e10(0x15);
      FUN_00765fb0(4);
      *(undefined4 *)(param_1 + 0x38) = 3;
      break;
    case 4:
      FUN_00788e10(0x17);
      FUN_00765fb0(4);
      *(undefined4 *)(param_1 + 0x38) = 5;
      break;
    case 6:
      *(undefined4 *)(param_1 + 0x38) = 7;
      break;
    default:
      FUN_00244ee0(&local_28);
      lVar3 = FUN_0057ddd0(local_28);
      *(undefined1 *)(lVar3 + 0x10) = 1;
      FUN_0057e090(local_28);
      FUN_00783ed0(0x16);
    }
  }
  if (*plVar1 != local_20) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

