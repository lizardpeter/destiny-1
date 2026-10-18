
void FUN_007536f0(undefined4 *param_1,ushort *param_2)

{
  ushort uVar1;
  uint uVar2;
  byte bVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  param_2[0] = 0;
  param_2[1] = 0;
  param_2[2] = 0;
  param_2[3] = 0;
  uVar1 = 0;
  iVar4 = 0;
  uVar5 = 0;
  uVar6 = 0;
  uVar7 = 0;
  do {
    bVar3 = (byte)iVar4;
    switch(*param_1) {
    case 0:
      uVar2 = 1 << (bVar3 & 0x1f);
      *param_2 = (ushort)uVar2 | (ushort)uVar7;
      uVar7 = uVar2 & 0xffff | uVar7;
      break;
    case 1:
    case 3:
      uVar2 = 1 << (bVar3 & 0x1f);
      param_2[2] = (ushort)uVar2 | (ushort)uVar5;
      uVar5 = uVar2 & 0xffff | uVar5;
      break;
    case 2:
      uVar2 = 1 << (bVar3 & 0x1f);
      param_2[1] = (ushort)uVar2 | (ushort)uVar6;
      uVar6 = uVar2 & 0xffff | uVar6;
      break;
    case 4:
    case 5:
      uVar1 = (ushort)(1 << (bVar3 & 0x1f)) | uVar1;
      param_2[3] = uVar1;
    }
    param_1 = param_1 + 3;
    iVar4 = iVar4 + 1;
  } while (iVar4 != 8);
  return;
}

