
void FUN_007e1960(long param_1,uint param_2,int param_3,undefined8 param_4,int param_5)

{
  long lVar1;
  undefined4 uVar2;
  uint *puVar3;
  long lVar4;
  long lVar5;
  uint uVar6;
  ulong uVar7;
  int iVar8;
  undefined1 local_138 [256];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  puVar3 = *(uint **)(param_1 + 0x1d60);
  if (puVar3 == (uint *)0x0) goto LAB_007e1b01;
  uVar2 = *(undefined4 *)(&DAT_015d13c0 + (ulong)param_2 * 4);
  lVar4 = *(long *)(param_1 + 0x50);
  uVar6 = 0;
  iVar8 = 0;
  switch((ulong)param_2) {
  case 0:
    break;
  case 1:
    param_3 = param_3 * 2;
    break;
  case 2:
    param_3 = param_3 + 1;
    break;
  case 3:
  case 6:
    iVar8 = param_3 * 3;
    goto switchD_007e19d1_default;
  case 4:
  case 5:
    param_3 = param_3 + 2;
    break;
  case 7:
    param_3 = param_3 << 2;
    break;
  default:
    goto switchD_007e19d1_default;
  }
  iVar8 = param_3;
switchD_007e19d1_default:
  lVar1 = lVar4 + 0xc0;
  lVar5 = FUN_00f7feb0(lVar4,iVar8 * param_5,2);
  thunk_FUN_012aa7c6(lVar5,param_4,iVar8 * param_5);
  if (*puVar3 != 0) {
    do {
      uVar7 = (ulong)uVar6;
      FUN_00f7cf90(local_138 + uVar7 * 0x10,(ulong)(byte)puVar3[uVar7 * 2 + 6] + lVar5,
                   puVar3[uVar7 * 2 + 5],param_5,iVar8);
      FUN_00f8b600(lVar1,2,uVar7,1,local_138 + uVar7 * 0x10);
      uVar6 = uVar6 + 1;
    } while (uVar6 < *puVar3);
  }
  FUN_00f7f1e0(lVar4,uVar2);
  FUN_00f8df60(lVar1,lVar4,lVar4 + 0x80);
  FUN_00f7f260(lVar4,iVar8);
  FUN_00f8e880(lVar1,lVar4,lVar4 + 0x80);
  *(undefined4 *)(param_1 + 0x1d78) = 0xffffffff;
  *(undefined4 *)(&DAT_00001df8 + param_1) = 0;
  *(undefined4 *)(param_1 + 0x1d68) = 0xffffffff;
LAB_007e1b01:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

