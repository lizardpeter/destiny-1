
void FUN_00923840(int param_1,int param_2,int param_3,int param_4,undefined4 param_5,
                 undefined4 param_6)

{
  undefined1 uVar1;
  undefined4 uVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  
  lVar3 = DAT_0273eb80;
  if (*(int *)(DAT_0273eb80 + 4) == param_3) {
    *(undefined4 *)(DAT_0273eb80 + 4) = param_5;
  }
  else if (*(int *)(DAT_0273eb80 + 4) == param_4) {
    *(undefined4 *)(DAT_0273eb80 + 4) = param_6;
  }
  if (*(int *)(lVar3 + 0xc) == param_3) {
    *(undefined4 *)(lVar3 + 0xc) = param_5;
  }
  else if (*(int *)(lVar3 + 0xc) == param_4) {
    *(undefined4 *)(lVar3 + 0xc) = param_6;
  }
  if (*(int *)(lVar3 + 0x10) == param_3) {
    *(undefined4 *)(lVar3 + 0x10) = param_5;
  }
  else if (*(int *)(lVar3 + 0x10) == param_4) {
    *(undefined4 *)(lVar3 + 0x10) = param_6;
  }
  if (*(int *)(lVar3 + 0x14) == param_3) {
    *(undefined4 *)(lVar3 + 0x14) = param_5;
  }
  else if (*(int *)(lVar3 + 0x14) == param_4) {
    *(undefined4 *)(lVar3 + 0x14) = param_6;
  }
  if (*(int *)(lVar3 + 0x18) == param_3) {
    *(undefined4 *)(lVar3 + 0x18) = param_5;
  }
  else if (*(int *)(lVar3 + 0x18) == param_4) {
    *(undefined4 *)(lVar3 + 0x18) = param_6;
  }
  if (*(int *)(lVar3 + 0xc0) == param_3) {
    *(undefined4 *)(lVar3 + 0xc0) = param_5;
  }
  else if (*(int *)(lVar3 + 0xc0) == param_4) {
    *(undefined4 *)(lVar3 + 0xc0) = param_6;
  }
  lVar5 = (long)param_1;
  uVar2 = *(undefined4 *)(lVar3 + 0x1c + lVar5 * 4);
  lVar4 = (long)param_2;
  *(undefined4 *)(lVar3 + 0x1c + lVar5 * 4) = *(undefined4 *)(lVar3 + 0x1c + lVar4 * 4);
  *(undefined4 *)(lVar3 + 0x1c + lVar4 * 4) = uVar2;
  uVar2 = *(undefined4 *)(lVar3 + 0x6c + lVar5 * 4);
  *(undefined4 *)(lVar3 + 0x6c + lVar5 * 4) = *(undefined4 *)(lVar3 + 0x6c + lVar4 * 4);
  *(undefined4 *)(lVar3 + 0x6c + lVar4 * 4) = uVar2;
  uVar1 = *(undefined1 *)(lVar3 + 200 + lVar5);
  *(undefined1 *)(lVar3 + 200 + lVar5) = *(undefined1 *)(lVar3 + 200 + lVar4);
  *(undefined1 *)(lVar3 + 200 + lVar4) = uVar1;
  return;
}

