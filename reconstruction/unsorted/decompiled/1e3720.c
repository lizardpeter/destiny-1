
void FUN_001e3720(int *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  bool bVar6;
  undefined1 local_88 [40];
  undefined1 local_60 [40];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (*param_1 == 2) {
    iVar1 = FUN_000b9710(param_1[1],local_88);
    if (iVar1 != -1) {
      bVar6 = true;
      do {
        iVar2 = FUN_000b7bc0(iVar1);
        iVar3 = FUN_000b83e0(iVar1);
        iVar4 = FUN_000b80c0(iVar1);
        if (iVar2 == 0) {
          if (iVar4 == 3) {
LAB_001e3800:
            FUN_000b9620(iVar1);
          }
          else if (iVar4 == 1) {
            if (iVar3 == 1) {
              *(undefined1 *)(param_1 + 4) = 1;
            }
            else {
              if (iVar3 == 2) goto LAB_001e3800;
              if (iVar3 == 3) {
                FUN_000b92d0(iVar1);
                bVar6 = false;
              }
            }
          }
        }
        else {
          bVar6 = false;
        }
        iVar1 = FUN_000b9880(local_88);
      } while (iVar1 != -1);
      if ((!bVar6) && ((char)param_1[4] == '\0')) goto switchD_001e378c_default;
    }
    *param_1 = 0;
  }
  else if (*param_1 == 1) {
    switch(param_1[1]) {
    case 0:
      FUN_001e3ad0(param_1);
      break;
    case 1:
      if (param_1[2] != -1) {
        do {
          puVar5 = (undefined4 *)FUN_002b05e0();
          iVar1 = FUN_000b9a00(*puVar5);
          if (iVar1 == -1) {
            iVar1 = FUN_000b9430(1,*puVar5,2);
          }
          else {
            FUN_000b8000(iVar1,0);
          }
          FUN_000b7c60(iVar1,puVar5,0x100);
          iVar1 = param_1[2];
          param_1[2] = iVar1 + -1;
        } while (iVar1 != 0);
      }
      *param_1 = 2;
      break;
    case 2:
      FUN_001e3bf0(param_1);
      break;
    case 3:
      iVar1 = FUN_000b9a00(0xa0000001);
      if (iVar1 != -1) {
        FUN_000b8000(iVar1,0);
        FUN_000b7c60(iVar1,0xa0000001,0);
      }
      *param_1 = 2;
      break;
    case 4:
      iVar1 = FUN_000b9710(4,local_60);
      if (iVar1 != -1) {
        do {
          FUN_000b8000(iVar1,0);
          iVar1 = FUN_000b9880(local_60);
        } while (iVar1 != -1);
      }
      *param_1 = 2;
    }
  }
switchD_001e378c_default:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

