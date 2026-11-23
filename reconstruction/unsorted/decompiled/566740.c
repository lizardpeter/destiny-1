
void FUN_00566740(long param_1,undefined4 param_2,undefined8 param_3,int param_4)

{
  long lVar1;
  undefined8 uVar2;
  int iVar3;
  undefined1 local_7628 [12];
  int local_761c;
  undefined1 local_7618 [12];
  int local_760c;
  undefined1 local_7608 [30160];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar1 = (long)*(int *)(param_1 + 0x40) * 0x20;
  *(undefined8 *)(param_1 + 0x60 + lVar1) = *(undefined8 *)(param_1 + 0x38);
  *(undefined8 *)(param_1 + 0x58 + lVar1) = *(undefined8 *)(param_1 + 0x30);
  uVar2 = *(undefined8 *)(param_1 + 0x20);
  *(undefined8 *)(param_1 + 0x50 + lVar1) = *(undefined8 *)(param_1 + 0x28);
  *(undefined8 *)(param_1 + 0x48 + lVar1) = uVar2;
  *(int *)(param_1 + 0x40) = *(int *)(param_1 + 0x40) + 1;
  if (param_4 < 1) {
    FUN_00072350(param_1,1);
  }
  else {
    iVar3 = param_4;
    do {
      FUN_000730b0(param_1,local_7618,0x80);
      if (local_760c == 0) {
        uVar2 = FUN_0056b260();
        FUN_0056cda0(uVar2,param_2,param_3,local_7618);
      }
      else {
        FUN_000732b0(param_1,local_760c << 3);
      }
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
    FUN_00072350(param_1,1);
    if (0 < param_4) {
      do {
        FUN_000730b0(param_1,local_7628,0x80);
        if (local_761c != 0) {
          FUN_000730b0(param_1,local_7608,local_761c << 3);
          uVar2 = FUN_0056b260();
          FUN_0056c780(uVar2,param_2,param_3,local_7628,local_7608);
        }
        param_4 = param_4 + -1;
      } while (param_4 != 0);
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

