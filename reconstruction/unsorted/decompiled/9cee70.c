
void FUN_009cee70(long param_1)

{
  long *plVar1;
  char cVar2;
  undefined4 uVar3;
  long lVar4;
  undefined4 local_28 [2];
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  FUN_009438f0();
  uVar3 = FUN_00788e30();
  switch(uVar3) {
  case 4:
    *(undefined1 *)(param_1 + 0x98) = 1;
    break;
  case 5:
    *(undefined1 *)(param_1 + 0x98) = 2;
    break;
  case 6:
    *(undefined1 *)(param_1 + 0x98) = 3;
    break;
  default:
    *(undefined1 *)(param_1 + 0x98) = 0;
    break;
  case 8:
  case 9:
    *(undefined1 *)(param_1 + 0x98) = 4;
    break;
  case 10:
    *(undefined1 *)(param_1 + 0x98) = 5;
    break;
  case 0xb:
    *(undefined1 *)(param_1 + 0x98) = 6;
    break;
  case 0xc:
    *(undefined1 *)(param_1 + 0x98) = 7;
  }
  local_28[0] = DAT_02766f18;
  lVar4 = FUN_00977c40(*(undefined8 *)(param_1 + 0x28),local_28);
  if ((lVar4 != 0) &&
     (cVar2 = FUN_00978170(*(undefined8 *)(lVar4 + 0x10),DAT_027591a0), cVar2 != '\0')) {
    FUN_0098d150(lVar4,0);
  }
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

